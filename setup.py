from setuptools import setup

APP = ['main.py']
DATA_FILES = ['SplitImg.icns']
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'SplitImg.icns',
    'plist': {
        'CFBundleName': 'SplitImg Pro',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleIdentifier': 'com.saksglobal.splitimgpro',
        'NSHumanReadableCopyright': '© 2023 SaksGlobal',
        'CFBundleDocumentTypes': [],
    },
    'packages': ['PyQt6', 'PIL', 'pandas'],
    'excludes': ['PyInstaller', '_webp'],
    'includes': ['PIL'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    name='SplitImg Pro'
) 