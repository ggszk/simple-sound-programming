"""
examples/ スクリプトの実行テスト

ライブラリAPIとexamplesの整合性を検証します。
一時ディレクトリで実行し、生成ファイルが残らないようにします。
"""

import matplotlib
matplotlib.use("Agg")  # plt.show() がブロックしないよう非インタラクティブバックエンドを使用

import pytest


@pytest.fixture()
def run_in_tmpdir(monkeypatch, tmp_path):
    """一時ディレクトリで実行"""
    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestExamples:
    """examples/ の各スクリプトがエラーなく実行できることを検証"""

    def test_basic_examples(self, run_in_tmpdir):
        from examples.basic_examples import main
        main()

    def test_educational_tutorial(self, run_in_tmpdir):
        pytest.importorskip("matplotlib")
        from examples.educational_tutorial import main
        main()

    def test_debug_oscillators(self, run_in_tmpdir):
        pytest.importorskip("matplotlib")
        from examples.debug_oscillators import (
            debug_sine_wave, debug_sawtooth_wave, debug_square_wave, compare_waveforms,
        )
        debug_sine_wave()
        debug_sawtooth_wave()
        debug_square_wave()
        compare_waveforms()

    def test_debug_envelopes(self, run_in_tmpdir):
        pytest.importorskip("matplotlib")
        from examples.debug_envelopes import (
            debug_adsr_envelope, debug_linear_envelope, debug_envelope_application, visualize_envelopes,
        )
        debug_adsr_envelope()
        debug_linear_envelope()
        debug_envelope_application()
        visualize_envelopes()

    def test_debug_instruments(self, run_in_tmpdir):
        from examples.debug_instruments import (
            debug_piano, debug_guitar, debug_drum, debug_sequencer, debug_note_utilities,
        )
        debug_note_utilities()
        debug_piano()
        debug_guitar()
        debug_drum()
        debug_sequencer()
