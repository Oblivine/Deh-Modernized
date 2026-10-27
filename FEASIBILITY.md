# X3 interface feasibility assessment

27 October 2026. Assessment of a documented reference platform; the user's physical X3 has not been diagnosed or benchmarked.

## Result

**A native implementation looks plausible; direct installation of this browser prototype is unverified.** The memory arithmetic supports one animation at a time. It does not establish firmware compatibility or prove performance under audio, phone projection and camera workloads. No exact Sunplus board emulation was performed.

## What changed and what works

The interface uses compact track information, a wide animation area, accessible playback controls and larger round navigation. The screen fits a 720 × 405 browser preview without scrolling. Amber and cyan settings change the interface and monochrome clips; original full-color clips retain their colors. Scanlines, a light glow and edge shading apply only to the animation. Audio, radio, phone and camera features remain demonstrations.

Movies, Color and Meters are direct animation libraries. Tapping the left or right half of the animation stays within the chosen library. Shuffle is saved independently for each library and advances moving clips at their original timing; Color still images are available only when its shuffle is off. Movie music playback controls do not pause animations. The animation gallery and Backgrounds shortcut were removed. Meter channels use the original upper and lower frames placed side by side, and are recorded rather than audio-reactive.

The package retains all 83 original assets: 59 monochrome and 24 full-color, including ten color stills. The direct libraries expose 17 movies, 24 color files and 15 meters. All 3,592 original frames, order and native dimensions were checked against pinned Git blobs. A browser may retain decoded caches for the animation and glow layers; the memory model is not a bounded native decoder. [Original reference](https://youxufkhan.github.io/carozerra/), [source collection](https://github.com/youxufkhan/carozerra/tree/main/assets/clips).

Browser checks covered each library, still exclusion while shuffling, automatic advancement, saved preferences, playback, and 27 combinations of three fonts, three libraries and 720 × 405, 800 × 480, and 1024 × 600 viewports. They do not measure physical touch targets or performance on the actual unit. The desktop stress snapshot below measured an earlier interface revision and is not a benchmark of the current build.

## Documented hardware and limits

Sunplus specifies a Cortex-A7 main CPU, Andes N13 coprocessor and **1 Gbit embedded DDR2**, conventionally **128 MiB**, for SPHE8368-U. Its CPU clock and the application memory available on this particular unit remain unknown. [Vendor specification](https://www.sunplus.com/products/sphe8368-U.asp), [preliminary vendor datasheet](https://storage.googleapis.com/www.taiwantradeshow.com.tw/product/202203/T-01752086.pdf).

Firsthand X3 firmware research identifies Linux 4.9.217, 32-bit ARM EABI5 and Qt 5.3.2 in build X3_20250718. It documents 1024 × 600 Android Auto display/touch configuration, approximately 132 MB userdata storage and a shared approximately 28 MB RAM-backed tmpfs. These observations are from the reference unit. They do not verify this user's board, framebuffer or free storage. A usable browser runtime was not established. [X3 firmware findings](https://github.com/prasys/eannon-x3-fw-reverse/blob/main/docs/FINDINGS.md).

No compatible SPHE8368-U board model was located in the examined QEMU Arm machine documentation. A generic Cortex-A7 or `virt` machine would omit Sunplus display, DSP, MCU, storage and projection services. [QEMU Arm documentation](https://www.qemu.org/docs/master/system/target-arm.html).

## Memory model

The package includes 59 cyan variants alongside 59 amber and 24 original full-color clips. The cyan variants preserve 2,182 source-frame positions and 63 ms timing, with source brightness mapped to OEL cyan. The player loads the selected palette; it does not decode both libraries eagerly. The base decoded-frame arithmetic below is unchanged by palette switching.


| Allocation | Calculated size |
| --- | ---: |
| Entire encoded animation library | 8.21 MiB |
| Still thumbnails | 0.46 MiB |
| All 83 clips decoded as native RGBA | 116.05 MiB |
| Largest single decoded RGBA clip | 5.27 MiB |
| Largest two native RGBA clip buffers | 128 KiB |
| Two 1024 × 600 ARGB framebuffers | 4.688 MiB |

Pre-decoding the whole collection would leave under 12 MiB of nominal RAM for the OS, UI, graphics and all other services. Keep the library on persistent storage and scale only the frame being shown. A proposed native streaming decoder could use two small clip buffers; codec state, read buffers, UI libraries and drivers require additional memory.

The interactive lab uses an adjustable **assumed** OS/services reserve (96 MiB by default) and 4 MiB extra UI/decoder allowance. Neither was measured on the X3. The model includes the selected compressed clip and framebuffers. It demonstrates allocation tradeoffs; it does not enforce a browser memory cap or prove that the native process fits. Large RGB565 buffers would be half the RGBA allocation but would reduce color precision.

## Measured desktop stress tests

Windows x86-64 Chrome, 1024 × 600 display area, local static server. Each run measures 36 DOM click actions through the second animation-frame opportunity, then four seconds of visible Movie 01 animation changes using cropped painted-frame capture.

| Relative CPU throttle | Initial load | Tap to frame median | Tap to frame p95 | Visible animation changes | JS heap |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1× | 547 ms | 13.9 ms | 308.8 ms | 15.70/s | 3.06 MiB |
| 4× | 1021 ms | 13.9 ms | 228.5 ms | 15.63/s | 3.07 MiB |
| 8× | 2288 ms | 34.0 ms | 141.1 ms | 15.39/s | 3.09 MiB |
| 16× | 5045 ms | 75.0 ms | 186.1 ms | 15.52/s | 3.09 MiB |

These are **uncalibrated desktop stress factors**, not X3-equivalent CPU speeds. They throttle browser main-thread execution; decoder threads, GPU, memory bandwidth and ARM instructions are not reproduced. The frame capture adds overhead and counts visible changes, so duplicate source frames need not produce a change. Tap timings are paint opportunities, not measured physical touch-to-photon latency. Cold transitions cause occasional longer stalls (maximum 512 ms).

The baseline Chrome renderer processes summed to 207.23 MiB working sets; all reported browser processes summed to 505.79 MiB. Shared pages may be counted more than once, and these desktop snapshots do not predict ARM memory use. They demonstrate why the small JavaScript heap alone is an inadequate feasibility measure. No audio playback, CarPlay/Android Auto, Bluetooth or camera workload ran in these tests.

## Next engineering stage

First obtain read-only measurements from the actual unit: exact board/firmware, CPU identification/clock, /proc/meminfo, stock process memory, framebuffer size/format, persistent storage and load during audio, phone projection and reverse camera. Then build a compatible native Qt test process or verified equivalent, measure decode/scaling and control latency on that board, and integrate its real hardware services. That work is required before a performance claim about the actual X3.

Firmware replacement remains separate: verify hardware and ABI compatibility, make a usable backup, and confirm a recovery method before any firmware writes. Nothing in this prototype has been flashed or installed on the unit.
