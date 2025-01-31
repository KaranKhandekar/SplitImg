import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import time
from PIL import Image
import threading
import subprocess
import pandas as pd

class SplitImgApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SplitImg")
        self.root.geometry("1000x700")
        self.root.configure(bg="#FFF5F5")
        
        # Configure grid weight
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Left side - Title and subtitle
        self.title_frame = tk.Frame(root, bg="#FFF5F5")
        self.title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=20)
        
        self.title_label = tk.Label(
            self.title_frame, 
            text="SAKS GLOBAL", 
            font=("Arial", 24, "bold"),
            fg="#E91E63",
            bg="#FFF5F5"
        )
        self.title_label.pack(anchor="w")
        
        self.subtitle_label = tk.Label(
            self.title_frame,
            text="SplitImg2\nFor Product Image Team\nMade in India",
            font=("Arial", 12),
            fg="#666666",
            bg="#FFF5F5",
            justify="left"
        )
        self.subtitle_label.pack(anchor="w")
        
        # Right side - Controls
        self.control_frame = tk.Frame(root, bg="#FFF5F5")
        self.control_frame.grid(row=0, column=1, sticky="e", padx=20, pady=20)
        
        # Designer count dropdown
        self.designer_var = tk.StringVar()
        self.designer_combo = ttk.Combobox(
            self.control_frame,
            textvariable=self.designer_var,
            values=[str(i) for i in range(1, 41)],
            width=20,
            state="readonly"
        )
        self.designer_combo.set("Select Designers (1-40)")
        self.designer_combo.pack(pady=5)
        
        # Start button
        self.start_button = tk.Button(
            self.control_frame,
            text="Start",
            command=self.start_process,
            bg="#E91E63",
            fg="black",
            font=("Arial", 12),
            width=20,
            relief="flat"
        )
        self.start_button.pack(pady=5)
        
        # Help button
        self.help_button = tk.Button(
            self.control_frame,
            text="Help",
            command=self.show_help,
            bg="#F4B183",
            fg="black",
            font=("Arial", 12),
            width=20,
            relief="flat"
        )
        self.help_button.pack(pady=5)
        
        # Statistics section - Add to main grid
        self.stats_frame = tk.Frame(root, bg="#FFF5F5")
        self.stats_frame.grid(row=1, column=1, sticky="e", padx=20)
        
        self.total_images_label = tk.Label(
            self.stats_frame,
            text="Total images processed: 0",
            font=("Arial", 12),
            fg="#666666",
            bg="#FFF5F5"
        )
        self.total_images_label.pack(anchor="e")
        
        self.white_bg_label = tk.Label(
            self.stats_frame,
            text="Images with white background: 0",
            font=("Arial", 12),
            fg="#666666",
            bg="#FFF5F5"
        )
        self.white_bg_label.pack(anchor="e")
        
        self.non_white_bg_label = tk.Label(
            self.stats_frame,
            text="Images with non-white background: 0",
            font=("Arial", 12),
            fg="#666666",
            bg="#FFF5F5"
        )
        self.non_white_bg_label.pack(anchor="e")
        
        # Status section
        self.status_frame = tk.Frame(self.control_frame, bg="#FFF5F5")
        self.status_frame.pack(pady=20)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Status",
            font=("Arial", 12),
            fg="#666666",
            bg="#FFF5F5"
        )
        self.status_label.pack()
        
        self.time_label = tk.Label(
            self.status_frame,
            text="Time tracking",
            font=("Arial", 12),
            fg="#666666",
            bg="#FFF5F5"
        )
        self.time_label.pack()
        
        self.error_label = tk.Label(
            self.status_frame,
            text="Error handling",
            font=("Arial", 12),
            fg="#666666",
            bg="#FFF5F5"
        )
        self.error_label.pack()
        
        # Progress section - Fix the geometry manager and size
        self.progress_frame = tk.Frame(root, bg="#D3D3D3", height=100)  # Set fixed height
        self.progress_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20)
        self.progress_frame.grid_propagate(False)  # Prevent frame from shrinking
        
        # Center the content in the progress frame
        self.progress_frame.grid_rowconfigure(0, weight=1)
        self.progress_frame.grid_rowconfigure(1, weight=1)
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_label = tk.Label(
            self.progress_frame,
            text="Process Information Update",
            font=("Arial", 12),
            fg="#666666",
            bg="#D3D3D3"
        )
        self.progress_label.grid(row=0, column=0, pady=(20,5))  # Add padding to center vertically
        
        # Progress bar with specific height
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            length=900,
            mode="determinate"
        )
        self.progress_bar.grid(row=1, column=0, pady=(5,20))  # Add padding to center vertically
        
        # Configure progress bar height (using ttk style)
        style = ttk.Style()
        style.configure("TProgressbar", thickness=10)  # Set progress bar height to 10px
        
        # Initialize variables
        self.processing = False
        self.start_time = None
        
    def is_white_background(self, image_path):
        with Image.open(image_path) as img:
            # Get the top-left and top-right 5x5 pixels
            left_crop = (0, 0, 5, 5)
            right_crop = (img.width - 5, 0, img.width, 5)
            
            left_cropped = img.crop(left_crop)
            right_cropped = img.crop(right_crop)
            
            # Calculate average RGB values for both crops
            left_pixels = list(left_cropped.getdata())
            right_pixels = list(right_cropped.getdata())
            
            # Check left crop
            left_avg_r = sum(p[0] for p in left_pixels) / len(left_pixels)
            left_avg_g = sum(p[1] for p in left_pixels) / len(left_pixels)
            left_avg_b = sum(p[2] for p in left_pixels) / len(left_pixels)
            
            # Check right crop
            right_avg_r = sum(p[0] for p in right_pixels) / len(right_pixels)
            right_avg_g = sum(p[1] for p in right_pixels) / len(right_pixels)
            right_avg_b = sum(p[2] for p in right_pixels) / len(right_pixels)
            
            # Consider it white if either left or right crop is white (RGB values > 240)
            left_is_white = all(x > 240 for x in (left_avg_r, left_avg_g, left_avg_b))
            right_is_white = all(x > 240 for x in (right_avg_r, right_avg_g, right_avg_b))
            
            return left_is_white or right_is_white
    
    def set_finder_tag(self, file_path, is_white):
        tag = "Yellow" if is_white else "Green"
        applescript = f'''
        tell application "Finder"
            set theFile to POSIX file "{file_path}" as alias
            set label index of theFile to {6 if is_white else 4}
        end tell
        '''
        subprocess.run(["osascript", "-e", applescript])
    
    def process_images(self, folder_path, num_designers):
        try:
            # Initialize counters and storage for SVS groups
            self.white_bg_count = 0
            self.non_white_bg_count = 0
            svs_groups = {}
            designer_assignments = {}  # To track which designer got which files
            
            # Get all image files
            image_files = [f for f in os.listdir(folder_path) 
                         if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            if not image_files:
                messagebox.showerror("Error", "No image files found in the selected folder")
                return
            
            # Group files by SVS number (first 13 digits)
            for image_file in image_files:
                svs = image_file[:13]  # Get first 13 digits (SVS number)
                if svs not in svs_groups:
                    svs_groups[svs] = []
                svs_groups[svs].append(image_file)
            
            # Create designer folders and initialize assignment tracking
            designer_folders = []
            for i in range(num_designers):
                folder_name = f"Designer_{i+1}"
                folder_path_full = os.path.join(folder_path, folder_name)
                os.makedirs(folder_path_full, exist_ok=True)
                designer_folders.append(folder_path_full)
                designer_assignments[folder_name] = []
            
            # Distribute SVS groups across designers
            total_images = len(image_files)
            processed_count = 0
            designer_idx = 0
            
            # Sort SVS groups by size (largest first) to ensure even distribution
            sorted_svs = sorted(svs_groups.items(), key=lambda x: len(x[1]), reverse=True)
            
            # Assign each SVS group to a designer
            for svs, group_files in sorted_svs:
                target_folder = designer_folders[designer_idx]
                designer_name = f"Designer_{designer_idx + 1}"
                
                # Process all files in this SVS group
                for image_file in group_files:
                    # Update progress
                    processed_count += 1
                    progress = (processed_count / total_images) * 100
                    self.root.after(0, self.progress_bar.configure, {"value": progress})
                    self.root.after(0, self.progress_label.configure, 
                                  {"text": f"Processing image {processed_count} of {total_images}"})
                    
                    # Process image
                    image_path = os.path.join(folder_path, image_file)
                    
                    # Check background and set tag
                    is_white = self.is_white_background(image_path)
                    if is_white:
                        self.white_bg_count += 1
                    else:
                        self.non_white_bg_count += 1
                    
                    self.set_finder_tag(image_path, is_white)
                    
                    # Move file and track assignment
                    shutil.move(image_path, os.path.join(target_folder, image_file))
                    designer_assignments[designer_name].append(image_file)
                    
                    # Update statistics in real-time
                    self.root.after(0, self.total_images_label.configure, 
                                  {"text": f"Total images processed: {processed_count}/{total_images}"})
                    self.root.after(0, self.white_bg_label.configure, 
                                  {"text": f"Images with white background: {self.white_bg_count}"})
                    self.root.after(0, self.non_white_bg_label.configure, 
                                  {"text": f"Images with non-white background: {self.non_white_bg_count}"})
                
                # Move to next designer for next SVS group
                designer_idx = (designer_idx + 1) % num_designers
            
            # Generate Excel report
            self.generate_assignment_report(folder_path, designer_assignments)
            
            # Show final statistics
            stats_message = f"""Processing completed successfully!
            
Total images processed: {total_images}
Images with white background: {self.white_bg_count}
Images with non-white background: {self.non_white_bg_count}

An Excel report has been generated with the distribution details."""
            
            messagebox.showinfo("Success", stats_message)
            
        except Exception as e:
            self.root.after(0, self.error_label.configure, {"text": f"Error: {str(e)}"})
            messagebox.showerror("Error", str(e))
        
        finally:
            self.processing = False
            self.update_time()
    
    def generate_assignment_report(self, folder_path, designer_assignments):
        # Get current date in MM-DD-YYYY format
        current_date = time.strftime("%m-%d-%Y")
        
        # Create Excel writer with date in filename
        excel_path = os.path.join(folder_path, f'image_distribution_report_{current_date}.xlsx')
        writer = pd.ExcelWriter(excel_path, engine='xlsxwriter')
        
        # Create data structure for the report
        max_files = max(len(files) for files in designer_assignments.values())
        data = {}
        
        for designer, files in designer_assignments.items():
            # Count white and non-white backgrounds for this designer
            white_count = 0
            non_white_count = 0
            for file in files:
                file_path = os.path.join(folder_path, designer, file)
                is_white = self.is_white_background(file_path)
                if is_white:
                    white_count += 1
                else:
                    non_white_count += 1
            
            # Create column data for this designer
            column_data = [
                designer,  # Designer name
                f"Total Images: {len(files)}",  # Total count
                f"White Background: {white_count}",  # White background count
                f"Non-White Background: {non_white_count}",  # Non-white background count
                "Files:"  # Header for file list
            ]
            column_data.extend(files)  # Add all files
            
            # Pad with empty strings if needed
            while len(column_data) < max_files + 5:  # +5 for the header rows
                column_data.append("")
                
            data[designer] = column_data
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Write to Excel
        df.to_excel(writer, sheet_name='Distribution Report', index=False)
        
        # Format the worksheet
        worksheet = writer.sheets['Distribution Report']
        
        # Set column widths
        for idx, col in enumerate(df.columns):
            worksheet.set_column(idx, idx, 50)  # Set each column width to 50
        
        writer.close()
    
    def start_process(self):
        if self.processing:
            return
            
        if not self.designer_var.get() or self.designer_var.get() == "Select Designers (1-40)":
            messagebox.showerror("Error", "Please select number of designers")
            return
            
        folder_path = filedialog.askdirectory(title="Select Image Folder")
        if not folder_path:
            return
            
        self.processing = True
        self.start_time = time.time()
        num_designers = int(self.designer_var.get())
        
        # Start processing in a separate thread
        thread = threading.Thread(
            target=self.process_images,
            args=(folder_path, num_designers)
        )
        thread.start()
        
        # Start time update
        self.update_time()
    
    def update_time(self):
        if self.processing and self.start_time:
            elapsed = int(time.time() - self.start_time)
            self.time_label.configure(text=f"Time elapsed: {elapsed}s")
            self.root.after(1000, self.update_time)
    
    def show_help(self):
        help_text = """
        How to use SplitImg:
        1. Select the number of designers (1-40)
        2. Click 'Start' and choose the folder with images
        3. Wait for processing to complete
        
        The app will:
        - Distribute images among designer folders
        - Tag white backgrounds with Yellow
        - Tag non-white backgrounds with Green
        """
        messagebox.showinfo("Help", help_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = SplitImgApp(root)
    root.mainloop()
