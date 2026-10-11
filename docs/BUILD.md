# Build and verification — v0.2.2

Python 3, Pillow, Pasmo and Windows fonts are required. Fonts and BIOS files are not bundled.

```powershell
python -m pip install Pillow
$env:PASMO = 'C:/path/to/pasmo.exe'
python tools/build_release.py
```

This rebuilds the checked-in 50 stages without regenerating or reordering them. The release builder checks SHA-256 fingerprints of the stage data, rule model and exhaustive-search evidence, then replays all stored solutions. For changed puzzle inputs, use `python tools/build.py` to run a fresh exhaustive search (potentially slow). Output: `outputs/PAWS-PARTNERS-MSX2.rom`.

The renderer uses Windows fonts under `C:/Windows/Fonts`. Different font versions can change the ROM. Do not rebuild a ROM while an emulator has it open. Authoring scripts are not needed for a release rebuild. Stage data and validation evidence contain solutions.

## Current ROM — v0.2.2

SHA-256: `ac38954755d60358477c3052b2d7fe91494f991dfd9a3d1aa6b8c3f8ea850e43`.

The rendering-code build `89d5ea4ba5ac14b7544c27a2346f13937faf7a57eb6272b7cee433fa59b63fc0` passed 40,897 campaign checks, 22 cancellation, 16 overlay, 88 tall-page, 56 PAD, 255 password and 14 music checks per openMSX profile, plus PSG trace verification. The final build changes only 92 label-graphics bytes from that tested ROM. A further 480 byte-exact VRAM checks passed on the final ROM using RAM-injected display fixtures. These fixtures verify overlapping mechanism identities and states, not player-input behavior. Historical reports retain their tested hashes.

1 MiB ASCII8. MSX2 or later, 64 KiB RAM / 64 KiB VRAM; TurboR uses Z80 mode. Physical hardware is unverified.

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
