# PAWS PARTNERS

**ネコとうさぎを、それぞれの家へ。 / Guide two friends to their own homes.**

A 50-stage cooperative puzzle game for **MSX2 and later**. Place TURN and WAIT chips, push crates, hop over holes, and coordinate switches. There is no time limit.

ネコとうさぎの得意技と、到着する順番を考えるパズルです。方向転換やWAITを配置してから二匹を出発させます。時間制限なし・全50面。

![PAWS PARTNERS title](docs/images/title.png)

## Download / ダウンロード

- **[Latest release / 最新版](https://github.com/kanon-ai/PAWS-PARTNERS/releases/latest)** — ROM and manuals in one ZIP.
- [ROM directly / ROM単体](rom/PAWS-PARTNERS-MSX2.rom) — 1 MiB, ASCII8.
- **[日本語マニュアル](docs/MANUAL.ja.md)** / **[English manual](docs/MANUAL.en.md)**
- [BGM付き紹介動画 / Music trailer](media/PAWS-PARTNERS-X-BGM.mp4) — approximately 56 seconds, fictional promotional stages, no campaign solutions. Music is laid continuously over the video; the actual game's title screen is silent.

## Requirements / 動作条件

MSX2 or later, **64 KiB RAM / 64 KiB VRAM**, keyboard, and a device or emulator supporting **1 MiB ASCII8** ROMs. MSX Turbo R runs the game in Z80 mode. No enhanced VDP is required. A 512 KiB-only flash cartridge is insufficient.

MSX2以降、メインRAM 64KiB・VRAM 64KiB以上、キーボード操作です。拡張VDPは不要です。1MiBのASCII8 ROMに対応する環境を使用してください。

**OpenMSX-tested; physical hardware not yet verified. / openMSXで確認済み・実機未検証。**

## Quick start / まず遊ぶ

1. At the title, leave the password blank and press **Enter**. / 合言葉を空欄にしてEnter。
2. Select a placement spot with **Left/Right**, cycle its chip with **Space**. / 左右で場所を選び、Spaceで配置。
3. Press **Enter** to start both friends. Use **Esc** to retry. / Enterで出発、Escで再挑戦。
4. Bring both friends to their matching homes. / 二匹をそれぞれの家に帰しましょう。

**Planning: Up places a solution hint; Down removes all chips.**
配置中の上キーは、その場所に正解チップを置くヒントです。下キーは全消去です。

Read the manuals for WAIT, FLIP, large-map browsing, retries, and stage passwords.
ミスしても残機は減りません。詳しい仕掛け・スクロール・合言葉の使い方はマニュアルをご覧ください。

## Status / 公開状況

**v0.1.0 — public prototype / 公開試作版**

The 50 stages include mirrored layouts and route variations, not 50 unrelated mechanisms. Larger maps and timing puzzles appear later. Stage data and source code contain solutions, but the player manuals do not list stage solutions or passwords.

50面には反転・経路違いの派生を含みます。後半では広いマップやタイミングを考える仕掛けが登場します。ソース・面データには解法が含まれますが、プレイヤー向けマニュアルには解答や合言葉一覧を載せていません。

There is no automatic save; write down stage-clear passwords. Joystick controls are not implemented. Continuously moving loops are not automatically detected: press Esc to retry.

進行状況は合言葉で再開できます。自動セーブ・ジョイスティック操作は未実装です。動き続けるループはEscでやり直してください。

## Music / 音楽

**Pixel Party** — music supplied by kanon-ai, produced through a Suno → PSG → AI music editor workflow. Two melodic PSG channels and percussion, with short sound-effect borrowing on channel C.

ゲーム中はループし、タイトル／合言葉・行き詰まり画面では停止します。

## Development / 開発

[Build instructions and test evidence / ビルドと検証](docs/BUILD.md)

The released ROM passed 821 checks on each of three openMSX machine profiles, plus password and audio-specific tests. These are emulator results, not a physical-hardware guarantee.

公開ROMはopenMSXの3機種設定で各821項目、および合言葉・音楽の専用検証を通過しています。すべての遊び方や実機互換性を保証するものではありません。

## License and disclaimer / ライセンス・免責

[MIT License](LICENSE) · [Credits / 素材の表記](CREDITS.md) · **[Disclaimer / 免責事項](DISCLAIMER.md)**

Free prototype, provided **as is, without warranty**. Bug reports are welcome, but responses, fixes, and future updates are not guaranteed.

無償公開の試作版・無保証です。不具合報告をいただいても、返信・修正・今後の更新を保証できません。
BIOS・エミュレーター本体・書き込みツールは同梱しません。
