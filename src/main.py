#!/usr/bin/env python
import devlprd

if __name__ == "__main__":
    controller = devlprd.DaemonController()
    controller.start(True)
    