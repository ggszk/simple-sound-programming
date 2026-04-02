"""
音声信号データとサンプリングレートをセットで管理するクラス

音響処理において、信号データ（np.ndarray）とサンプリングレートは
切り離せない情報であり、常にセットで扱う。
"""

import numpy as np
from scipy.io import wavfile


class AudioSignal:
    """音声信号データとサンプリングレートをセットで管理するクラス"""

    def __init__(self, data: np.ndarray, sample_rate: int = 44100):
        """
        Args:
            data: 音声データ（float64, 通常 -1.0 〜 1.0）
            sample_rate: サンプリングレート（Hz）
        """
        self.data = np.asarray(data, dtype=np.float64)
        self.sample_rate = sample_rate

    @property
    def duration(self) -> float:
        """信号の長さ（秒）"""
        return len(self.data) / self.sample_rate

    @property
    def num_samples(self) -> int:
        """サンプル数"""
        return len(self.data)

    # --- ファイルI/O ---

    def save(self, filename: str) -> None:
        """WAVファイルとして保存

        Args:
            filename: 保存先ファイル名
        """
        max_amplitude = 0.95  # クリッピング防止
        clipped = np.clip(self.data, -max_amplitude, max_amplitude)
        audio_16bit = (clipped * 32767).astype(np.int16)
        wavfile.write(filename, self.sample_rate, audio_16bit)

    # --- 算術演算 ---

    def __mul__(self, other: "AudioSignal | int | float | np.ndarray") -> "AudioSignal":
        """信号 * エンベロープ、信号 * 音量係数"""
        if isinstance(other, AudioSignal):
            _check_same_sample_rate(self, other)
            min_len = min(len(self.data), len(other.data))
            return AudioSignal(self.data[:min_len] * other.data[:min_len], self.sample_rate)
        elif isinstance(other, (int, float, np.ndarray)):
            return AudioSignal(self.data * other, self.sample_rate)
        return NotImplemented

    def __rmul__(self, other: "int | float | np.ndarray") -> "AudioSignal":
        return self.__mul__(other)

    def __add__(self, other: "AudioSignal | int | float") -> "AudioSignal":
        """信号の重ね合わせ（ミキシング）"""
        if isinstance(other, AudioSignal):
            _check_same_sample_rate(self, other)
            # 長さが異なる場合はゼロパディングで合わせる
            max_len = max(len(self.data), len(other.data))
            a = np.zeros(max_len, dtype=np.float64)
            b = np.zeros(max_len, dtype=np.float64)
            a[: len(self.data)] = self.data
            b[: len(other.data)] = other.data
            return AudioSignal(a + b, self.sample_rate)
        elif isinstance(other, (int, float)):
            return AudioSignal(self.data + other, self.sample_rate)
        return NotImplemented

    def __radd__(self, other: "int | float") -> "AudioSignal":
        return self.__add__(other)

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return f"AudioSignal(samples={self.num_samples}, sample_rate={self.sample_rate}, duration={self.duration:.3f}s)"


def _check_same_sample_rate(a: AudioSignal, b: AudioSignal) -> None:
    """2つのAudioSignalのsample_rateが一致するか検証"""
    if a.sample_rate != b.sample_rate:
        raise ValueError(
            f"sample_rateが一致しません: {a.sample_rate}Hz と {b.sample_rate}Hz"
        )


# --- ファイルI/O関数 ---

def save_audio(filename: str, signal: AudioSignal) -> None:
    """AudioSignalをWAVファイルとして保存

    Args:
        filename: 保存先ファイル名
        signal: 保存する音声信号
    """
    signal.save(filename)


def load_audio(filename: str) -> AudioSignal:
    """WAVファイルを読み込みAudioSignalとして返す

    Args:
        filename: 読み込むファイル名

    Returns:
        AudioSignal: 読み込んだ音声信号
    """
    file_sample_rate, audio_data = wavfile.read(filename)
    audio_data = audio_data.astype(np.float64)

    # 16bitの場合の正規化 (-1.0 〜 1.0)
    if np.max(np.abs(audio_data)) > 1.0:
        audio_data = audio_data / 32768.0

    return AudioSignal(audio_data, file_sample_rate)
