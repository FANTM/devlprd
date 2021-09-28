from .daemon import DaemonController

if __name__ == "__main__":
    controller = DaemonController()
    controller.start(True)
    