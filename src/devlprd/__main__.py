from .daemon import DaemonController

if __name__ == "__main__":
    controller = DaemonController('DEVLPR')
    controller.start(True)
    