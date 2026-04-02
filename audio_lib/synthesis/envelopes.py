"""
エンベロープ（音量変化）生成関数

各関数は継続時間とパラメータを受け取り、AudioSignalを返す。
状態を持たない純粋な関数として設計。
"""

import numpy as np
from ..core.audio_signal import AudioSignal


def adsr(
    duration: float,
    attack: float = 0.1,
    decay: float = 0.1,
    sustain: float = 0.7,
    release: float = 0.2,
    gate_time: float | None = None,
    sample_rate: int = 44100,
) -> AudioSignal:
    """ADSRエンベロープを生成

    Args:
        duration: 全体の継続時間 (秒)
        attack: アタック時間 (秒)
        decay: ディケイ時間 (秒)
        sustain: サステインレベル (0.0-1.0)
        release: リリース時間 (秒)
        gate_time: ゲート時間 (秒)。Noneの場合はduration - release
        sample_rate: サンプリングレート (Hz)

    Returns:
        AudioSignal: ADSRエンベロープデータ
    """
    if gate_time is None:
        gate_time = max(0, duration - release)

    num_samples = int(sample_rate * duration)
    envelope = np.zeros(num_samples)

    attack_samples = int(sample_rate * attack)
    decay_samples = int(sample_rate * decay)
    gate_samples = int(sample_rate * gate_time)
    release_samples = int(sample_rate * release)

    # アタック段階
    attack_end = min(attack_samples, num_samples)
    if attack_samples > 0:
        for n in range(attack_end):
            envelope[n] = (1 - np.exp(-5 * n / attack_samples)) / (1 - np.exp(-5))

    # ディケイ段階
    decay_start = attack_end
    decay_end = min(decay_start + decay_samples, gate_samples, num_samples)
    if decay_samples > 0 and decay_end > decay_start:
        for n in range(decay_start, decay_end):
            progress = (n - decay_start) / decay_samples
            envelope[n] = 1.0 + (sustain - 1.0) * (1 - np.exp(-5 * progress))

    # サステイン段階
    sustain_start = decay_end
    sustain_end = min(gate_samples, num_samples)
    if sustain_end > sustain_start:
        envelope[sustain_start:sustain_end] = sustain

    # リリース段階
    release_start = min(gate_samples, num_samples)
    release_end = min(release_start + release_samples, num_samples)
    if release_samples > 0 and release_end > release_start:
        initial_level = sustain if release_start < len(envelope) else envelope[release_start - 1]
        for n in range(release_start, release_end):
            progress = (n - release_start) / release_samples
            envelope[n] = initial_level * np.exp(-5 * progress)

    return AudioSignal(envelope, sample_rate)


def linear_envelope(
    duration: float,
    fade_in: float = 0.01,
    fade_out: float = 0.01,
    sample_rate: int = 44100,
) -> AudioSignal:
    """リニア（直線的）エンベロープを生成

    Args:
        duration: 継続時間 (秒)
        fade_in: フェードイン時間 (秒)
        fade_out: フェードアウト時間 (秒)
        sample_rate: サンプリングレート (Hz)

    Returns:
        AudioSignal: リニアエンベロープデータ
    """
    num_samples = int(sample_rate * duration)
    envelope = np.ones(num_samples)

    fade_in_samples = int(sample_rate * fade_in)
    fade_out_samples = int(sample_rate * fade_out)

    # フェードイン
    fade_in_end = min(fade_in_samples, num_samples)
    if fade_in_samples > 0:
        envelope[:fade_in_end] = np.linspace(0, 1, fade_in_end)

    # フェードアウト
    fade_out_start = max(0, num_samples - fade_out_samples)
    if fade_out_samples > 0 and fade_out_start < num_samples:
        envelope[fade_out_start:] = np.linspace(1, 0, num_samples - fade_out_start)

    return AudioSignal(envelope, sample_rate)


def cosine_envelope(
    duration: float,
    attack: float = 0.1,
    release: float = 0.1,
    sustain_level: float = 1.0,
    sample_rate: int = 44100,
) -> AudioSignal:
    """コサイン型エンベロープを生成（滑らかな変化）

    Args:
        duration: 継続時間 (秒)
        attack: アタック時間 (秒)
        release: リリース時間 (秒)
        sustain_level: サステインレベル (0.0-1.0)
        sample_rate: サンプリングレート (Hz)

    Returns:
        AudioSignal: コサインエンベロープデータ
    """
    num_samples = int(sample_rate * duration)
    envelope = np.ones(num_samples) * sustain_level

    attack_samples = int(sample_rate * attack)
    release_samples = int(sample_rate * release)

    # アタック（コサインカーブ）
    attack_end = min(attack_samples, num_samples)
    if attack_samples > 0:
        for n in range(attack_end):
            progress = n / attack_samples
            envelope[n] = sustain_level * (0.5 - 0.5 * np.cos(np.pi * progress))

    # リリース（コサインカーブ）
    release_start = max(0, num_samples - release_samples)
    if release_samples > 0 and release_start < num_samples:
        for n in range(release_start, num_samples):
            progress = (n - release_start) / release_samples
            envelope[n] = sustain_level * (0.5 + 0.5 * np.cos(np.pi * progress))

    return AudioSignal(envelope, sample_rate)
