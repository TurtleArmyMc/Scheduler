import os
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

from ui.qt_main import App


if __name__ == "__main__":
    app = App()
    app.run()