from setuptools import setup

APP = ['CryptowatchForMac.py']
APP_NAME = "Cryptowatch For Mac"
DATA_FILES = [('', ['data', 'configuration'])]
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'icons/app.icns',
    'plist': {
        'LSUIElement': True,
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleGetInfoString': "Cryptowatch For MacOS info",
        'CFBundleIdentifier': "com.danishdua.osx.CryptowatchForMac",
        'CFBundleVersion': "0.3",
        'CFBundleShortVersionString': "0.3",
        'NSHumanReadableCopyright': u"Copyright \u00a9, 2017, Danish Dua"
    },
    'packages': ['rumps', 'cryptoBar'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    url='http://github.com/dandua98/CryptowatchForMac',
    author='Danish Dua',
    author_email='danishdua1998@gmail.com',
    license='MIT',
)
