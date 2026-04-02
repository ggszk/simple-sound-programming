"""
audio_lib パッケージの包括的テスト

主要機能の動作を検証します。
"""

import numpy as np
import pytest
import tempfile
import os
from audio_lib import (
    AudioSignal, sine_wave, square_wave, sawtooth_wave,
    adsr, linear_envelope,
    save_audio, load_audio,
    note_to_frequency, frequency_to_note, note_name_to_number,
    LowPassFilter, HighPassFilter,
    Reverb, Distortion, Delay, Chorus, Compressor,
)


class TestAudioSignal:
    """AudioSignal クラスのテスト"""

    def test_basic_properties(self):
        """基本プロパティのテスト"""
        data = np.zeros(44100)
        signal = AudioSignal(data, 44100)
        assert signal.sample_rate == 44100
        assert signal.num_samples == 44100
        assert abs(signal.duration - 1.0) < 0.001

    def test_arithmetic_operations(self):
        """算術演算のテスト"""
        s1 = sine_wave(440, 1.0)
        s2 = sine_wave(880, 1.0)

        # 加算
        mixed = s1 + s2
        assert isinstance(mixed, AudioSignal)
        assert mixed.num_samples == s1.num_samples

        # スカラー乗算
        scaled = s1 * 0.5
        assert np.max(np.abs(scaled.data)) < np.max(np.abs(s1.data)) + 0.01

        # AudioSignal同士の乗算（エンベロープ適用）
        env = adsr(1.0)
        shaped = s1 * env
        assert isinstance(shaped, AudioSignal)

    def test_sample_rate_mismatch(self):
        """sample_rate不一致時のエラー"""
        s1 = sine_wave(440, 1.0, sample_rate=44100)
        s2 = sine_wave(440, 1.0, sample_rate=48000)
        with pytest.raises(ValueError):
            s1 + s2


class TestBasicOscillators:
    """基本波形生成のテスト"""

    def test_sine_wave_basic(self):
        """サイン波の基本動作テスト"""
        signal = sine_wave(440.0, 1.0)

        assert signal.num_samples == 44100
        assert -1.0 <= np.min(signal.data) <= 1.0
        assert -1.0 <= np.max(signal.data) <= 1.0
        assert np.abs(np.max(signal.data) - 1.0) < 0.1
        assert np.abs(np.min(signal.data) - (-1.0)) < 0.1

    def test_square_wave_basic(self):
        """矩形波の基本動作テスト"""
        signal = square_wave(440.0, 1.0)
        assert signal.num_samples == 44100

    def test_sawtooth_wave_basic(self):
        """ノコギリ波の基本動作テスト"""
        signal = sawtooth_wave(440.0, 1.0)
        assert signal.num_samples == 44100


class TestEnvelopes:
    """エンベロープのテスト"""

    def test_linear_envelope(self):
        """リニアエンベロープのテスト"""
        env = linear_envelope(2.0, fade_in=0.1, fade_out=0.1)

        assert env.num_samples == int(44100 * 2.0)
        assert env.data[0] == 0.0
        assert env.data[-1] == 0.0
        assert np.max(env.data) <= 1.0

    def test_adsr_envelope(self):
        """ADSRエンベロープのテスト"""
        env = adsr(2.0, attack=0.1, decay=0.2, sustain=0.7, release=0.3)

        assert env.num_samples == int(44100 * 2.0)
        assert 0.0 <= np.min(env.data)
        assert np.max(env.data) <= 1.0
        assert env.data[0] == 0.0

    def test_envelope_application(self):
        """エンベロープ適用のテスト"""
        signal = sine_wave(440.0, 2.0)
        env = adsr(2.0, attack=0.1, decay=0.2, sustain=0.5, release=0.3)

        processed = signal * env
        assert processed.num_samples == signal.num_samples
        assert np.max(np.abs(processed.data)) <= np.max(np.abs(signal.data))


class TestNoteUtils:
    """音名・周波数変換のテスト"""

    def test_note_to_frequency(self):
        assert abs(note_to_frequency(69) - 440.0) < 0.1
        assert abs(note_to_frequency(60) - 261.63) < 0.1

    def test_frequency_to_note(self):
        assert frequency_to_note(440.0) == 69
        assert frequency_to_note(261.63) == 60

    def test_note_name_to_number(self):
        assert note_name_to_number("A4") == 69
        assert note_name_to_number("C4") == 60
        assert note_name_to_number("C5") == 72


class TestAudioEffects:
    """オーディオエフェクトのテスト"""

    def setup_method(self):
        self.test_signal = sine_wave(440.0, 1.0)

    def test_compression(self):
        """コンプレッション効果のテスト"""
        comp = Compressor(threshold=0.5, ratio=4.0)
        compressed = comp.process(self.test_signal)

        assert compressed.num_samples == self.test_signal.num_samples
        assert np.max(np.abs(compressed.data)) <= np.max(np.abs(self.test_signal.data))

    def test_low_pass_filter(self):
        lpf = LowPassFilter(cutoff_freq=1000)
        filtered = lpf.process(self.test_signal)
        assert filtered.num_samples == self.test_signal.num_samples

    def test_high_pass_filter(self):
        hpf = HighPassFilter(cutoff_freq=1000)
        filtered = hpf.process(self.test_signal)
        assert filtered.num_samples == self.test_signal.num_samples

    def test_reverb_effect(self):
        reverb = Reverb(room_size=0.7, damping=0.5)
        processed = reverb.process(self.test_signal)
        assert processed.num_samples == self.test_signal.num_samples

    def test_delay_effect(self):
        delay = Delay(delay_time=0.3, feedback=0.4, wet_level=0.3)
        processed = delay.process(self.test_signal)
        assert processed.num_samples == self.test_signal.num_samples

    def test_chorus_effect(self):
        chorus = Chorus(rate=1.5, depth=0.005, wet_level=0.5)
        processed = chorus.process(self.test_signal)
        assert processed.num_samples == self.test_signal.num_samples

    def test_distortion_effect(self):
        distortion = Distortion(gain=10.0, output_level=0.7)
        processed = distortion.process(self.test_signal)
        assert processed.num_samples == self.test_signal.num_samples


class TestAudioFileIO:
    """音声ファイル入出力のテスト"""

    def test_save_and_load(self):
        """保存と読み込みのテスト"""
        signal = sine_wave(440.0, 1.0)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            temp_filename = tmp.name

        try:
            signal.save(temp_filename)
            assert os.path.exists(temp_filename)
            assert os.path.getsize(temp_filename) > 0

            loaded = load_audio(temp_filename)
            assert loaded.sample_rate == 44100
            assert loaded.num_samples == signal.num_samples
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_save_audio_function(self):
        """save_audio関数のテスト"""
        signal = sine_wave(440.0, 1.0)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            temp_filename = tmp.name

        try:
            save_audio(temp_filename, signal)
            assert os.path.exists(temp_filename)
            assert os.path.getsize(temp_filename) > 0
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)


class TestEducationalScenarios:
    """教育シナリオのテスト"""

    def test_lesson01_basic_sine_wave(self):
        """Lesson 1: 基本サイン波生成"""
        signal = sine_wave(frequency=440.0, duration=1.0)

        assert signal.num_samples == 44100
        assert np.abs(np.max(signal.data) - 1.0) < 0.1
        assert np.abs(np.min(signal.data) - (-1.0)) < 0.1

    def test_lesson02_envelope_application(self):
        """Lesson 2: エンベロープ適用"""
        signal = sine_wave(440.0, 2.0)
        envelope = adsr(2.0, attack=0.1, decay=0.2, sustain=0.7, release=0.3)
        processed = signal * envelope

        assert processed.num_samples == signal.num_samples
        assert processed.data[0] == 0.0
        assert np.abs(processed.data[-1]) < 0.1

    def test_melody_generation(self):
        """メロディー生成のテスト"""
        melody_notes = [("C4", 0.5), ("C4", 0.5), ("G4", 0.5), ("G4", 0.5)]
        melody_data = []

        for note_name, note_duration in melody_notes:
            midi_number = note_name_to_number(note_name)
            frequency = note_to_frequency(midi_number)
            signal = sine_wave(frequency, note_duration)
            envelope = adsr(note_duration, attack=0.01, decay=0.2, sustain=0.4, release=0.3)
            note_with_envelope = signal * envelope
            melody_data.append(note_with_envelope.data)

        full_melody = np.concatenate(melody_data)
        expected_total_duration = sum(d for _, d in melody_notes)
        expected_samples = int(44100 * expected_total_duration)
        assert len(full_melody) == expected_samples


def test_integration_all_components():
    """全コンポーネントの統合テスト"""
    # 1. 波形生成
    signal = sine_wave(440.0, 1.0)

    # 2. エンベロープ
    envelope = adsr(1.0, attack=0.1, decay=0.2, sustain=0.5, release=0.3)
    signal_with_envelope = signal * envelope

    # 3. エフェクト
    reverb = Reverb(room_size=0.7, damping=0.5)
    final_signal = reverb.process(signal_with_envelope)

    # 4. ファイル保存
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        temp_filename = tmp.name

    try:
        final_signal.save(temp_filename)
        assert os.path.exists(temp_filename)
        assert os.path.getsize(temp_filename) > 0
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
