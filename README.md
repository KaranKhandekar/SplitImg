# SplitImg Pro

SplitImg Pro is a macOS application that helps distribute images across multiple designer folders while automatically tagging them based on their background color.

## Features

- Supports multiple image formats (PNG, JPEG, BMP, GIF, TIFF)
- Automatic background color detection
- Color-based tagging (yellow for white background, green for gray background)
- Round-robin distribution of images across designer folders
- Real-time progress tracking
- Simple and intuitive user interface

## Installation

1. Ensure you have Python 3.8 or later installed on your system
2. Clone this repository or download the source code
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Select the number of designers (1-15) from the dropdown menu

3. Click the "Run" button

4. Select the folder containing the images you want to process

5. The application will:
   - Create separate folders for each designer
   - Process all images in the source folder
   - Tag images based on their background color
   - Distribute images evenly among the designer folders
   - Show progress and completion status

## Background Color Detection

The application analyzes the top-right corner of each image to determine its background color:
- White background (RGB: 255, 255, 255) → Yellow tag
- Gray background (RGB: ~128, ~128, ~128) → Green tag
- Other backgrounds → No tag

## Requirements

- macOS operating system
- Python 3.8 or later
- PyQt6
- Pillow (PIL) 