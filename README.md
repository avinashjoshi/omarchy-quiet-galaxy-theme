# Star Wars for Omarchy

A quiet, dark Star Wars theme for [Omarchy](https://omarchy.org): near-black
greys, grey text, and opening-crawl yellow as the one accent. The colours are
chosen for protanopia. The default wallpaper collection contains five cinematic AI-generated
wallpapers. Additional stills, line art and video loops are optional extras.

![Star Wars theme](preview.png)

## Install

```bash
omarchy theme install https://github.com/avinashjoshi/omarchy-star-wars-theme
```

Or pick **Star Wars** later from `omarchy theme switcher`.

## What's in it

**Palette** (`colors.toml`), which Omarchy turns into matching configs for
Hyprland, the terminals, btop, Neovim, VS Code, Chromium and the rest:

| Role | Colour | |
|---|---|---|
| Background | `#161617` | near-black, not pitch black, so panels and borders still read |
| Foreground | `#cfcfcf` | soft grey |
| Accent | `#ffe81f` | opening-crawl yellow |
| Blue | `#80a2f8` | saber blue, used for hover and focus |
| Borders | `#55555a` | visible on every surface |

The focused window gets a solid yellow border; the others get plain grey.

**Shell surfaces** (`shell.*.toml`): a dark bar with grey type, dark popups,
menus and notifications with a clear grey edge, yellow for the selected row
and for anything asking for attention.

**T3 Code** (`t3code.json`): neutral grey surfaces and input borders instead
of the accent-tinted ones T3 Code derives by default.

**Default backgrounds**: five AI-generated wallpapers in the normal picker
and rotation. The numbers match the full collection:

| # | Wallpaper | Native resolution |
|---|---|---|
| 13 | [Twin Suns](backgrounds/13-hero-twin-suns.png) | 1672 × 941 |
| 14 | [Blade](backgrounds/14-hero-blade.png) | 1672 × 941 |
| 16 | [Death Star](backgrounds/16-hero-death-star.png) | 1586 × 992 |
| 17 | [Crossed Blades](backgrounds/17-hero-crossed-blades.png) | 1586 × 992 |
| 18 | [Millennium Falcon](backgrounds/18-hero-millennium-falcon.png) | 1586 × 992 |

These are native generated PNGs without upscaling or intro animations.
Generation prompts are saved in `.art/hero-wallpapers/`.

### Optional wallpapers

[extras/backgrounds/](extras/backgrounds/) contains 15 optional wallpapers:
ten sparse line drawings, *Lightspeed Live*, *Starfield Live*, and the
cinematic *Battle Station*, *Galaxy*, and *Galaxy OLED*. They stay out of the
rotation until you add them.

[Galaxy](extras/backgrounds/19-hero-galaxy.png) is a sweeping blue spiral
galaxy with a small X-wing for scale, generated at 1586 × 992. Its prompt is
saved in `.art/hero-wallpapers/galaxy-prompt.txt`.

[Galaxy OLED](extras/backgrounds/20-hero-galaxy-oled.png) uses a thin blue
galactic arc and a small Millennium Falcon against true black. At its native
1586 × 992 resolution, 85.8% of pixels are exactly `#000000`. Generated with
the built-in image tool; the prompt is saved in
`.art/hero-wallpapers/galaxy-oled-prompt.txt`.

![The ten line-art wallpapers, cropped to their middles](.art/wallpapers.png)

To enable one extra, copy it into your personal wallpaper folder:

```bash
mkdir -p ~/.config/omarchy/backgrounds/star-wars
cp ~/.config/omarchy/themes/star-wars/extras/backgrounds/01-twin-suns.png \
   ~/.config/omarchy/backgrounds/star-wars/
```

To enable all extras, including the line-art intro animations:

```bash
mkdir -p ~/.config/omarchy/backgrounds/star-wars
cp -r ~/.config/omarchy/themes/star-wars/extras/backgrounds/. \
      ~/.config/omarchy/backgrounds/star-wars/
```

The line-art stills have matching three-second animations in
`extras/backgrounds/intros/`. Omarchy plays these on theme activation or boot
when the matching still is selected and intros are enabled. Disable them with
`omarchy theme bg intro disable`. The two video wallpapers are looping clips.
Personal wallpapers also join the rotation; a fresh install has just the five
defaults above.

**Icons**: `Yaru-yellow-dark`.

**Boot splash** (`unlock.png`): the twin suns, used if you run
`omarchy plymouth set by theme star-wars`.

## Official Star Wars art

The included cinematic wallpapers are AI-generated fan art, not official
artwork or film stills. StarWars.com also offers official backgrounds:

- [Star Wars backgrounds on StarWars.com](https://www.starwars.com/news/star-wars-backgrounds)
  (1920x1080; the starfield, hyperspace and Star Destroyer interiors suit this
  theme best)

Save the ones you like into `~/.config/omarchy/backgrounds/star-wars/` and
they join this theme's wallpaper rotation on your machine only
(`omarchy theme bg install` opens that folder).

## Built for protanopia

Protanopia removes the red-sensing cones. Red light looks dim, and red, orange
and green collapse toward the same yellow-brown, while blue against yellow
stays as clear as ever. So the theme is built on that axis:

- **States swing between blue and yellow or orange, never red and green.**
  Hover and focus are blue, selection is yellow, and a wrong password on the
  lock screen or a sudo prompt turns orange.
- **Red is a light coral** (`#f29080`), not a saturated red, which a protanope
  sees as a dark brown that sinks into the background.
- **Red and green differ in brightness as well as hue**, so a diff still reads
  when the hue difference is gone.
- **Purple is kept darker than blue**, because without red the two share a hue.
- **The line-art red blade** (*Dark Side*, in extras) keeps a white core, and its glow is a
  red light enough to hold 4.7:1 on the wallpaper under the simulation.

`.art/cvd.py` simulates protanopia (Machado, Oliveira & Fernandes 2009, full
severity) and measures two things on the simulated colours: contrast against
the background, and how far apart the meaningful colours stay. For this
palette:

| Colour | Hex | As a protanope sees it | Contrast on background |
|---|---|---|---|
| Foreground | `#cfcfcf` | `#cfcfcf` | 11.6:1 |
| Red | `#f29080` | `#a79e7e` | 6.7:1 |
| Orange | `#df7a21` | `#98860c` | 5.0:1 |
| Yellow | `#ffe81f` | `#ffe100` | 13.8:1 |
| Green | `#4ac855` | `#cbb749` | 8.9:1 |
| Cyan | `#69ffff` | `#f0f4ff` | 16.4:1 |
| Blue | `#80a2f8` | `#81aafc` | 7.8:1 |
| Magenta | `#be64f6` | `#2b89fb` | 5.2:1 |

Every pair among those colours, the comment grey and the text stays at least
0.113 apart in OKLab under the simulation (the bright set, 0.106), where about
0.02 is one just-noticeable step. Comment grey (`#7c7c82`) is deliberately
quieter at 4.4:1.

The preview above, run through the same simulation:

![Preview under simulated protanopia](.art/preview-protanopia.png)

This is a simulation, not a substitute for your own eyes. If two colours are
hard to tell apart for you, please open an issue.

## Regenerating

```bash
uv run --with numpy .art/cvd.py              # palette report
uv run --with numpy .art/cvd.py --search     # search for a better set of hues
uv run --with numpy --with pillow .art/generate.py stills    # wallpapers
uv run --with numpy --with pillow .art/generate.py videos    # intros and loops (needs ffmpeg, takes ~10 minutes)
uv run --with numpy --with pillow .art/generate.py emblem unlock-preview contact-sheet
```

## License

Theme configuration and procedural artwork code: MIT, see [LICENSE](LICENSE).
The AI-generated fan wallpapers are not a grant of rights to underlying
Star Wars intellectual property. This is an unofficial fan theme. Star Wars is a
trademark of Lucasfilm Ltd.; this project is not affiliated with or endorsed
by Lucasfilm or Disney. The line art is drawn by the script in `.art/`; the cinematic wallpapers are
AI-generated fan art. No film stills or logos are included. Star Wars names
and depicted franchise designs remain the property of their respective owners.
