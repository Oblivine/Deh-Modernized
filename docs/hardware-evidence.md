# X3 hardware evidence and simulation limits

Research date: 2026-10-26. This describes a documented reference platform, not a diagnosis of the user's physical board.

| Item | Evidence | Confidence / limit |
| --- | --- | --- |
| SoC | Sunplus SPHE8368-U, Cortex-A7 main CPU; Andes N13 coprocessor | Vendor specifications; community X3 firmware identifies this family. Board revision still unverified. |
| RAM | Embedded 1 Gbit DDR2, conventionally 128 MiB capacity | Vendor specification, not 1 GB. Available application memory is lower and unknown. |
| CPU frequency | Not stated in the examined vendor sources | Do not report 800 MHz as verified. |
| Graphics | 2D graphics, OSD formats/scaling; video decoders | Vendor capability does not prove a browser can use acceleration. |
| OS / UI | Linux 4.9.217; ARM EABI5; Qt 5.3.2 | Extracted X3_20250718 reference firmware findings; not verified on user's unit. |
| Display | X3 app's Android Auto configuration uses 1024 x 600 display/touch | Configuration evidence, not an independent framebuffer measurement. |
| Persistent storage | userdata 132 MB, approximately 130 MB free in research unit; nvm 16 MB, approximately 12.2 MB free | Unit snapshot, not guaranteed headroom. Keep clips out of settings partition. |
| Temporary storage | /etc, /root and /tmp share approximately 28 MB RAM-backed tmpfs | Reference-unit observation; do not stage the library there. |
| Browser | No usable browser runtime has been established by this research | The HTML/WebP prototype is not an installable Qt 5.3.2 UI. |
| Hardware emulator | No SPHE8368-U board appears in QEMU's examined supported Arm board documentation; no suitable model located | An emulated Cortex-A7 CPU or generic `virt` board does not reproduce Sunplus display, DSP, MCU, NAND or projection services. |

Sources: [Sunplus product specification](https://www.sunplus.com/products/sphe8368-U.asp), [Sunplus preliminary datasheet, March 2022](https://storage.googleapis.com/www.taiwantradeshow.com.tw/product/202203/T-01752086.pdf), [X3 firsthand firmware investigation](https://github.com/prasys/eannon-x3-fw-reverse/blob/main/docs/FINDINGS.md), [QEMU Arm machine documentation](https://www.qemu.org/docs/master/system/target-arm.html).

## What a simulation can establish

Desktop CPU throttling is a relative stress test, with no calibrated mapping to this SoC. Browser JavaScript heap excludes much of the renderer, decoded image cache, GPU surfaces and operating system. Neither measure establishes real X3 RAM use, boot time, touch latency, thermal behavior or audio/projection contention. A model can test resource arithmetic and detect excessive preloading; it cannot certify firmware compatibility.

At the prototype's 1024 x 600 target, a 32-bit framebuffer occupies 2.344 MiB, or 4.688 MiB double buffered. RGB565 halves these figures. Two 256 x 64 RGBA clip buffers occupy 128 KiB; two RGB565 buffers occupy 64 KiB. These are arithmetic allocations only, excluding UI libraries and drivers. Scale each native frame at presentation rather than storing every frame enlarged to the display size.

## Engineering recommendation

Conditional feasibility: the visual design and small native-resolution clips are plausible for a native lightweight player that streams one animation and uses a small bounded decode buffer. The entire library should stay on persistent storage; avoid pre-decoding every clip. A modern Chromium runtime is not an established fit for a 128 MiB platform and adds an unverified dependency. Prefer integration with the stock Qt application or a compatible native process once its ABI, graphics path, service interfaces and available memory have been measured.

The next meaningful board test is read-only identification: firmware/build and SoC revision, /proc/meminfo, /proc/cpuinfo, framebuffer dimensions/format, stock process memory, storage headroom, and CPU use during USB audio, CarPlay/Android Auto and reverse camera. Native decoding and touch latency must then be measured on that same board. Firmware replacement remains a separate stage with a verified backup and recovery route.
