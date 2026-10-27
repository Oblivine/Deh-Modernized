# DEH Modernized

A complete, interactive Eonon X3 interface prototype with a Y2K cybercore skin: recessed theme-tinted media keys, round icon navigation and a carbon-alloy header, original Pioneer OEL animations and Amber/Cyan illumination.

![Cyan player](docs/previews/cyan.png)

## Run it

Download this repository using **Code → Download ZIP**, extract it, and open **index.html** in Chrome or Edge. The complete player and all assets are in this repository; no external ZIP or CDN is required. A local static server also works.

## Controls and appearance

- **Settings → Display → Color** switches between Amber and Original cyan. The interface and monochrome animation files change together. The 24 original full-color clips retain their colors.
- All **83 original clips** are included at their native resolution. The gallery under Settings → Display → Dimmer → Animations shows all 17 movies at head-unit size; tap one to play it.
- Click the **left half** of the playing animation for the previous movie and the **right half** for the next. The shuffle key in the playback strip advances animation movies after a clip finishes and avoids repeats through the cycle. It does not shuffle the demo songs.
- Animated clips stay in motion independently of music play/pause. There is no animation-pause option or song-seeking slider.
- Scanlines, a restrained glow and edge shading apply **only to the animation**. The display backdrop is pure black.
- **Display → Font** offers Audiowide, Orbitron and the supplied Accessories Urban font. All three are embedded for local playback, and the choice is saved. Custom control emblems match the skin. Playback has separate previous, play, pause, stop and next keys; the larger, 64 px round navigation buttons form a widely spaced half-circle below them. The bottom corners open Backgrounds, Color and Meters. Meter channels are cropped from their original vertical arrangement and shown side by side across the display. The former Movies selector row is removed. The header is one continuous frame; the spiked emblem is removed. Buttons use the tinted media-player finish, with no chrome button frames.
- Source selection, volume, radio presets, 16-band EQ, audio settings, auto-dimming and saved preferences are interactive. Audio, radio and hardware connections are demonstrations.

![Amber player](docs/previews/amber.png)

## Source and checks

`source/` contains the editable interface, asset builders, pinned animation manifest and skin sources. `tools/build.py` rebuilds the root player from these files. Python 3 is sufficient for the UI build; regenerating the animation files additionally requires Pillow.

`docs/` contains frame/palette verification, browser checks, hardware evidence and desktop stress measurements. These desktop tests do not certify X3 performance. See [FEASIBILITY.md](FEASIBILITY.md).

**This is a browser prototype. No flashable firmware image is included.**

## Credits

- [Carozerra original animations and reference display effects](https://github.com/youxufkhan/carozerra)
- [X3 firmware investigation](https://github.com/prasys/eannon-x3-fw-reverse)
- Audiowide and Orbitron: Google Fonts, with their SIL Open Font License files in `assets/fonts/`.
- Accessories Urban font supplied by the project owner; original TTF retained in `assets/fonts/`.
