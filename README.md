# devlprd
[![Python application](https://github.com/FANTM/devlprd/actions/workflows/python-app.yml/badge.svg)](https://github.com/FANTM/devlprd/actions/workflows/python-app.yml)

## Overview
The FANTM DEVLPR daemon for managing and publishing data streams. It serves as a middleware between the hardware itself, and whatever integration you want to make. 
It exists to both abstract away data processing from the end application, and to allow for language agnostic integrations. Right now there is only a [python endpoint](https://github.com/FANTM/pydevlpr), but there are plans for JS and more in the near future. 
In effect, first an Arduino is flashed with the provided firmware, then the daemon is launched, and then the application that you're using the data with. 

## Getting Started
The first thing that needs to be done is formatting the Arduino. In the `arduino_firmware` folder there are scripts that format the data in such a way that the daemon can package, process, and send it out easily. 
So [flash an arduino](https://www.arduino.cc/en/Guide) with one of those scripts and make sure it is connected to the computer you will be running the daemon from.

This project uses [Poetry](https://python-poetry.org/) for dependency management, and while it's not required to get started it's a useful tool. All of the dependencies are in `pyproject.toml`,
so just run `poetry install`. Then just run `poetry run python src/main.py` and the daemon should start.

## Development
### Adding a data transformer
To add support for a new data transformer, edit the `self.callbacks: Dict[str, Callable[[int], Union[int, bool]]]` dictionary in the `__init__` function of DaemonState (in `DaemonState.py`).
You will need to add a new entry with a data topic, using one of the supported topics defined in `protocol.py` and a function. 
The function is a callback that takes a single int as an arguement representing the pin the data is coming from on the Arduino.
The function should be inside of DaemonState, but it can be wrapper for a function living in another file (`filtering.py` is usually a good choice). 

Now whenever a client subscribes to your topic, the callback will be called and you'll see your data stream.

### Adding a new data topic
Add a new line to the DataTopic class in `protocol.py` with an ALL_CAPS_NAME and a unique two letter identifier. 
Then go to the [`protocol.py`](https://github.com/FANTM/pydevlpr/blob/main/src/pydevlpr/protocol.py) in the `pydevlpr` repository and add it there as well so others can use the topic. 

### Adding support for different types of messages
Add a new line in the PacketType class in `protocol.py` with an ALL_CAPS_NAME and a unique one letter identifier. 
Then go to `daemon.py` and add an `elif command == PacketType.ALL_CAPS_NAME` with the handler for your custom packet type to the `receive(...)` function.
