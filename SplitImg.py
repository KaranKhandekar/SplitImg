import os
import shutil
import time
import webbrowser
from tkinter import Tk, Button, Label, filedialog, messagebox, StringVar, OptionMenu
from PIL import Image

def tag_file(filepath, color_tag):
    """
    Apply macOS tags to files using AppleScript commands.
    """
    try:
        # Use AppleScript to apply tags
        tag_command = f"""osascript -e 'tell application "Finder" to set label index of (POSIX file "{filepath}" as alias) to {color_tag}'"""
        os.system(tag_command)
    except Exception as e:
        print(f"Error tagging file {filepath}: {e}")

def split_images(source_folder, num_designers, status_label, count_label, time_label):
    """
    Split images into folders based on the number of designers and tag files based on background color.
    """
    start_time = time.time()
    status_label.config(text="Status: In Progress")
    count = 0

    # Create folders for designers
    designer_folders = []
    for i in range(1, num_designers + 1):
        folder_path = os.path.join(source_folder, f"Designer_{i}")
        os.makedirs(folder_path, exist_ok=True)
        designer_folders.append(folder_path)

    # Group files by ID (first 13 characters of the filename)
    file_groups = {}
    for filename in os.listdir(source_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
            file_id = filename[:13]  # Extract first 13 characters as ID
            file_groups.setdefault(file_id, []).append(filename)

    # Distribute files among designers
    grouped_ids = list(file_groups.keys())
    for idx, file_id in enumerate(grouped_ids):
        target_folder = designer_folders[idx % num_designers]  # Round-robin distribution
        for filename in file_groups[file_id]:
            image_path = os.path.join(source_folder, filename)
            try:
                # Determine background and tag accordingly
                if filename.lower().endswith('.png') or not is_white_background(image_path):
                    tag_file(image_path, 6)  # Green tag for Gray Background Images
                else:
                    tag_file(image_path, 3)  # Yellow tag for White Background Images
                
                shutil.move(image_path, os.path.join(target_folder, filename))
                count += 1
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

    elapsed_time = time.time() - start_time
    status_label.config(text="Status: Idle")
    count_label.config(text=f"Images Processed: {count}")
    time_label.config(text=f"Time Taken: {elapsed_time:.2f} seconds")
    messagebox.showinfo("Process Complete", "Image splitting and tagging complete.")

def run_app():
    root = Tk()
    root.title("SplitImg for Saks Global")
    root.geometry("500x600")
    root.configure(bg='black')  # Set background to black

    # Designer count dropdown
    designer_count_var = StringVar(root)
    designer_count_var.set("1")  # Default value

    designer_count_label = Label(root, text="Select the number of Designers", font=('Helvetica', 14), fg='white', bg='black')
    designer_count_label.pack(pady=10)

    designer_count_dropdown = OptionMenu(root, designer_count_var, *[str(i) for i in range(1, 16)])  # Limit to 15 designers
    designer_count_dropdown.config(bg='black', fg='white')  # Set dropdown to white text and black background
    designer_count_dropdown.pack(pady=10)

    def on_run():
        num_designers = int(designer_count_var.get())
        source_folder = filedialog.askdirectory(title="Select Source Folder")
        if source_folder:
            split_images(source_folder, num_designers, status_label, count_label, time_label)
        else:
            messagebox.showwarning("No Folder Selected", "Please select a source folder.")

    # Run button
    run_button = Button(root, text="Run", command=on_run, font=('Helvetica', 12), bg='gray', fg='white')
    run_button.pack(pady=15)

    # Status labels
    status_label = Label(root, text="Status: Idle", font=('Helvetica', 12), fg='white', bg='black')
    status_label.pack(pady=5)

    count_label = Label(root, text="Images Processed: 0", font=('Helvetica', 12), fg='white', bg='black')
    count_label.pack(pady=5)

    time_label = Label(root, text="Time Taken: 0.00 seconds", font=('Helvetica', 12), fg='white', bg='black')
    time_label.pack(pady=5)

    # Static text at the bottom
    static_text = Label(root, text="Made for Saks Global\nBy Karan Khandekar", font=('Helvetica', 12), fg='white', bg='black')
    static_text.pack(side='bottom', pady=10)

    # Documentation and User Guide buttons
    doc_button = Button(root, text="Documentation", command=lambda: open_link("https://karankhandekar.github.io/SplitImg/documentation.html"), font=('Helvetica', 12), bg='gray', fg='white')
    doc_button.pack(pady=5)

    user_guide_button = Button(root, text="User Guide", command=lambda: open_link("https://karankhandekar.github.io/SplitImg/how_to_use.html"), font=('Helvetica', 12), bg='gray', fg='white')
    user_guide_button.pack(pady=5)

    root.mainloop()

def open_link(url):
    webbrowser.open(url)

def is_white_background(image_path):
    """
    Check if the top-right corner of the image has a white background.
    """
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            pixels = img.load()
            for x in range(width-5, width):
                for y in range(5):
                    if pixels[x, y][:3] != (255, 255, 255):  # Compare RGB only
                        return False
            return True
    except Exception as e:
        print(f"Error checking white background: {e}")
        return False

if __name__ == "__main__":
    run_app()
