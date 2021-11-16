from typing import Dict, List, Union

Board = Dict[str, Union[str, int]]

CONFIG = {
    'ADDRESS': ("localhost", 8765)  # (Address/IP, Port)
}

BOARDS: Dict[str, Board] = {
    'DEVLPR': {
        'BAUD': 2_000_000,
        'NAME': 'arduino',
        'NUM PINS': 6
    },
    'Neuron': {
        'BAUD': 115_200,
        'NAME': 'neuron',
        'NUM PINS': 8
    }
}

def get_board_ids() -> List[str]:
    return list(BOARDS.keys())