# X3 Amber Player (Deh-Modernized)

Interactive recreation of the **Eonon X3** head-unit interface, redesigned in a 2008-era amber / OEL style inspired by classic Pioneer DEH / Carrozzeria and 1990s Alpine equalizers.

This is a fully working browser prototype intended as a visual and behavioral reference for a future native replacement UI on the actual hardware.

**Live demo intent**: open `index.html` locally or host the folder. The player opens directly into the stereo interface.

> **Important**: The complete working player (`index.html`, full `player.js`, and all 83 animation assets) is provided in the project zip. Upload those files into this repository (or use the zip directly) for a fully functional experience. The GitHub tree currently holds documentation and verification data.

## What’s included

- **83 original Carozerra animation clips**
  - 59 amber-palette
  - 24 full original RGB color
- Continuous animation (no pause) + movie shuffle
- Simplified one-screen Movies picker (all 17 movies at once; tap returns to Now Playing)
- **Illumination color switch**: Amber or Blue (Settings → Display)
- Source selection, transport, volume, radio tuning + presets
- 16-band EQ, audio settings, auto-dimming (clock schedule / vehicle lights / manual)
- Interactive memory model + desktop stress-test lab
- Preference persistence (localStorage)
- Responsive layout checks at 1024×600 and smaller viewports

## Design direction

- Predominantly black faceplate with amber/orange (or blue) illuminated text, indicators and animations
- Period-correct dense layouts, segmented numbers, compact uppercase labels
- Hardware bezel that mirrors the real X3 front-panel controls (knob, Home/Power, USB, AUX, MIC, RST)
- No modern “dashboard app” styling — deliberately 2008-era car-audio aesthetic

## Hardware & feasibility notes

See **[FEASIBILITY.md](FEASIBILITY.md)** and the JSON reports in `/docs`.

**Summary of current understanding** (reference platform only — your physical unit has not been measured):

| Item | Documented value | Source |
|------|------------------|--------|
| SoC | Sunplus SPHE8368-U | Vendor datasheet |
| CPU | ARM Cortex-A7 + Andes N13 | Vendor |
| RAM | 1 Gbit embedded DDR2 (nominal 128 MiB) | Vendor |
| Firmware (reference) | Linux 4.9.217, 32-bit ARM EABI5, Qt 5.3.2 (build X3_20250718) | Reverse-engineering |
| Display config | 1024 × 600 Android Auto / touch | Firmware findings |
| Userdata / tmpfs | ~132 MB userdata, ~28 MB shared tmpfs (reference unit) | Firmware findings |

A native streaming decoder that keeps only one (or two small) frame buffers looks plausible on the memory arithmetic. Full browser deployment on the unit is unverified. Exact free RAM, framebuffer format, CPU clock and performance under simultaneous audio + phone projection + reverse camera still need to be measured on the real hardware.

**Firmware replacement is a separate engineering stage** and requires verified hardware/ABI compatibility, a full backup, and a tested recovery path before any writes.

## Sources & citations

### Original animation assets & web reference
- Interactive reference player: https://youxufkhan.github.io/carozerra/
- Source collection (pinned Git blobs used for verification): https://github.com/youxufkhan/carozerra/tree/main/assets/clips

All 3 592 frames, frame order and native dimensions were verified against the original collection. Meter clips are pre-recorded animations, not live audio analysis.

### X3 firmware reverse-engineering
- Primary findings document: https://github.com/prasys/eannon-x3-fw-reverse/blob/main/docs/FINDINGS.md  
  (Linux version, Qt version, ABI, display configuration, storage observations on a reference unit)

### Vendor hardware
- Sunplus SPHE8368-U product page: https://www.sunplus.com/products/sphe8368-U.asp
- Preliminary datasheet (Taiwan Trade Show mirror): https://storage.googleapis.com/www.taiwantradeshow.com.tw/product/202203/T-01752086.pdf

### Emulation note
No exact SPHE8368-U board model appears in the examined QEMU Arm documentation. Generic Cortex-A7 / `virt` machines omit the proprietary display, DSP, MCU and projection services.

## Project layout

```
├── index.html          # Self-contained player (assets embedded as JSON + files)
├── player.js           # All UI logic, state, auto-dimming, theme, lab
├── assets/
│   ├── animations/     # 83 × .webp (animated) + .png (still)
│   ├── lucide.min.js
│   └── benchmark-results.js
├── docs/               # Verification & measurement dumps
│   ├── X3-asset-verification.json
│   ├── X3-benchmark-results.json
│   ├── X3-browser-verification.json
│   ├── X3-color-motion-verification.json
│   ├── X3-hardware-evidence.json
│   └── X3-publication.json
└── FEASIBILITY.md      # Full memory model, stress-test results, next engineering steps
```

## Running

1. Download the complete project zip (or upload its contents into this repo).
2. Open `index.html` in a modern browser (Chrome / Edge recommended).
3. Or serve the folder with any static HTTP server.

**Theme**: Settings → Display → Illumination color → Amber or Blue.

All settings persist across reloads via `localStorage` key `x3-2008-v3`.

## License / attribution

Animation assets originate from the Carozerra / Pioneer OEL collection curated by youxufkhan.  
Firmware observations come from the public reverse-engineering work of prasys.  
This prototype is a non-commercial interface study and feasibility artifact.

---

*Built as a reference for a potential native Qt replacement on the Eonon X3. Not affiliated with Eonon, Pioneer, Alpine or Sunplus.*
