try:
    from cryptoBar.cryptoBar import CryptoBar
except ImportError:
    from cryptoBar import CryptoBar

if __name__ == "__main__":

    # app initialization
    app = CryptoBar('Cryptowatch', quit_button = None).run()
