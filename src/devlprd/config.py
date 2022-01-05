from typing import Dict, List, Union

Board = Dict[str, Union[str, int]]

ADDRESS = ("localhost", 8765)  # (Address/IP, Port)

BOARDS: Dict[str, Board] = {
    'DEVLPR': {
        'BAUD': 2_000_000,
        'NAME': 'arduino',
        'NUM PINS': 6,
        'VID': 0x2341
    },
    'Neuron': {
        'BAUD':  2_000_000,
        'NAME': 'neuron',
        'NUM PINS': 8,
        'VID': 0xcafe
    }
}

def get_board_ids() -> List[str]:
    return list(BOARDS.keys())