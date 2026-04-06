"""
波形生成関数のテスト

基本的な波形生成の動作を検証します。
"""

import numpy as np
import pytest
from audio_lib import sine_wave, square_wave, sawtooth_wave, triangle_wave


class TestSineWave:
    """サイン波のテスト"""

    def test_sine_wave_generation(self):
        """基本的なサイン波生成のテスト"""
        frequency = 440.0
        duration = 1.0
        sample_rate = 44100

        signal = sine_wave(frequency, duration, sample_rate=sample_rate)

        assert signal.num_samples == int(sample_rate * duration)
        assert signal.sample_rate == sample_rate
        assert -1.0 <= signal.data.min()
        assert signal.data.max() <= 1.0
        assert np.abs(signal.data.max() - 1.0) < 0.1
        assert np.abs(signal.data.min() - (-1.0)) < 0.1

    def test_frequency_accuracy(self):
        """周波数の正確性をテスト"""
        frequency = 1000.0
        duration = 1.0
        sample_rate = 44100

        signal = sine_wave(frequency, duration, sample_rate=sample_rate)

        fft_result = np.fft.fft(signal.data)
        freqs = np.fft.fftfreq(len(signal.data), 1 / sample_rate)
        positive_freqs = freqs[: len(freqs) // 2]
        magnitude = np.abs(fft_result[: len(fft_result) // 2])

        peak_freq_index = np.argmax(magnitude)
        detected_frequency = positive_freqs[peak_freq_index]

        assert abs(detected_frequency - frequency) < 5.0

    def test_amplitude_parameter(self):
        """振幅パラメータのテスト"""
        amplitude = 0.5
        signal = sine_wave(440.0, 0.1)
        scaled = signal * amplitude

        max_amplitude = np.max(np.abs(scaled.data))
        assert abs(max_amplitude - amplitude) < 0.1


class TestSquareWave:
    """矩形波のテスト"""

    def test_square_wave_generation(self):
        """基本的な矩形波生成のテスト（帯域制限付き加算合成）"""
        signal = square_wave(frequency=440.0, duration=0.1)
        # 加算合成ではギブス現象でわずかにオーバーシュートするが、
        # おおむね ±1 の範囲に収まる
        assert signal.data.max() < 1.2
        assert signal.data.min() > -1.2

    def test_duty_cycle(self):
        """デューティサイクルのテスト（帯域制限付き加算合成）"""
        duty = 0.25
        signal = square_wave(frequency=100.0, duration=1.0, duty_cycle=duty)

        # DC成分が 2d - 1 = -0.5 に近いことを確認
        expected_dc = 2.0 * duty - 1.0
        actual_dc = np.mean(signal.data)
        assert abs(actual_dc - expected_dc) < 0.05


class TestWaveformComparison:
    """波形間の比較テスト"""

    def test_different_waveforms(self):
        """異なる波形の特性比較"""
        frequency = 440.0
        duration = 0.1

        sine = sine_wave(frequency, duration)
        square = square_wave(frequency, duration)
        sawtooth = sawtooth_wave(frequency, duration)
        triangle = triangle_wave(frequency, duration)

        length = sine.num_samples
        assert square.num_samples == length
        assert sawtooth.num_samples == length
        assert triangle.num_samples == length

        assert not np.array_equal(sine.data, square.data)
        assert not np.array_equal(sine.data, sawtooth.data)
        assert not np.array_equal(square.data, triangle.data)

    def test_harmonic_content(self):
        """高調波成分の比較テスト"""
        frequency = 440.0
        duration = 1.0
        sample_rate = 44100

        sine = sine_wave(frequency, duration, sample_rate=sample_rate)
        square = square_wave(frequency, duration, sample_rate=sample_rate)

        sine_fft = np.abs(np.fft.fft(sine.data))
        square_fft = np.abs(np.fft.fft(square.data))

        fundamental_bin = int(frequency * sine.num_samples / sample_rate)
        sine_harmonics = np.sum(sine_fft[fundamental_bin * 2 : fundamental_bin * 10])
        square_harmonics = np.sum(square_fft[fundamental_bin * 2 : fundamental_bin * 10])

        assert square_harmonics > sine_harmonics


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
