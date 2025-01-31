from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': ['tkinter', 'PIL', 'pandas', 'xlsxwriter', 'pkg_resources', 'jaraco.text', 
                'jaraco.functools', 'jaraco.context', 'autocommand', 'more_itertools'],
    'excludes': ['packaging'],
    'iconfile': 'SplitImg.icns',
    'plist': {
        'CFBundleName': 'SplitImg',
        'CFBundleDisplayName': 'SplitImg',
        'CFBundleIdentifier': 'com.saks.splitimg',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': '© 2024 Saks Global'
    },
    'strip': False,
    'semi_standalone': True,
    'site_packages': True,
    'includes': ['PIL', 'pandas', 'xlsxwriter', 'jaraco', 'jaraco.text', 'jaraco.functools', 
                'jaraco.context', 'autocommand', 'more_itertools'],
    'frameworks': [],
    'resources': []
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=['jaraco.text', 'jaraco.functools', 'jaraco.context', 'autocommand', 'more-itertools'],
    name='SplitImg'
)
