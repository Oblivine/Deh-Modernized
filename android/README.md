# DEH Modernized — Android preview

This is an early, test-signed Android app for Android 8.0 (API 26) or newer. It is an APK, not firmware. A recent Android System WebView/Chrome with container query and dynamic viewport support is required. No physical Android head unit was connected for this build.

## Install

Copy `DEH-Modernized-Android-preview.apk` to the unit with a USB drive, or download it on the unit. Open it in the unit's Files app and follow Android's installer. Android may ask you to allow this file manager or browser to install unknown apps. Open **DEH Modernized** from the app list. No root or flashing is required. This is a preview, not a production-certified build.

## Use

- **Source → Files** opens Android's file picker. Choose one or more audio files; Play, Pause, Stop, Previous and Next control those files. Audio focus loss pauses playback. Android and the selected provider determine which audio formats can be played and whether access persists after reboot.
- Movies, Color and Meters use the included original clips. Each library has its own animation shuffle; shuffle skips still images. Meter animations are recorded and do not respond to music.
- **Settings → Android & dial setup** lets you reverse a supported rotary dial or opt into using volume key events for navigation. With that option on, volume-up/down navigate and mute/volume-mute selects only if the unit delivers those events to the app; this changes what those keys do while the app is in front. The last received input is displayed to help identify the hardware. Normal volume keys remain volume by default.
- D-pad arrows and supported Android rotary encoders move focus; center/Enter selects. Press on a selected slider or list to adjust it using rotation, then press again to leave adjustment mode.
- **Settings → Android & dial setup** can assign the unit's own launchable apps to **Radio**, **Bluetooth phone**, **Camera**, and **Audio / EQ**. Choose the corresponding stock app installed on the unit for each shortcut; the selection is saved and can be cleared there. If a control has not been assigned, selecting it offers the app picker and then opens the chosen app. When launching the radio or phone app, DEH Modernized pauses its own music. This is a handoff to the manufacturer's screen, not tuner, calling, camera or DSP controls inside DEH Modernized. Apps without a launchable activity may not appear in the picker; a removed or unavailable app must be selected again.
- The **APPS** button opens other launchable Android apps. In Android & dial setup, **Choose default Home app** opens Android's Home-app settings. If your head unit allows this and you select DEH Modernized, Android can return to it on startup. Some vendors override the default launcher; sleep, cold boot, reverse camera, and stock-app behavior have not been verified. You can change the default Home app back in Android settings.

## Current limitations

The current candidate is the universal 7-inch, 2-DIN Android head unit listed at https://www.aliexpress.us/item/3256813188616078.html. Its lowest-priced option is labelled 2-32G No Carplay. The internal platform, Android version, true specifications and firmware are not yet verified, and the unit has not been purchased or tested. Physical fit and wiring for a 2008 Yaris hatchback must be confirmed. The earlier Eonon UX7A was a candidate, not a verified match. Neither the listing nor the supplied Civic cleanup write-up establishes third-party APIs for directly controlling this unit’s hardware. The stock-app shortcuts depend on the matching apps being installed and launchable; their names and behavior on the UX7A remain unverified. The unit is responsible for any automatic reverse-camera takeover, which this app does not implement or override. The Android audio-session equalizer is not a substitute for the unit's hardware DSP.

File playback and controls were implemented but not tested on an Android device. Background playback, resume after sleep/reboot, audio-focus behavior, long playlists, removable USB storage, different WebView versions, launcher startup and all dial events require real-unit testing. Android Auto and CarPlay are not integrated. It does not replace firmware or claim the supported functions of a manufacturer app. It does not run as an Android Auto projected app on a phone.

# Head-unit inventory helper

`tools/inspect-head-unit.ps1` is an optional, read-only inventory for an Android unit that is already connected to ADB and authorized on the unit. It records the Android-reported version, API, model, hardware and CPU properties, total memory, available WebView provider details, package names and launchable activity names. These are self-reported values and are not proof of the actual hardware. Availability varies by Android version and vendor.

The helper does not connect or pair, install or disable apps, change settings, root, flash, take screenshots, or collect logcat. It requires exactly one connected and authorized ADB device and refuses to overwrite an existing report. Device serial numbers and IP addresses are deliberately not recorded. The report includes installed package and activity names, which can reveal private information; review it before sharing.

Example, after installing Google's official Android platform-tools and authorizing the device yourself:

```powershell
.\tools\inspect-head-unit.ps1 -AdbPath 'C:\platform-tools\adb.exe' -ReportPath '.\head-unit-report.txt'
```

Inspecting device-specific vendor app components may help identify possible integrations; it does not establish that direct radio, phone, camera, or DSP APIs are available or safe to use.

## Build

Keep this `android/` folder next to the repository `assets/` folder, open this folder in Android Studio, install Android SDK Platform 35 and Build Tools 35.0.0, and run `gradlew assembleDebug` or `gradlew assembleRelease`. Gradle wrapper 8.11.1 uses a pinned checksum. Android Gradle Plugin 8.9.0 requires JDK 17 or later. The release build is configured to use a local test signing key; set `DEH_DEBUG_KEYSTORE` to the original preview keystore if you need compatible updates. A different signing key requires uninstalling the old app, which removes its data. Do not publish a private signing key. Production signing and a full device test are separate work.

## Sources

- Android local content and WebViewAssetLoader: https://developer.android.com/develop/ui/views/layout/webapps/load-local-content
- Android rotary events: https://developer.android.com/reference/android/view/InputDevice#SOURCE_ROTARY_ENCODER and https://developer.android.com/reference/android/view/MotionEvent#AXIS_SCROLL
- Home apps: https://developer.android.com/work/dpc/dedicated-devices/cookbook#custom-home-apps
- Eonon UX7A product information: https://www.eonon.com/Android-Car-GPS/Double-Din-GPS-Navigation/eonon-7-inch-2-din-carplay-and-android-auto-car-stereo-ux7a.html
- Android package visibility: https://developer.android.com/training/package-visibility
- Android audio-session equalizer: https://developer.android.com/reference/android/media/audiofx/Equalizer
- Original animations: https://github.com/youxufkhan/carozerra
