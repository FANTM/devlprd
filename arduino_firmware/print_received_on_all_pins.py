import pydevlpr

def printpin0(payload: str) -> None:
    print(('0',payload))

def printpin1(payload: str) -> None:
    print(('1',payload))

def printpin2(payload: str) -> None:
    print(('2',payload))

def printpin3(payload: str) -> None:
    print(('3',payload))

def printpin4(payload: str) -> None:
    print(('4',payload))

def printpin5(payload: str) -> None:
    print(('5',payload))

pydevlpr.add_callback(pydevlpr.DataTopic.RAW_DATA_TOPIC, 0, printpin0)
pydevlpr.add_callback(pydevlpr.DataTopic.RAW_DATA_TOPIC, 1, printpin1)
pydevlpr.add_callback(pydevlpr.DataTopic.RAW_DATA_TOPIC, 2, printpin2)
pydevlpr.add_callback(pydevlpr.DataTopic.RAW_DATA_TOPIC, 3, printpin3)
pydevlpr.add_callback(pydevlpr.DataTopic.RAW_DATA_TOPIC, 4, printpin4)
pydevlpr.add_callback(pydevlpr.DataTopic.RAW_DATA_TOPIC, 5, printpin5)

while True:
    pass

pydevlpr.close()