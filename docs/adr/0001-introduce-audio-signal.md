# ADR-0001: AudioSignalクラスの導入とAudioConfig廃止

- **日付:** 2026-04-03
- **ステータス:** 採用済み

## 背景

旧設計では `AudioConfig`（`sample_rate`, `bit_depth`, `max_amplitude` を保持）を全クラスのコンストラクタに渡していたが、以下の問題があった。

1. **性質の異なるものが混在** — `sample_rate` は音響処理の根幹だが、`bit_depth`/`max_amplitude` はWAV保存の実装詳細
2. **データとメタデータの分離** — 生成された信号（np.ndarray）が sample_rate を持たず、呼び出し側が常にペアで管理する必要があった
3. **config不一致のリスク** — 各クラスが `config or AudioConfig()` で独立にデフォルト生成するため、異なる sample_rate のオブジェクトが混在しうる

## 決定

音響ライブラリの標準的な設計（librosa, scipy, pydub）に倣い、**信号データに sample_rate を持たせる `AudioSignal` クラス**を導入し、`AudioConfig` を廃止する。

### 関数とオブジェクトの使い分け

状態を持たない操作は**関数**、状態を持つ操作は**オブジェクト**とした。この使い分け自体がプログラミング教育の教材となる。

| 分類 | 形 | 理由 |
|------|---|------|
| 波形生成（サイン波等） | 関数 | 入力→出力の純粋な変換。内部状態なし |
| エンベロープ（ADSR等） | 関数 | 同上 |
| フィルター・エフェクト | オブジェクト | 内部状態（係数・バッファ）を持つ |
| 楽器・シーケンサー | オブジェクト | 複数部品の構成・トラック管理 |

### 廃止したもの

| 廃止対象 | 移動先 |
|---------|--------|
| `AudioConfig` クラス | sample_rate は各関数/クラスの引数 + AudioSignal へ |
| `bit_depth` / `max_amplitude` | `save()` の内部定数（16bit / 0.95 固定） |
| `WaveFileIO` クラス | `save_audio()` / `load_audio()` 関数 |
| オシレーター/エンベロープのクラス | `sine_wave()` / `adsr()` 等の関数 |
| `apply_envelope()` | `AudioSignal` の `*` 演算子で代替 |

## 影響

ライブラリ全体のAPI変更（core, synthesis, effects, instruments, sequencer）、全テスト・ノートブック・examplesの更新が必要となり、一括で実施した。
