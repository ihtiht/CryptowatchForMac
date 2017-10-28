from setuptools import setup

APP = ['CryptoWatchForMac.py']
APP_NAME = "CryptoWatchForMac"
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'app.icns',
    'plist': {
        'LSUIElement': True,
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleGetInfoString': "Cryptowatch For MacOS info",
        'CFBundleIdentifier': "com.danishdua.osx.CryptoWatchForMac",
        'CFBundleVersion': "0.1",
        'CFBundleShortVersionString': "0.1",
        'NSHumanReadableCopyright': "Copyright \u00a9, Danish Dua"
    },
    'packages': ['rumps'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
