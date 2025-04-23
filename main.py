import sys
import os
import time
import pandas as pd
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QLabel, QLineEdit, QFileDialog, QProgressBar, QGroupBox, QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIntValidator, QAction, QIcon
from PIL import Image
import subprocess

class ImageProcessor(QThread):
    progress_updated = pyqtSignal(int, str, dict)
    processing_complete = pyqtSignal(dict)
    scan_progress = pyqtSignal(int)

    def __init__(self, source_folder, num_designers):
        super().__init__()
        self.source_folder = source_folder
        self.num_designers = num_designers
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'}
        self.stats = {
            'total_images': 0,
            'white_background': 0,
            'non_white_background': 0,
            'extensions': {},
            'designer_files': {}
        }

    def run(self):
        try:
            start_time = time.time()
            
            # Create designer folders
            for i in range(self.num_designers):
                folder_path = os.path.join(self.source_folder, f'Designer_{i+1}')
                os.makedirs(folder_path, exist_ok=True)
                self.stats['designer_files'][f'Designer_{i+1}'] = []

            # First scan to count files and group by file ID
            image_groups = {}  # Dictionary to store groups of images by file ID
            image_files = []
            for root, _, files in os.walk(self.source_folder):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in self.supported_formats:
                        # Extract file ID from filename
                        file_id = self.extract_file_id(file)
                        if file_id:
                            if file_id not in image_groups:
                                image_groups[file_id] = []
                            image_groups[file_id].append(os.path.join(root, file))
                            image_files.append(os.path.join(root, file))
                            self.stats['extensions'][ext] = self.stats['extensions'].get(ext, 0) + 1
                            self.scan_progress.emit(len(image_files))

            self.stats['total_images'] = len(image_files)
            processed = 0

            # Sort groups by ID to ensure consistent distribution
            sorted_groups = sorted(image_groups.items())
            total_groups = len(sorted_groups)
            
            # Calculate how many groups each designer should get
            groups_per_designer = total_groups // self.num_designers
            extra_groups = total_groups % self.num_designers

            # Distribute groups to designers
            current_designer = 0
            for i, (file_id, group_files) in enumerate(sorted_groups):
                # Determine which designer gets this group
                if i < (groups_per_designer + 1) * extra_groups:
                    current_designer = i // (groups_per_designer + 1)
                else:
                    current_designer = (i - extra_groups) // groups_per_designer

                designer_folder = os.path.join(self.source_folder, f'Designer_{current_designer + 1}')
                
                # Process all files in this group
                for image_path in group_files:
                    image_file = os.path.basename(image_path)
                    dest_path = os.path.join(designer_folder, image_file)
                    self.stats['designer_files'][f'Designer_{current_designer + 1}'].append(image_file)

                    try:
                        # Move file first
                        os.rename(image_path, dest_path)
                        
                        # Then apply tag based on background
                        if self.is_white_background(dest_path):
                            self.stats['white_background'] += 1
                            self.apply_mac_tag(dest_path, 6)  # Green tag for white background
                        else:
                            self.stats['non_white_background'] += 1
                            self.apply_mac_tag(dest_path, 4)  # Blue tag for non-white background
                        
                        processed += 1
                        elapsed_time = time.time() - start_time
                        self.progress_updated.emit(processed, self.format_time(elapsed_time), self.stats)

                    except Exception as e:
                        print(f"Error processing {image_file}: {str(e)}")

            # Create Excel report
            self.create_excel_report(start_time)
            self.processing_complete.emit(self.stats)

        except Exception as e:
            print(f"Error in processing thread: {str(e)}")

    def format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def apply_mac_tag(self, file_path, tag_index):
        try:
            # Convert the file path to a format that AppleScript can understand
            file_path = file_path.replace('"', '\\"')
            script = f"""osascript -e 'tell application "Finder" to set label index of (POSIX file "{file_path}" as alias) to {tag_index}'"""
            os.system(script)  # Changed from subprocess.run to os.system
        except Exception as e:
            print(f"Error applying tag: {str(e)}")

    def is_white_background(self, image_path):
        """
        Check if either top-left or top-right corner of the image has a white background.
        """
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                pixels = img.load()
                
                # Check top-left corner (5x5 pixels)
                is_left_white = True
                for x in range(5):
                    for y in range(5):
                        if pixels[x, y][:3] != (255, 255, 255):  # Compare RGB only
                            is_left_white = False
                            break
                    if not is_left_white:
                        break
                
                # Check top-right corner (5x5 pixels)
                is_right_white = True
                for x in range(width-5, width):
                    for y in range(5):
                        if pixels[x, y][:3] != (255, 255, 255):  # Compare RGB only
                            is_right_white = False
                            break
                    if not is_right_white:
                        break
                
                return is_left_white or is_right_white
        except Exception as e:
            print(f"Error checking white background: {e}")
            return False

    def extract_file_id(self, filename):
        """
        Extract the file ID from the filename.
        Returns the first 13 characters if it's a digit, or the first 12 characters if it's alphanumeric.
        """
        # Check for 13-digit number
        if len(filename) >= 13 and filename[:13].isdigit():
            return filename[:13]
        # Check for 12-character alphanumeric
        elif len(filename) >= 12:
            return filename[:12]
        return None

    def create_excel_report(self, start_time):
        try:
            max_files = max(len(files) for files in self.stats['designer_files'].values())
            data = {designer: files + [''] * (max_files - len(files)) 
                   for designer, files in self.stats['designer_files'].items()}
            
            df = pd.DataFrame(data)
            excel_path = os.path.join(self.source_folder, 'SplitImg_Report.xlsx')
            
            with pd.ExcelWriter(excel_path) as writer:
                df.to_excel(writer, sheet_name='Designer Files', index=False)
                
                # Format extensions count for display
                extensions_text = ', '.join(f"{ext} ({count})" for ext, count in self.stats['extensions'].items())
                
                # Calculate total processing time
                total_time = time.time() - start_time
                hours = int(total_time // 3600)
                minutes = int((total_time % 3600) // 60)
                seconds = int(total_time % 60)
                processing_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                
                summary_data = {
                    'Metric': [
                        'Total Images Processed',
                        'White Background Images',
                        'Non-White Background Images',
                        'Supported Extensions',
                        'Total Processing Time'
                    ],
                    'Value': [
                        self.stats['total_images'],
                        self.stats['white_background'],
                        self.stats['non_white_background'],
                        extensions_text,
                        processing_time
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        except Exception as e:
            print(f"Error creating Excel report: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SplitImg Pro V3.0.0")
        self.setMinimumSize(1000, 900)
        
        # Set application icon
        try:
            # Try to get the icon from the executable directory (for built app)
            if getattr(sys, 'frozen', False):
                # Running in a bundle
                icon_path = os.path.join(sys._MEIPASS, 'SplitImg.icns')
            else:
                # Running in normal Python environment
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SplitImg.icns')
            
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            print(f"Error setting icon: {e}")

        # Create menu bar
        self.create_menu_bar()

        # Set dark mode theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                color: #ffffff;
                font-size: 14px;
            }
            QGroupBox {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
                margin-top: 15px;
                padding: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 5px 0 5px;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #4d4d4d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:disabled {
                background-color: #383838;
                color: #808080;
            }
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #2d2d2d;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #ffffff;
                border-radius: 4px;
            }
            QLineEdit {
                background-color: #2d2d2d;
                border: 2px solid #4d4d4d;
                border-radius: 4px;
                padding: 8px;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid #666666;
                background-color: #333333;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #2d2d2d;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #4d4d4d;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Add header information
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        
        title_label = QLabel("SplitImg Pro")
        title_label.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Designed for Saks Global")
        subtitle_label.setStyleSheet("font-size: 18px; color: white;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        main_layout.addLayout(header_layout)

        # Create scroll area for stats
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(20)

        # Designer selection
        designer_group = QGroupBox("Designer Configuration")
        designer_layout = QVBoxLayout()
        designer_layout.setSpacing(10)
        self.designer_label = QLabel("Number of Designers (1-60):")
        self.designer_input = QLineEdit()
        self.designer_input.setValidator(QIntValidator(1, 60))
        self.designer_input.setMaxLength(2)
        self.designer_input.setPlaceholderText("Enter number between 1-60")
        self.designer_input.textChanged.connect(self.validate_designer_input)  # Add text change handler
        designer_layout.addWidget(self.designer_label)
        designer_layout.addWidget(self.designer_input)
        designer_group.setLayout(designer_layout)
        layout.addWidget(designer_group)
        layout.addSpacing(20)

        # Progress bars
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(15)
        
        self.scan_progress_label = QLabel("Scanning Images...")
        self.scan_progress_bar = QProgressBar()
        progress_layout.addWidget(self.scan_progress_label)
        progress_layout.addWidget(self.scan_progress_bar)
        
        self.process_progress_label = QLabel("Processing Images...")
        self.process_progress_bar = QProgressBar()
        progress_layout.addWidget(self.process_progress_label)
        progress_layout.addWidget(self.process_progress_bar)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        layout.addSpacing(20)

        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(10)
        
        self.total_images_label = QLabel("Total Images Processed: 0")
        self.white_bg_label = QLabel("White Background Images: 0")
        self.non_white_bg_label = QLabel("Non-White Background Images: 0")
        self.time_label = QLabel("Time Taken: 00:00:00")
        self.extensions_label = QLabel("Supported Extensions: .png, .jpg, .jpeg, .bmp, .gif, .tiff")
        
        for label in [self.total_images_label, self.white_bg_label, 
                     self.non_white_bg_label, self.time_label, self.extensions_label]:
            label.setStyleSheet("color: white; padding: 5px;")
            stats_layout.addWidget(label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Run button
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.start_processing)
        self.run_button.setFixedHeight(50)
        main_layout.addWidget(self.run_button)

        # Add footer
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(5)
        
        version_label = QLabel("V3.0.0")
        version_label.setStyleSheet("font-size: 14px; color: white;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(version_label)
        
        made_in_label = QLabel("Made in India")
        made_in_label.setStyleSheet("font-size: 12px; color: white;")
        made_in_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(made_in_label)
        
        main_layout.addLayout(footer_layout)

    def create_menu_bar(self):
        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("Start New Split", self)
        new_action.triggered.connect(self.reset_application)
        file_menu.addAction(new_action)
        
        # Window menu
        window_menu = menubar.addMenu("Window")
        
        minimize_action = QAction("Minimize", self)
        minimize_action.triggered.connect(self.showMinimized)
        window_menu.addAction(minimize_action)
        
        zoom_action = QAction("Zoom", self)
        zoom_action.triggered.connect(self.toggle_maximized)
        window_menu.addAction(zoom_action)
        
        fill_action = QAction("Fill", self)
        fill_action.triggered.connect(self.fill_screen)
        window_menu.addAction(fill_action)
        
        center_action = QAction("Center", self)
        center_action.triggered.connect(self.center_window)
        window_menu.addAction(center_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        how_to_use_action = QAction("How to Use", self)
        how_to_use_action.triggered.connect(self.show_how_to_use)
        help_menu.addAction(how_to_use_action)
        
        source_code_action = QAction("Source Code", self)
        source_code_action.triggered.connect(self.show_source_code)
        help_menu.addAction(source_code_action)
        
        contact_support_action = QAction("Contact Support", self)
        contact_support_action.triggered.connect(self.show_contact_support)
        help_menu.addAction(contact_support_action)

    def reset_application(self):
        """Reset the application to its initial state"""
        reply = QMessageBox.question(self, 'Start New Split',
                                   'Are you sure you want to start a new split? This will reset all current progress.',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Reset designer input
                self.designer_input.clear()
                
                # Reset progress bars
                self.scan_progress_bar.setValue(0)
                self.process_progress_bar.setValue(0)
                
                # Reset progress labels
                self.scan_progress_label.setText("Scanning Images...")
                self.process_progress_label.setText("Processing Images...")
                
                # Reset statistics
                self.total_images_label.setText("Total Images Processed: 0")
                self.white_bg_label.setText("White Background Images: 0")
                self.non_white_bg_label.setText("Non-White Background Images: 0")
                self.time_label.setText("Time Taken: 00:00:00")
                
                # Reset button state
                self.run_button.setEnabled(False)
                
                # Clear any error messages safely
                try:
                    for i in reversed(range(self.designer_layout.count())): 
                        item = self.designer_layout.itemAt(i)
                        if item and item.widget():
                            widget = item.widget()
                            if isinstance(widget, QLabel) and widget.text().startswith("Error:"):
                                widget.deleteLater()
                except Exception as e:
                    print(f"Error clearing messages: {e}")
                    
            except Exception as e:
                print(f"Error during reset: {e}")
                QMessageBox.warning(self, "Reset Error", "An error occurred during reset. Please try again.")

    def toggle_maximized(self):
        """Toggle between maximized and normal window state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def fill_screen(self):
        """Fill the screen with the window"""
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

    def center_window(self):
        """Center the window on the screen"""
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.primaryScreen().geometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>SplitImg Pro V3.0.0</h2>
        <p>A professional image distribution tool designed for efficient workflow management.</p>
        <p>© 2024 Saks Global. All rights reserved.</p>
        <p>Made in India</p>
        """
        QMessageBox.about(self, "About SplitImg Pro", about_text)

    def show_how_to_use(self):
        """Show how to use instructions"""
        instructions = """
        <h2>How to Use SplitImg Pro</h2>
        <ol>
            <li>Enter the number of designers (1-60)</li>
            <li>Click the 'Run' button</li>
            <li>Select the folder containing your images</li>
            <li>Wait for the process to complete</li>
            <li>Check the generated Excel report for details</li>
        </ol>
        <p><b>Note:</b> Images are grouped by their unique identifiers and distributed evenly among designers.</p>
        """
        QMessageBox.information(self, "How to Use", instructions)

    def show_source_code(self):
        """Show source code information"""
        source_info = """
        <h2>Source Code</h2>
        <p>SplitImg Pro is built using:</p>
        <ul>
            <li>Python 3.x</li>
            <li>PyQt6 for the user interface</li>
            <li>Pillow for image processing</li>
            <li>pandas for Excel report generation</li>
        </ul>
        <p>For source code access, please contact the development team.</p>
        """
        QMessageBox.information(self, "Source Code", source_info)

    def show_contact_support(self):
        """Show contact support information"""
        support_info = """
        <h2>Contact Support</h2>
        <p>For technical support or questions, please contact:</p>
        <p>Email: karan.khandekar@saks.com</p>
        <p>Phone: +91 82377 49219</p>
        <p>Hours: Monday - Friday, 11:00 AM - 8:00 PM IST</p>
        """
        QMessageBox.information(self, "Contact Support", support_info)

    def start_processing(self):
        # Check if designer input is empty
        if not self.designer_input.text().strip():
            QMessageBox.warning(self, "Error", "Please Select Number of Designer")
            return
            
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            try:
                num_designers = int(self.designer_input.text())
                if num_designers > 60:
                    error_label = QLabel("Error: Maximum 60 designers allowed")
                    error_label.setStyleSheet("color: #ff4444; font-weight: bold;")
                    error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.designer_layout.addWidget(error_label)
                    QTimer.singleShot(3000, error_label.deleteLater)
                    return
                if 1 <= num_designers <= 60:
                    self.processor = ImageProcessor(folder, num_designers)
                    self.processor.progress_updated.connect(self.update_progress)
                    self.processor.processing_complete.connect(self.processing_complete)
                    self.processor.scan_progress.connect(self.update_scan_progress)
                    self.processor.start()
                    self.run_button.setEnabled(False)
                    self.reset_progress()
                else:
                    print("Please enter a number between 1 and 60")
            except ValueError:
                print("Please enter a valid number")

    def reset_progress(self):
        self.scan_progress_bar.setValue(0)
        self.process_progress_bar.setValue(0)
        self.total_images_label.setText("Total Images Processed: 0")
        self.white_bg_label.setText("White Background Images: 0")
        self.non_white_bg_label.setText("Non-White Background Images: 0")
        self.time_label.setText("Time Taken: 00:00:00")

    def update_scan_progress(self, count):
        self.scan_progress_bar.setValue(count)
        self.scan_progress_label.setText(f"Scanning Images... ({count} files found)")

    def update_progress(self, processed, time_taken, stats):
        self.process_progress_bar.setValue(processed)
        self.process_progress_label.setText(f"Processing Images... ({processed}/{stats['total_images']})")
        self.total_images_label.setText(f"Total Images Processed: {stats['total_images']}")
        self.white_bg_label.setText(f"White Background Images: {stats['white_background']}")
        self.non_white_bg_label.setText(f"Non-White Background Images: {stats['non_white_background']}")
        self.time_label.setText(f"Time Taken: {time_taken}")
        self.extensions_label.setText(f"Supported Extensions: {', '.join(f'{ext} ({count})' for ext, count in stats['extensions'].items())}")

    def processing_complete(self, stats):
        self.run_button.setEnabled(True)
        self.process_progress_bar.setValue(stats['total_images'])

    def validate_designer_input(self):
        """Validate the designer input and enable/disable the run button accordingly"""
        try:
            num_designers = int(self.designer_input.text())
            self.run_button.setEnabled(1 <= num_designers <= 60)
        except ValueError:
            self.run_button.setEnabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
