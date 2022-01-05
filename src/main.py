#!/usr/bin/env python
import devlprd
import asyncio

if __name__ == "__main__":
    controller = devlprd.DaemonController('DEVLPR')
    asyncio.run(controller.start(True))
