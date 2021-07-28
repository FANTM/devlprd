#!/usr/bin/env python
import asyncio
import devlprd.daemon as daemon

if __name__ == "__main__":
    asyncio.run(daemon.startup())
