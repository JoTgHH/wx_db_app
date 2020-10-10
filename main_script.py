from wx import App
from custom_frame import CustomFrame


def main():
    app = App()
    myFrame = CustomFrame()
    app.MainLoop()


if __name__ == '__main__':
    main()
