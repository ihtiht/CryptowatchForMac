from setuptools import setup

APP = ['CryptowatchForMac.py']
APP_NAME = "Cryptowatch For Mac"
DATA_FILES = [('', ['data'])]
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'data/app.icns',
    'plist': {
        'LSUIElement': True,
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleGetInfoString': "Cryptowatch For MacOS info",
        'CFBundleIdentifier': "com.danishdua.osx.CryptowatchForMac",
        'CFBundleVersion': "0.2",
        'CFBundleShortVersionString': "0.2",
        'NSHumanReadableCopyright': u"Copyright \u00a9, 2017, Danish Dua"
    },
    'packages': ['rumps'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
