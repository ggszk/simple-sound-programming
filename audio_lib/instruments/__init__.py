"""
instruments モジュール - 楽器クラス
"""

from .basic_instruments import (
    BaseInstrument, SimpleSynthesizer,
    BasicPiano, BasicOrgan, BasicGuitar, BasicDrum,
    Piano, Organ, Guitar, Drum,
)

__all__ = [
    "BaseInstrument", "SimpleSynthesizer",
    "BasicPiano", "BasicOrgan", "BasicGuitar", "BasicDrum",
    "Piano", "Organ", "Guitar", "Drum",
]
