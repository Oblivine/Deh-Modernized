# DEH Modernized

A complete, interactive Eonon X3 interface prototype with a Y2K cybercore skin: blackened liquid-chrome controls, original Pioneer OEL animations and Amber/Cyan illumination.

![Cyan player](docs/previews/cyan.png)

## Run it

Download this repository using **Code → Download ZIP**, extract it, and open **index.html** in Chrome or Edge. The complete player and all assets are in this repository; no external ZIP or CDN is required. A local static server also works.

## Controls and appearance

- **Settings → Display → Illumination** switches between Amber and Original cyan. The interface and monochrome animation files change together. The 24 original full-color clips retain their colors.
- All **83 original clips** are included at their native resolution. The Movies picker shows all 17 movies at head-unit size; tap one to play it.
- Click the **left half** of the playing animation for the previous movie and the **right half** for the next. Shuffle advances after a clip finishes and avoids repeats through the cycle.
- Animated clips stay in motion independently of music play/pause. There is no animation-pause option or song-seeking slider.
- Scanlines, glow and edge shading apply **only to the animation**. The display backdrop is pure black.
- The supplied **Accessories Urban** font is embedded for local playback. The liquid-chrome header is one continuous frame; its controls have no individual boxes.
- Source selection, volume, radio presets, 16-band EQ, audio settings, auto-dimming and saved preferences are interactive. Audio, radio and hardware connections are demonstrations.

![Amber player](docs/previews/amber.png)

## Source and checks

`source/` contains the editable interface, asset builders, pinned animation manifest and skin sources. `tools/build.py` rebuilds the root player from these files. Python 3 is sufficient for the UI build; regenerating the animation files additionally requires Pillow.

`docs/` contains frame/palette verification, browser checks, hardware evidence and desktop stress measurements. These desktop tests do not certify X3 performance. See [FEASIBILITY.md](FEASIBILITY.md).

**This is a browser prototype. No flashable firmware image is included.**

## Credits

- [Carozerra original animations and reference display effects](https://github.com/youxufkhan/carozerra)
- [X3 firmware investigation](https://github.com/prasys/eannon-x3-fw-reverse)
- Lucide icons: see `assets/LUCIDE-LICENSE`.
- Accessories Urban font supplied by the project owner; original TTF retained in `assets/fonts/`.
