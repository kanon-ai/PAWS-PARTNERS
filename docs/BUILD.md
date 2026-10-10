# Build and verification — v0.2.0

Python 3, Pillow, Pasmo and Windows fonts are required. Fonts and BIOS files are not bundled.

```powershell
python -m pip install Pillow
$env:PASMO = 'C:/path/to/pasmo.exe'
python tools/build_release.py
```

This rebuilds the checked-in 50 stages without regenerating or reordering them. The release builder checks SHA-256 fingerprints of the stage data, rule model and exhaustive-search evidence, then replays all stored solutions. For changed puzzle inputs, use `python tools/build.py` to run a fresh exhaustive search (potentially slow). Output: `outputs/PAWS-PARTNERS-MSX2.rom`.

The renderer uses Windows fonts under `C:/Windows/Fonts`. Different font versions can change the ROM. Do not rebuild a ROM while an emulator has it open. Authoring scripts are not needed for a release rebuild. Stage data and validation evidence contain solutions.

## Current ROM

SHA-256: `548d38a04635cafa0b9ace6f475fe6630ac02d475f353a09dbe55967b05b3556`

1 MiB ASCII8. MSX2 or later, 64 KiB RAM / 64 KiB VRAM. TurboR uses Z80 mode.

For this hash, both openMSX profiles `C-BIOS_MSX2_EU` and `Panasonic_FS-A1ST` passed:

- Full 50-stage keyboard regression, including correct and empty placements, retry and final wrap: 40,897 checks each.
- PAD boundary fixtures: 56 each (RAM-injected, separate from keyboard tests).
- Mid-run cancellation: 22 each.
- Overlay controls: 16 each; tall-page browsing: 88 each.
- Password entry: 255 each.
- Music state: 14 each; PSG stream checked separately.

```powershell
python tools/check_trials.py --machine C-BIOS_MSX2_EU --wrong-paths
python tools/check_supports.py --machine C-BIOS_MSX2_EU
python tools/check_cancel.py --machine C-BIOS_MSX2_EU
python tools/check_passwords.py --machine C-BIOS_MSX2_EU
python tools/check_music.py --machine C-BIOS_MSX2_EU
python tools/verify_music_trace.py --machine C-BIOS_MSX2_EU
```

Repeat with `Panasonic_FS-A1ST`. Scripts expect openMSX at `C:/Program Files/openMSX` and use isolated directories under `work/`. Supply machine ROMs separately. Reports in `validation/` identify their ROM hashes. These checks do not establish physical-hardware compatibility, exhaustive ROM input coverage or measured human difficulty.

## 日本語

通常は `tools/build_release.py` で配布データを再ビルドしてください。面の自動生成ツールは不要です。データやルールを変更した場合は `tools/build.py` の全探索検証を実行します。ソースと検証資料には解法が含まれます。実機動作は未確認です。
