"""
audio_lib の API 仕様書を docstring から自動生成するスクリプト

使い方:
  python scripts/generate_api_docs.py

出力先: docs/api_reference.md
"""

import inspect
import importlib
import os
import sys

# audio_lib のパスを通す
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 出力先
OUTPUT_DIR = "docs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "api_reference.md")

# スキャン対象のモジュールと表示名
MODULES = [
    ("audio_lib.core.audio_signal", "Core: AudioSignal", ["AudioSignal", "save_audio", "load_audio"]),
    ("audio_lib.synthesis.oscillators", "波形生成 (Oscillators)", [
        "sine_wave", "sawtooth_wave", "square_wave", "triangle_wave",
        "additive_synth", "white_noise", "pink_noise",
    ]),
    ("audio_lib.synthesis.envelopes", "エンベロープ (Envelopes)", [
        "adsr", "linear_envelope", "cosine_envelope",
    ]),
    ("audio_lib.synthesis.note_utils", "音程ユーティリティ (Note Utils)", [
        "note_to_frequency", "frequency_to_note", "note_name_to_number",
        "number_to_note_name", "create_scale",
    ]),
    ("audio_lib.effects.filters", "フィルター (Filters)", [
        "LowPassFilter", "HighPassFilter", "BandPassFilter",
    ]),
    ("audio_lib.effects.audio_effects", "エフェクト (Effects)", [
        "Reverb", "Distortion", "Delay", "Chorus", "Compressor",
    ]),
    ("audio_lib.instruments.basic_instruments", "楽器 (Instruments)", [
        "SimpleSynthesizer", "BasicPiano", "BasicOrgan", "BasicGuitar", "BasicDrum",
    ]),
    ("audio_lib.sequencer", "シーケンサー (Sequencer)", [
        "Note", "Track", "Sequencer", "create_simple_melody", "create_chord",
    ]),
    ("audio_lib.notebook", "ノートブック用ヘルパー (Notebook)", [
        "setup_environment", "play_sound", "plot_waveform", "plot_spectrum",
        "plot_harmonics", "apply_effect",
    ]),
]


def format_signature(obj):
    """関数・メソッドのシグネチャを取得"""
    try:
        sig = inspect.signature(obj)
        return str(sig)
    except (ValueError, TypeError):
        return "()"


def format_docstring(obj, indent=""):
    """docstring を整形して返す"""
    doc = inspect.getdoc(obj)
    if not doc:
        return f"{indent}*(docstring なし)*\n"
    lines = doc.split("\n")
    result = []
    for line in lines:
        result.append(f"{indent}{line}")
    return "\n".join(result) + "\n"


def document_class(cls, name):
    """クラスのドキュメントを生成"""
    lines = []
    lines.append(f"### `{name}`\n")

    # クラスの docstring
    doc = inspect.getdoc(cls)
    if doc:
        lines.append(f"{doc}\n")

    # __init__ のシグネチャ
    init = getattr(cls, "__init__", None)
    if init and init is not object.__init__:
        sig = format_signature(init)
        lines.append(f"```python\n{name}{sig}\n```\n")
        init_doc = inspect.getdoc(init)
        if init_doc:
            lines.append(f"{init_doc}\n")

    # 主要な公開メソッド
    methods = []
    for method_name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if method_name.startswith("_"):
            continue
        methods.append((method_name, method))

    if methods:
        lines.append("**メソッド:**\n")
        for method_name, method in methods:
            sig = format_signature(method)
            doc = inspect.getdoc(method)
            summary = doc.split("\n")[0] if doc else ""
            lines.append(f"- `{method_name}{sig}` — {summary}")
        lines.append("")

    return "\n".join(lines)


def document_function(func, name):
    """関数のドキュメントを生成"""
    lines = []
    sig = format_signature(func)
    lines.append(f"### `{name}{sig}`\n")

    doc = inspect.getdoc(func)
    if doc:
        lines.append(f"{doc}\n")

    return "\n".join(lines)


def generate():
    """API 仕様書を生成"""
    output = []
    output.append("# audio_lib API リファレンス\n")
    output.append("*このドキュメントは `scripts/generate_api_docs.py` により docstring から自動生成されています。*\n")
    output.append("---\n")

    for module_path, section_title, names in MODULES:
        try:
            mod = importlib.import_module(module_path)
        except ImportError as e:
            output.append(f"## {section_title}\n")
            output.append(f"*インポートエラー: {e}*\n")
            continue

        output.append(f"## {section_title}\n")
        output.append(f"`{module_path}`\n")

        for name in names:
            obj = getattr(mod, name, None)
            if obj is None:
                output.append(f"### `{name}`\n")
                output.append(f"*未定義*\n")
                continue

            if inspect.isclass(obj):
                output.append(document_class(obj, name))
            elif callable(obj):
                output.append(document_function(obj, name))
            else:
                output.append(f"### `{name}`\n")
                output.append(f"*ドキュメント化対象外*\n")

        output.append("---\n")

    return "\n".join(output)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    content = generate()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"API 仕様書を生成しました → {OUTPUT_FILE}")
