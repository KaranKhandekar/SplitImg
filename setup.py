from setuptools import setup

APP = ['main.py']
DATA_FILES = ['icon.icns']  # Include the icon file
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'icon.icns',  # Path to your icon file
    'packages': ['PIL', 'tkinter'],
}

setup(
    app=APP,
    name='SortImg',  # Set the name of your application
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
