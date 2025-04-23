import os
import shutil
import subprocess

# Clean up previous builds
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

# Install py2app if not already installed
try:
    import py2app
except ImportError:
    subprocess.check_call(['pip', 'install', 'py2app'])

# Build using py2app
print("Building app with py2app...")
subprocess.check_call(['python', 'setup.py', 'py2app'])

print("\nBuild completed! Check the 'dist' folder for the application.") 