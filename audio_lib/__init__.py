"""
音のプログラミング - 教育的音響合成ライブラリ

関数とオブジェクトの使い分け:
- 波形生成・エンベロープ: 関数（状態なし）
- フィルター・エフェクト・楽器・シーケンサー: オブジェクト（状態あり）
"""

# 信号データ
from .core.audio_signal import AudioSignal, save_audio, load_audio

# 波形生成（関数）
from .synthesis.oscillators import sine_wave, sawtooth_wave, square_wave, triangle_wave, additive_synth, white_noise, pink_noise

# エンベロープ（関数）
from .synthesis.envelopes import adsr, linear_envelope, cosine_envelope

# 音程ユーティリティ（関数）
from .synthesis.note_utils import note_to_frequency, frequency_to_note, note_name_to_number, number_to_note_name

# フィルター（オブジェクト）
from .effects.filters import LowPassFilter, HighPassFilter, BandPassFilter

# エフェクト（オブジェクト）
from .effects.audio_effects import Reverb, Distortion, Delay, Chorus, Compressor

# 楽器（オブジェクト）
from .instruments.basic_instruments import (
    BaseInstrument, SimpleSynthesizer,
    BasicPiano, BasicOrgan, BasicGuitar, BasicDrum,
    Piano, Organ, Guitar, Drum,
)

# シーケンサー（オブジェクト）
from .sequencer import Sequencer, Note, Track, create_simple_melody, create_chord

# ノートブック用ヘルパー（オプショナル依存: matplotlib, IPython）
# audio_lib.notebook として利用可能

__version__ = "1.0.0"
