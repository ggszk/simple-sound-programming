"""
ノートブック教材の動作確認テスト

各レッスンノートブックで使用される機能が正しく動作することを確認します。
"""

import numpy as np
import pytest
import tempfile
import os
from audio_lib import (
    sine_wave, sawtooth_wave,
    adsr, linear_envelope,
    note_to_frequency, note_name_to_number,
    LowPassFilter, HighPassFilter,
    Reverb, Delay, Chorus, Distortion, Compressor,
)


class TestLesson01BasicsAndSineWaves:
    """Lesson 1: サイン波と基礎"""

    def test_basic_sine_wave_generation(self):
        """基本的なサイン波生成"""
        signal = sine_wave(frequency=440.0, duration=1.0)

        assert signal.num_samples == 44100
        assert signal.sample_rate == 44100
        assert abs(np.max(signal.data) - 1.0) < 0.1
        assert abs(np.min(signal.data) - (-1.0)) < 0.1

    def test_different_frequencies(self):
        """異なる周波数での音生成テスト"""
        for freq in [220, 440, 880, 1760]:
            signal = sine_wave(freq, 1.0)
            assert signal.num_samples == 44100
            assert -1.0 <= np.min(signal.data) <= 1.0

    def test_volume_variations(self):
        """音量変化のテスト"""
        for volume in [0.1, 0.3, 1.0, 0.8]:
            signal = sine_wave(440.0, 1.0)
            signal_with_volume = signal * volume
            max_amplitude = np.max(np.abs(signal_with_volume.data))
            assert abs(max_amplitude - volume) < 0.1

    def test_note_frequency_conversion(self):
        """音名と周波数の変換テスト"""
        note_table = {
            "C4": 60, "D4": 62, "E4": 64, "F4": 65,
            "G4": 67, "A4": 69, "B4": 71, "C5": 72,
        }
        for note_name, expected_midi in note_table.items():
            midi_number = note_name_to_number(note_name)
            assert midi_number == expected_midi

    def test_melody_generation(self):
        """ドレミファソラシド メロディー生成テスト"""
        melody_notes = [
            ("C4", 0.5), ("D4", 0.5), ("E4", 0.5), ("F4", 0.5),
            ("G4", 0.5), ("A4", 0.5), ("B4", 0.5), ("C5", 0.5),
        ]

        melody_data = []
        for note_name, note_duration in melody_notes:
            midi_number = note_name_to_number(note_name)
            frequency = note_to_frequency(midi_number)
            signal = sine_wave(frequency, note_duration)
            melody_data.append(signal.data)

        full_melody = np.concatenate(melody_data)
        expected_length = int(44100 * 4.0)
        assert len(full_melody) == expected_length

    def test_harmony_generation(self):
        """和音生成テスト"""
        signal1 = sine_wave(440, 2.0)
        signal2 = sine_wave(554, 2.0)
        harmony = signal1 + signal2

        assert harmony.num_samples == signal1.num_samples


class TestLesson02EnvelopesAndADSR:
    """Lesson 2: エンベロープとADSR"""

    def test_raw_signal_click_problem(self):
        """クリック音問題の確認"""
        raw_signal = sine_wave(440, 1.0)
        assert abs(raw_signal.data[0]) == 0.0
        assert abs(raw_signal.data[-1]) > 0.01

    def test_linear_envelope(self):
        """リニアエンベロープのテスト"""
        env = linear_envelope(duration=1.0, fade_in=0.1, fade_out=0.1)

        assert env.data[0] == 0.0
        assert env.data[-1] == 0.0
        assert np.max(env.data) <= 1.0

    def test_adsr_envelope_basic(self):
        """基本ADSRエンベロープのテスト"""
        env = adsr(duration=2.0, attack=0.1, decay=0.2, sustain=0.7, release=0.5)

        assert env.num_samples == int(44100 * 2.0)
        assert env.data[0] == 0.0
        assert np.max(env.data) <= 1.0

    def test_envelope_application(self):
        """エンベロープ適用のテスト"""
        signal = sine_wave(440, 2.0)
        envelope = adsr(2.0, attack=0.1, decay=0.2, sustain=0.7, release=0.5)
        processed = signal * envelope

        assert processed.num_samples == signal.num_samples
        assert np.max(np.abs(processed.data)) <= np.max(np.abs(signal.data))

    def test_instrument_simulation(self):
        """楽器シミュレーションのテスト"""
        duration = 3.0
        signal = sine_wave(440, duration)

        piano_env = adsr(duration, attack=0.01, decay=0.3, sustain=0.3, release=1.5)
        piano_sound = signal * piano_env

        organ_env = adsr(duration, attack=0.05, decay=0.0, sustain=1.0, release=0.1)
        organ_sound = signal * organ_env

        string_env = adsr(duration, attack=0.3, decay=0.1, sustain=0.8, release=0.4)
        string_sound = signal * string_env

        assert not np.array_equal(piano_sound.data, organ_sound.data)
        assert not np.array_equal(piano_sound.data, string_sound.data)

    def test_twinkle_star_melody(self):
        """きらきら星メロディーのテスト"""
        melody_notes = [
            ("C4", 0.5), ("C4", 0.5), ("G4", 0.5), ("G4", 0.5),
            ("A4", 0.5), ("A4", 0.5), ("G4", 1.0),
            ("F4", 0.5), ("F4", 0.5), ("E4", 0.5), ("E4", 0.5),
            ("D4", 0.5), ("D4", 0.5), ("C4", 1.0),
        ]

        melody_audio_data = []
        for note_name, note_duration in melody_notes:
            midi_number = note_name_to_number(note_name)
            frequency = note_to_frequency(midi_number)
            note_signal = sine_wave(frequency, note_duration)
            envelope = adsr(note_duration, attack=0.01, decay=0.2, sustain=0.4, release=0.3)
            note_with_envelope = note_signal * envelope
            melody_audio_data.append(note_with_envelope.data)

        full_melody = np.concatenate(melody_audio_data)
        total_duration = sum(d for _, d in melody_notes)
        expected_samples = int(44100 * total_duration)
        assert len(full_melody) == expected_samples


class TestLesson03FiltersAndSoundDesign:
    """Lesson 3: フィルターと音響設計"""

    def test_low_pass_filter(self):
        signal = sawtooth_wave(440, 1.0)
        lpf = LowPassFilter(cutoff_freq=1000)
        filtered = lpf.process(signal)
        assert filtered.num_samples == signal.num_samples

    def test_high_pass_filter(self):
        signal = sawtooth_wave(440, 1.0)
        hpf = HighPassFilter(cutoff_freq=1000)
        filtered = hpf.process(signal)
        assert filtered.num_samples == signal.num_samples


class TestLesson04AudioEffectsAndDynamics:
    """Lesson 4: オーディオエフェクトとダイナミクス"""

    def setup_method(self):
        self.test_signal = sine_wave(440, 1.0)

    def test_compression_effect(self):
        comp = Compressor(threshold=0.5, ratio=4.0)
        compressed = comp.process(self.test_signal)
        assert compressed.num_samples == self.test_signal.num_samples

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


def test_complete_educational_workflow():
    """完全な教育ワークフローのテスト"""
    # 1. 波形生成 (Lesson 1)
    signal = sine_wave(440.0, 2.0)

    # 2. エンベロープ (Lesson 2)
    envelope = adsr(2.0, attack=0.1, decay=0.2, sustain=0.6, release=0.4)
    shaped = signal * envelope

    # 3. フィルター (Lesson 3)
    lpf = LowPassFilter(cutoff_freq=2000)
    filtered = lpf.process(shaped)

    # 4. エフェクト (Lesson 4)
    reverb = Reverb(room_size=0.5, damping=0.4)
    final = reverb.process(filtered)

    # 5. ファイル保存
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        temp_filename = tmp.name

    try:
        final.save(temp_filename)
        assert os.path.exists(temp_filename)
        assert os.path.getsize(temp_filename) > 0
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
