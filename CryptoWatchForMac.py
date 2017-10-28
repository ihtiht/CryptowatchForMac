import rumps

class BarApp(rumps.App):

    @rumps.clicked("Set an onclick")
    def iniOption(self, _):
        rumps.notification("Version 0.1", "This is just an Initial build", \
        "Info to be displayed later")

if __name__ == "__main__":
    BarApp("Initial Setup").run()
