"""
synthesis モジュール - 音響合成機能
"""

from .oscillators import sine_wave, sawtooth_wave, square_wave, triangle_wave, white_noise, pink_noise
from .envelopes import adsr, linear_envelope, cosine_envelope
from .note_utils import note_to_frequency, frequency_to_note, note_name_to_number, number_to_note_name, create_scale

__all__ = [
    "sine_wave", "sawtooth_wave", "square_wave", "triangle_wave", "white_noise", "pink_noise",
    "adsr", "linear_envelope", "cosine_envelope",
    "note_to_frequency", "frequency_to_note", "note_name_to_number", "number_to_note_name", "create_scale",
]
