# 仕様 / Specifications

| 項目 / Item | 内容 / Details |
|---|---|
| Edition | Expert Version 1.0.3 |
| Stages | 新作50面 / 50 new stages |
| Target | MSX2, 64 KiB RAM, 64 KiB VRAM; TurboR Z80 mode |
| ROM | 1,048,576 bytes; ASCII8 mapper |
| Board | 最大16×12マス、通常表示は最大4区画 / Up to 16×12 tiles, up to four normal-view sections |
| Inspector | F5 + hold SHIFT + arrows: inspect any tile; release to return |
| Overview | F5: full-board placement and live simulation; pause/resume supported |
| Goal | 二匹をそれぞれの家へ / Both friends reach their matching homes |
| Time limit | なし / None |
| Resume | 面ごとのパスワード。途中配置・実行状態は保存しない / Stage passwords; no mid-stage state save |
| Sound | PSG; Expert BGM and clear phrase |

固定された種別分岐、訪問ごとに変わるALT・CYC、一度だけ効く床、重さで開閉する扉、一度きりのロケットなどを組み合わせています。配置できるチップとステージ固有の仕掛けはマニュアルで分けて説明しています。

Mechanisms include species-dependent routing, ALT/CYC visit states, one-use floors, weight-controlled gates and one-use rockets. Placeable chips and built-in mechanisms are documented separately.

画面展開の平均時間は、openMSXの通常画面200枚の比較で約10％短縮しました。MSX2設定は約0.541→0.487秒、TurboR設定は約0.551→0.496秒です。展開処理のみの値であり、切り替え全体や実機の実測ではありません。描画の優先順位や転送内容は変更していません。

The board decoder is about 10% faster in a 200-page openMSX comparison: approximately 0.541→0.487 s with the MSX2 profile and 0.551→0.496 s with the TurboR profile. These are decoder timings, not complete transitions or physical-hardware measurements. Drawing priority and transferred contents are unchanged.

難易度は試遊前の暫定評価です。エミュレーター検証は実機互換性の保証ではありません。[免責事項](DISCLAIMER.md)を参照してください。

Difficulty is provisional before human playtesting. Emulator validation does not guarantee physical-hardware compatibility. See the [disclaimer](DISCLAIMER.md).
