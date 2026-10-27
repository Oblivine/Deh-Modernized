# DEH Modernized — Android preview

This is an early, test-signed Android app for Android 8.0 (API 26) or newer. It is an APK, not firmware. A recent Android System WebView/Chrome with container query and dynamic viewport support is required. No physical Android head unit was connected for this build.

## Install

Copy `DEH-Modernized-Android-preview.apk` to the unit with a USB drive, or download it on the unit. Open it in the unit's Files app and follow Android's installer. Android may ask you to allow this file manager or browser to install unknown apps. Open **DEH Modernized** from the app list. No root or flashing is required. This is a preview, not a production-certified build.

## Use

- **Source → Files** opens Android's file picker. Choose one or more audio files; Play, Pause, Stop, Previous and Next control those files. Audio focus loss pauses playback. Android and the selected provider determine which audio formats can be played and whether access persists after reboot.
- Movies, Color and Meters use the included original clips. Each library has its own animation shuffle; shuffle skips still images. Meter animations are recorded and do not respond to music.
- **Settings → Android & dial setup** lets you reverse a supported rotary dial or opt into using volume key events for navigation. With that option on, volume-up/down navigate and mute/volume-mute selects only if the unit delivers those events to the app; this changes what those keys do while the app is in front. The last received input is displayed to help identify the hardware. Normal volume keys remain volume by default.
- D-pad arrows and supported Android rotary encoders move focus; center/Enter selects. Press on a selected slider or list to adjust it using rotation, then press again to leave adjustment mode.
- The **APPS** button opens other launchable Android apps. In Android & dial setup, **Choose default Home app** opens Android's Home-app settings. If your head unit allows this and you select DEH Modernized, Android can return to it on startup. Some vendors override the default launcher; sleep, cold boot, reverse camera, and stock-app behavior have not been verified. You can change the default Home app back in Android settings.

## Current limitations

File playback and controls were implemented but not tested on an Android device. Background playback, resume after sleep/reboot, audio-focus behavior, long playlists, removable USB storage, different WebView versions, launcher startup and all dial events require real-unit testing. The app does not connect to the head unit's FM/AM tuner, Bluetooth calling, DSP/equalizer, cameras, Android Auto or CarPlay; use the unit's own apps for those. It does not replace firmware or claim the supported functions of a manufacturer app. It does not run as an Android Auto projected app on a phone.

## Build

Keep this `android/` folder next to the repository `assets/` folder, open this folder in Android Studio, install Android SDK Platform 35 and Build Tools 35.0.0, and run `gradlew assembleDebug` or `gradlew assembleRelease`. Gradle wrapper 8.11.1 uses a pinned checksum. Android Gradle Plugin 8.9.0 requires JDK 17 or later. The release build is configured to use a local test signing key; set `DEH_DEBUG_KEYSTORE` to the original preview keystore if you need compatible updates. A different signing key requires uninstalling the old app, which removes its data. Do not publish a private signing key. Production signing and a full device test are separate work.

## Sources

- Android local content and WebViewAssetLoader: https://developer.android.com/develop/ui/views/layout/webapps/load-local-content
- Android rotary events: https://developer.android.com/reference/android/view/InputDevice#SOURCE_ROTARY_ENCODER and https://developer.android.com/reference/android/view/MotionEvent#AXIS_SCROLL
- Home apps: https://developer.android.com/work/dpc/dedicated-devices/cookbook#custom-home-apps
- Original animations: https://github.com/youxufkhan/carozerra
