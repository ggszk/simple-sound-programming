"""レッスン05: オーディオエフェクトとダイナミクス — ノートブック生成スクリプト

実行方法:
    uv run python scripts/generate_lesson05.py

出力:
    colab_lessons/lesson_05_audio_effects_and_dynamics.ipynb
"""

import nbformat

OUTPUT_PATH = "colab_lessons/lesson_05_audio_effects_and_dynamics.ipynb"


def md(source: str) -> nbformat.NotebookNode:
    return nbformat.v4.new_markdown_cell(source)


def code(source: str) -> nbformat.NotebookNode:
    return nbformat.v4.new_code_cell(source)


# ============================================================
# セル定義
# ============================================================

cells: list[nbformat.NotebookNode] = []

# ----------------------------------------------------------
# タイトル
# ----------------------------------------------------------
cells.append(md("""\
# 音のプログラミング 第5回: オーディオエフェクトとダイナミクス

**前回まで学んだこと：**
- 基本的な音響合成（発振器、エンベロープ）
- フィルターによる音色デザイン
- 楽器音の作成

**今回の学習目標:**
- **リバーブ**（残響）で音に空間的な広がりを与える
- **ディレイ**（遅延）でエコー効果を作る
- **コーラス**で音を豊かにする
- **ダイナミクス**（音量制御）の基本

**構成:**
- **前半（体験）：** プロ品質のエフェクト（pedalboard）で「エフェクトとはどういう音か」を体感
- **後半（仕組み）：** シンプルな自前実装でアルゴリズムの原理を理解

**所要時間:** 90分"""))

# ----------------------------------------------------------
# セットアップ
# ----------------------------------------------------------
cells.append(md("## セットアップ"))

cells.append(code("""\
import sys
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display
import warnings
warnings.filterwarnings('ignore')

try:
    import google.colab
    IN_COLAB = True
    print("Google Colab環境で実行中...")
except ImportError:
    IN_COLAB = False
    print("ローカル環境で実行中")

if IN_COLAB:
    print("Google Colab環境を設定中...")
    !pip install japanize-matplotlib pedalboard
    !git clone https://github.com/ggszk/simple-audio-programming.git
    sys.path.append('/content/simple-audio-programming')
    import japanize_matplotlib
else:
    print("ローカル環境を設定中...")
    sys.path.append('..')
    import platform
    if platform.system() == 'Darwin':
        plt.rcParams['font.family'] = 'Hiragino Sans'
    else:
        plt.rcParams['font.family'] = 'Meiryo'

print("セットアップ完了")"""))

cells.append(code("""\
from audio_lib import sine_wave, sawtooth_wave, adsr, AudioSignal
from audio_lib.synthesis.note_utils import note_to_frequency, note_name_to_number
from audio_lib.notebook import play_sound, apply_effect

from pedalboard import Reverb, Delay, Chorus, Compressor"""))

# ----------------------------------------------------------
# 準備: テスト用ピアノ音
# ----------------------------------------------------------
cells.append(md("""\
## 準備: テスト用ピアノ音

前回学んだ技法で、エフェクトのテスト用ピアノ音を作ります。"""))

cells.append(code("""\
def create_simple_piano(note_freq, duration=2.0):
    \"\"\"シンプルなピアノ音\"\"\"
    signal = sine_wave(note_freq, duration)
    envelope = adsr(duration, attack=0.01, decay=0.3, sustain=0.4, release=1.5)
    return signal * envelope"""))

# ==========================================================
# 前半: 体験パート（pedalboard）
# ==========================================================
cells.append(md("""\
---
# 前半: エフェクトを体験する（pedalboard）

まずはプロ品質のエフェクトで「どういう音になるか」を体感しましょう。
ここでは Spotify が開発した **pedalboard** ライブラリを使います。"""))

# --- リバーブ体験 ---
cells.append(md("""\
## 実習1: リバーブ（残響）— 音に空間を与える

リバーブは部屋や空間での音の反響をシミュレートする効果です。

- **コンサートホール**：長い残響
- **小さな部屋**：短い残響
- **屋外**：ほぼ残響なし"""))

cells.append(code("""\
# ドライ音（エフェクトなし）
dry_piano = create_simple_piano(note_to_frequency(note_name_to_number('C4')))
display(play_sound(dry_piano, "ドライ音（リバーブなし）"))

# リバーブあり
reverb = Reverb(room_size=0.8, damping=0.5, wet_level=0.3)
wet_piano = apply_effect(dry_piano, reverb)
display(play_sound(wet_piano, "リバーブあり（大きな部屋）"))"""))

cells.append(md("""\
### 聞き比べてみよう
- ドライ音：直接的で近い感じ
- リバーブあり：空間的で遠い感じ、音の尻尾が長い"""))

cells.append(md("""\
### リバーブパラメータの効果

| パラメータ | 範囲 | 効果 |
|-----------|------|------|
| **room_size** | 0.0〜1.0 | 部屋の大きさ（小部屋〜大ホール） |
| **damping** | 0.0〜1.0 | 高域の減衰（低い=明るい残響、高い=暗い残響） |
| **wet_level** | 0.0〜1.0 | エフェクト音の量（控えめ〜しっかり） |"""))

cells.append(code("""\
# 異なるリバーブ設定を比較
base_sound = create_simple_piano(note_to_frequency(note_name_to_number('A4')), 1.5)

settings = [
    ("小さな部屋",     Reverb(room_size=0.3, damping=0.8, wet_level=0.3)),
    ("コンサートホール", Reverb(room_size=0.7, damping=0.4, wet_level=0.5)),
    ("大きなホール",    Reverb(room_size=0.9, damping=0.2, wet_level=0.7)),
]

for name, reverb in settings:
    processed = apply_effect(base_sound, reverb)
    display(play_sound(processed, name))"""))

# --- ディレイ体験 ---
cells.append(md("""\
## 実習2: ディレイ（遅延）— エコー効果を作る

ディレイは音を一定時間遅らせて元の音に重ねる効果です。

- **短いディレイ**：音の厚みや広がり
- **長いディレイ**：明確なエコー効果
- **フィードバック**：エコーの繰り返し"""))

cells.append(code("""\
base_sound = create_simple_piano(note_to_frequency(note_name_to_number('E4')), 1.0)

display(play_sound(base_sound, "元の音"))

# 短いディレイ（音の厚み）
display(play_sound(
    apply_effect(base_sound, Delay(delay_seconds=0.1, feedback=0.3, mix=0.4)),
    "短いディレイ（0.1秒）"))

# 長いディレイ（明確なエコー）
display(play_sound(
    apply_effect(base_sound, Delay(delay_seconds=0.5, feedback=0.4, mix=0.5)),
    "長いディレイ（0.5秒）"))

# フィードバック多め（エコーの繰り返し）
display(play_sound(
    apply_effect(base_sound, Delay(delay_seconds=0.3, feedback=0.6, mix=0.4)),
    "フィードバック多め（エコーの繰り返し）"))"""))

# --- コーラス体験 ---
cells.append(md("""\
## 実習3: コーラス — 音を豊かにする

コーラスは音を少しずつピッチや時間をずらしてコピーし、重ね合わせる効果です。

| パラメータ | 効果 |
|-----------|------|
| **depth** | 変調の深さ（大きいほど揺れが大きい） |
| **rate_hz** | 変調の速度 (Hz) |
| **mix** | エフェクト音の量 |"""))

cells.append(code("""\
base_sound = create_simple_piano(note_to_frequency(note_name_to_number('G4')), 2.0)

display(play_sound(base_sound, "元の音"))

# 軽いコーラス（自然な広がり）
display(play_sound(
    apply_effect(base_sound, Chorus(rate_hz=2.0, depth=0.25, mix=0.4)),
    "軽いコーラス"))

# 深いコーラス（しっかりとした効果）
display(play_sound(
    apply_effect(base_sound, Chorus(rate_hz=1.5, depth=0.5, mix=0.6)),
    "深いコーラス"))

# 速いコーラス（ビブラート的）
display(play_sound(
    apply_effect(base_sound, Chorus(rate_hz=5.0, depth=0.15, mix=0.5)),
    "速いコーラス（ビブラート的）"))"""))

# --- エフェクトチェーン体験 ---
cells.append(md("""\
## 実習4: エフェクトの組み合わせ — プロフェッショナルな音作り

pedalboard では複数エフェクトをリストで渡すだけでチェーンを構築できます。"""))

cells.append(code("""\
from pedalboard import Pedalboard

dry_sound = create_simple_piano(note_to_frequency(note_name_to_number('C4')), 3.0)

# エフェクトチェーン: コーラス → ディレイ → リバーブ
board = Pedalboard([
    Chorus(rate_hz=2.5, depth=0.25, mix=0.3),
    Delay(delay_seconds=0.15, feedback=0.25, mix=0.2),
    Reverb(room_size=0.6, wet_level=0.3),
])
lush_sound = apply_effect(dry_sound, board)

display(play_sound(dry_sound, "ドライなピアノ音"))
display(play_sound(lush_sound, "豊かなエフェクト付きピアノ音"))"""))

# --- ジャンル別 ---
cells.append(md("""\
## 実習5: 音楽ジャンル別のエフェクト設定"""))

cells.append(code("""\
base_melody = [
    note_to_frequency(note_name_to_number('C4')),
    note_to_frequency(note_name_to_number('E4')),
    note_to_frequency(note_name_to_number('G4')),
    note_to_frequency(note_name_to_number('C5')),
]

def create_melody(notes, note_duration=1.0):
    \"\"\"メロディを作成\"\"\"
    sounds = [create_simple_piano(freq, note_duration).data for freq in notes]
    return AudioSignal(np.concatenate(sounds), 44100)

base_sound = create_melody(base_melody, 1.5)

# クラシック: 自然なリバーブ
classic_board = Pedalboard([Reverb(room_size=0.8, wet_level=0.5)])
display(play_sound(apply_effect(base_sound, classic_board), "クラシック（リバーブ重視）"))

# ポップス: コーラスで豊かさを
pop_board = Pedalboard([
    Chorus(rate_hz=2.0, depth=0.25, mix=0.3),
    Delay(delay_seconds=0.125, feedback=0.2, mix=0.2),
])
display(play_sound(apply_effect(base_sound, pop_board), "ポップス（コーラス + ディレイ）"))

# アンビエント: 空間的な効果
ambient_board = Pedalboard([
    Reverb(room_size=0.9, wet_level=0.7),
    Delay(delay_seconds=0.5, feedback=0.6, mix=0.4),
])
display(play_sound(apply_effect(base_sound, ambient_board), "アンビエント（深いリバーブ + ディレイ）"))"""))

# --- エフェクト順序比較 ---
cells.append(md("""\
## 実習6: エフェクトの順序による違い

エフェクトは適用順序で音が大きく変わります。聞き比べてみましょう。"""))

cells.append(code("""\
base_sound = create_simple_piano(note_to_frequency(note_name_to_number('C4')), 2.0)

# チェーン1: リバーブ → ディレイ
chain1 = Pedalboard([
    Reverb(room_size=0.7, damping=0.4, wet_level=0.4),
    Delay(delay_seconds=0.3, feedback=0.3, mix=0.4),
])
display(play_sound(apply_effect(base_sound, chain1), "チェーン1（リバーブ → ディレイ）"))

# チェーン2: ディレイ → リバーブ
chain2 = Pedalboard([
    Delay(delay_seconds=0.3, feedback=0.3, mix=0.4),
    Reverb(room_size=0.7, damping=0.4, wet_level=0.4),
])
display(play_sound(apply_effect(base_sound, chain2), "チェーン2（ディレイ → リバーブ）"))"""))

cells.append(md("""\
聞き比べてみよう：
- チェーン1：残響音にエコーがかかる → リズミカルな反復
- チェーン2：エコーに残響がかかる → 滑らかに溶け合う

エフェクトの適用順序で音が大きく変わることがわかります。"""))

# ==========================================================
# 後半: 仕組みパート（自前実装）
# ==========================================================
cells.append(md("""\
---
# 後半: エフェクトの仕組みを理解する

前半で体験したエフェクトが「どうやって実現されているか」を、
シンプルな自前実装で理解しましょう。

> **注意:** ここでの実装は原理の理解が目的です。
> 前半で聴いた pedalboard の音質とは差があります。"""))

# --- コムフィルタの原理 ---
cells.append(md("""\
## リバーブの原理: コムフィルタ

リバーブの基本構成要素は**コムフィルタ**です。
入力信号を一定時間遅延させ、フィードバックして元の信号に加えます。

```
入力 ──→ [+] ──→ 出力
           ↑         │
           └── [遅延] ← × feedback
```

これにより、一定間隔で減衰する反響音が生まれます。"""))

cells.append(code("""\
def simple_comb_filter(signal, delay_sec=0.03, feedback=0.7, sample_rate=44100):
    \"\"\"シンプルなコムフィルタ\"\"\"
    delay_samples = int(delay_sec * sample_rate)
    data = signal.data.copy()
    buf = np.zeros(delay_samples)
    idx = 0

    output = np.zeros_like(data)
    for n in range(len(data)):
        delayed = buf[idx]
        buf[idx] = data[n] + feedback * delayed
        output[n] = delayed
        idx = (idx + 1) % delay_samples

    return AudioSignal(output, sample_rate)

# コムフィルタ単体の効果
base = create_simple_piano(note_to_frequency(note_name_to_number('C4')), 1.5)
comb_out = simple_comb_filter(base, delay_sec=0.03, feedback=0.8)

display(play_sound(base, "元の音"))
display(play_sound(comb_out, "コムフィルタ通過後（遅延30ms, feedback 0.8）"))"""))

cells.append(md("""\
### コムフィルタの波形を見てみよう

フィードバックにより、信号が一定間隔で減衰しながら繰り返されます。"""))

cells.append(code("""\
# インパルス応答で仕組みを可視化
impulse = np.zeros(22050)  # 0.5秒
impulse[0] = 1.0
impulse_signal = AudioSignal(impulse, 44100)

comb_impulse = simple_comb_filter(impulse_signal, delay_sec=0.01, feedback=0.7)

plt.figure(figsize=(12, 4))
plt.plot(np.arange(4410) / 44100 * 1000, comb_impulse.data[:4410])
plt.title("コムフィルタのインパルス応答")
plt.xlabel("時間 (ms)")
plt.ylabel("振幅")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()"""))

cells.append(md("""\
### Schroeder リバーブ

実用的なリバーブは、遅延時間の異なるコムフィルタを**並列**に並べ、
その後にオールパスフィルタを**直列**に通します。

```
         ┌─ コムフィルタ1 ─┐
入力 ──→ ├─ コムフィルタ2 ─┤──→ オールパス1 → オールパス2 → 出力
         ├─ コムフィルタ3 ─┤
         └─ コムフィルタ4 ─┘
```

- 並列コムフィルタ: 異なる間隔の反響を生成（密度の高い残響）
- オールパスフィルタ: 反響の規則的なパターンを拡散

`audio_lib` の `Reverb` クラスはこの構成で実装されています。"""))

cells.append(code("""\
from audio_lib import Reverb as SimpleReverb

base = create_simple_piano(note_to_frequency(note_name_to_number('A4')), 1.5)

simple_reverb = SimpleReverb(room_size=0.8, damping=0.3, wet_level=0.5)
simple_out = simple_reverb.process(base)

# pedalboard との比較
pro_reverb = Reverb(room_size=0.8, damping=0.3, wet_level=0.5)
pro_out = apply_effect(base, pro_reverb)

display(play_sound(base, "元の音"))
display(play_sound(simple_out, "自前実装 (Schroeder)"))
display(play_sound(pro_out, "pedalboard"))"""))

cells.append(md("""\
自前実装と pedalboard の音質差を聴き比べてみましょう。
プロ品質のリバーブはより密度が高く自然な残響を生み出します。"""))

# --- ダイナミクス ---
cells.append(md("""\
## ダイナミクス処理の基本

ダイナミクスは音量の変化を制御する技術です。

- **コンプレッサー**：音量差を小さくする（大きい音を抑え、小さい音との差を縮める）
- **リミッター**：音量の上限を設定
- **ゲート**：小さな音をカット"""))

cells.append(code("""\
def simple_compressor(signal, threshold=0.7, ratio=4.0):
    \"\"\"シンプルなコンプレッサー\"\"\"
    compressed = signal.data.copy()

    for i in range(len(compressed)):
        sample_level = abs(compressed[i])
        if sample_level > threshold:
            excess = sample_level - threshold
            compressed_excess = excess / ratio
            new_level = threshold + compressed_excess
            if compressed[i] >= 0:
                compressed[i] = new_level
            else:
                compressed[i] = -new_level

    return AudioSignal(compressed, signal.sample_rate)

# 動的な音量変化を持つ音を作成
def create_dynamic_sound(duration=4.0):
    \"\"\"音量が変化する音を作成\"\"\"
    freq = note_to_frequency(note_name_to_number('A4'))
    signal = sine_wave(freq, duration)

    time_samples = len(signal)
    volume_envelope = np.ones(time_samples)
    for i in range(time_samples):
        t = i / time_samples
        volume = 0.5 + 0.3 * np.sin(t * 8 * np.pi) + 0.2 * np.sin(t * 20 * np.pi)
        volume_envelope[i] = max(0.1, min(1.0, volume))

    return AudioSignal(signal.data * volume_envelope, signal.sample_rate)

dynamic_sound = create_dynamic_sound()
compressed_sound = simple_compressor(dynamic_sound, threshold=0.6, ratio=3.0)

display(play_sound(dynamic_sound, "元の音（音量変化あり）"))
display(play_sound(compressed_sound, "コンプレッサー適用後（音量変化を抑制）"))"""))

cells.append(code("""\
# 波形の比較
plt.figure(figsize=(12, 6))
time = np.linspace(0, 4, len(dynamic_sound))

plt.subplot(2, 1, 1)
plt.plot(time, dynamic_sound.data, alpha=0.7)
plt.title('元の音（音量変化あり）')
plt.ylabel('振幅')
plt.grid(True, alpha=0.3)

plt.subplot(2, 1, 2)
plt.plot(time, compressed_sound.data, alpha=0.7, color='orange')
plt.title('コンプレッサー適用後')
plt.xlabel('時間 (秒)')
plt.ylabel('振幅')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()"""))

# ==========================================================
# チャレンジ課題
# ==========================================================
cells.append(md("""\
---
## チャレンジ課題

### 課題1: 自分だけのエフェクトプリセット

pedalboard を使って、自分だけのジャンル別プリセットを作ってみましょう。"""))

cells.append(code("""\
def create_genre_preset(base_sound, genre="pop"):
    \"\"\"ジャンル別エフェクトプリセット\"\"\"
    presets = {
        "pop": Pedalboard([
            Chorus(rate_hz=2.0, depth=0.25, mix=0.3),
            Reverb(room_size=0.5, damping=0.6, wet_level=0.2),
        ]),
        "ambient": Pedalboard([
            Chorus(rate_hz=1.0, depth=0.4, mix=0.4),
            Delay(delay_seconds=0.6, feedback=0.5, mix=0.4),
            Reverb(room_size=0.9, damping=0.2, wet_level=0.6),
        ]),
        "rock": Pedalboard([
            Compressor(threshold_db=-20, ratio=4, attack_ms=5, release_ms=100),
            Delay(delay_seconds=0.2, feedback=0.2, mix=0.2),
            Reverb(room_size=0.4, wet_level=0.2),
        ]),
    }
    board = presets.get(genre)
    return apply_effect(base_sound, board) if board else base_sound

test_sound = create_simple_piano(note_to_frequency(note_name_to_number('A4')), 2.0)

display(play_sound(test_sound, "ドライ"))
for genre in ["pop", "ambient", "rock"]:
    processed = create_genre_preset(test_sound, genre)
    display(play_sound(processed, f"{genre.upper()} プリセット"))"""))

cells.append(md("""\
### 課題2: ライブパフォーマンス風のエフェクト切り替え

セクションごとにエフェクトを追加していき、音の変化を体感しましょう。"""))

cells.append(code("""\
def create_performance_sound():
    \"\"\"ライブパフォーマンス風: 時間とともにエフェクトが変化\"\"\"
    sections = []
    base_freq = note_to_frequency(note_name_to_number('G4'))

    # セクション1: ドライ
    section1 = create_simple_piano(base_freq, 2.0)
    sections.append(section1.data)

    # セクション2: コーラス追加
    section2 = create_simple_piano(base_freq, 2.0)
    sections.append(apply_effect(section2, Chorus(rate_hz=3.0, depth=0.25, mix=0.5)).data)

    # セクション3: コーラス + ディレイ
    section3 = create_simple_piano(base_freq, 2.0)
    board3 = Pedalboard([
        Chorus(rate_hz=3.0, depth=0.25, mix=0.5),
        Delay(delay_seconds=0.25, feedback=0.4, mix=0.4),
    ])
    sections.append(apply_effect(section3, board3).data)

    # セクション4: フルエフェクト
    section4 = create_simple_piano(base_freq, 2.0)
    board4 = Pedalboard([
        Chorus(rate_hz=3.0, depth=0.25, mix=0.5),
        Delay(delay_seconds=0.25, feedback=0.4, mix=0.4),
        Reverb(room_size=0.8, damping=0.3, wet_level=0.5),
    ])
    sections.append(apply_effect(section4, board4).data)

    return AudioSignal(np.concatenate(sections), 44100)

performance_sound = create_performance_sound()
display(play_sound(performance_sound,
    "パフォーマンス風（ドライ → コーラス → ディレイ → フル）"))"""))

# --- まとめ ---
cells.append(md("""\
---
## 今日のまとめ

### 学んだこと
1. **リバーブ**：空間的な広がりと深みを与える
2. **ディレイ**：エコー効果と音の厚みを作る
3. **コーラス**：音を豊かにし、複数楽器感を演出
4. **ダイナミクス処理**：音量変化の制御
5. **エフェクトチェーン**：複数エフェクトの組み合わせ
6. **エフェクトの原理**：コムフィルタによるリバーブの仕組み

### 音楽制作のコツ
- エフェクトは適度に — やりすぎは禁物
- 順序が重要 — エフェクトの適用順で音が大きく変わる
- ジャンルに合わせる — 音楽スタイルに適した設定を選ぶ

### 次回予告
第6回では**MIDI**と**シーケンサー**を学びます。
複数パートを組み合わせた本格的な音楽制作に挑戦します。"""))

# ============================================================
# ノートブック生成
# ============================================================

def main():
    nb = nbformat.v4.new_notebook()
    nb.metadata.update({
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.12.0",
        },
    })
    nb.cells = cells
    nbformat.write(nb, OUTPUT_PATH)
    print(f"Generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
