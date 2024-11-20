from setuptools import setup

APP = ['SplitImg.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['numpy', 'Pillow'],  # List the libraries here
    'iconfile': 'app_icon.icns',
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

