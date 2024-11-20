<h1>Overview</h1>

SplitImg for Designers is a utility application developed for Saks Global. This tool automates the process of organizing, tagging, and distributing images among designers. It assigns color tags based on the background color of the images and ensures a smooth workflow by splitting images into designated folders for each designer.

<h1>Key Features</h1>

Supports multiple image formats: PNG, JPEG, BMP, GIF, TIFF<br>
Automatically assigns green or yellow tags based on the image's background color<br>
Distributes images among selected designers using a round-robin method<br>
Displays the number of images processed and the time taken for the task<br>
Simple UI for quick and efficient image sorting<br>

<h1>How It Works</h1>

SplitImg works by processing images in a selected folder and distributing them across multiple designer folders. The software performs the following steps:

<b>Image Identification</b>: The software scans the source folder for images in supported formats (PNG, JPEG, BMP, GIF, TIFF).<br>
<b>Background Color Check</b>: Each image's top-right corner is analyzed to determine if the background is white or gray. If the background is white, the image is tagged with a yellow label; if gray, it is tagged with a green label.<br>
<b>Round-Robin Distribution</b>: The images are distributed among the specified number of designers using a round-robin method, ensuring an even split of images.<br>
<b>Tagging</b>: Tags (green or yellow) are applied to the images using macOS AppleScript commands. This allows easy identification of images based on background color.<br>
<b>Logging and Feedback</b>: The software keeps track of the number of images processed and the time taken for the operation, providing real-time feedback in the user interface.<br>

<h1>Background Calculations</h1>

The software checks the background of each image by analyzing a small region of the image. Specifically, it looks at the top-right corner of the image (the last few pixels in that region). The following logic is applied:

If the pixels in the top-right corner match the color (255, 255, 255), which represents white, the image is considered to have a white background.
If the pixel color is close to RGB (128, 128, 128), the image is considered to have a gray background.
Images that don't fit into these categories are skipped, and the software doesn't apply any tags to them.

<h1>How to Use</h1>

Follow these simple steps to use the SplitImg software:

<b>Step 1</b>: Open the application and select the number of designers from the dropdown (up to 15). This will determine how the images are distributed.<br>
<b>Step 2</b>: Click the "Run" button to begin the process.<br>
<b>Step 3</b>: A file dialog will appear. Select the folder containing the images you want to process.<br>
<b>Step 4</b>: The software will begin processing the images. As it works, it will display the number of images processed and the time taken for the task.<br>
<b>Step 5</b>: Once the process is complete, you will be notified, and the images will be placed in separate folders for each designer, with appropriate tags applied.<be>

<h1>How the Software Works</h1>

The SplitImg software works by analyzing images and performing the following tasks:

<b>Image Selection</b>: You choose a folder containing images to be processed.<br>
<b>Background Analysis</b>: The software checks the background of each image by analyzing the top-right corner and determining if the background is white or gray.<br>
<b>Tagging</b>: If the background is gray, the image receives a green tag. If the background is white, the image gets a yellow tag.<br>
<b>Distribution</b>: The software then distributes the images among the specified number of designers using a round-robin method.<br>

<h1>Steps to Use the Software</h1>

<b>Step 1</b>: Open the SplitImg application.<br>
<b>Step 2</b>: Select the number of designers (up to 15) from the dropdown list.<br>
<b>Step 3</b>: Click the "Run" button to start the process.<br>
<b>Step 4</b>: A dialog box will open. Select the folder that contains the images you want to process.<br>
<b>Step 5</b>: Wait while the software processes the images. You will see the number of images processed and the time taken for the operation displayed in real-time.<br>
<b>Step 6</b>: Once the process is complete, the images will be sorted into folders, and the green or yellow tags will be applied as per their background color.<br>

<h1>Technical Background</h1>

The software calculates the background color of each image by examining the top-right corner. It uses basic RGB values to determine the dominant color:

White Background: Identified when the pixel color is RGB (255, 255, 255).
Gray Background: Identified when the pixel color is close to RGB (128, 128, 128).
The software then assigns the appropriate tag and distributes the image based on the settings provided.

<h1>Developer Information</h1>

This tool was developed by Karan Khandekar, specifically for Saks Global. It aims to streamline the workflow for designers working on image-based tasks by automating the organization and tagging process.
