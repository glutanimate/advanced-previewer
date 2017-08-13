This is the add-on description for Advanced Previewer, as found on [AnkiWeb](https://ankiweb.net/shared/info/544521385).

-------------

Extends the card preview window with the following new features:

- **Preview multiple cards** at once
- **Review cards** from the previewer
- **Show question or answer side** by default

![screenshot of the add-on](https://github.com/Glutanimate/advanced-previewer/blob/master/screenshots/combined.png?raw=true)

**COMPATIBILITY**

This add-on only works with Anki's stable release branch (2.0.x ≥ 2.0.30). The 2.1 beta branch is **not supported** at this point in time.

**RELEASE LOG**

2017-08-05: **v0.4.1** – A few new features and major performance improvements
2017-03-23: **v0.3.2** – Completely reworked the add-on, introducing card reviewing and a new options menu
2016-12-09: **v0.2.1** – Added support for the "Replay Buttons on Card" and "JS Booster" add-ons
2016-12-04: **v0.2.0** – Initial public release

**LATEST CHANGES AND NEWS**

2017-08-05 – **v0.4.1**

- Major performance improvements to card rendering
- Support for third-party extensions
- Confirmation dialog when invoking previewer on a large number of flashcards (>= 200)
- Delete hotkey (Alt+Del)
- Smaller bug fixes and improvements

**USAGE**

Most of the features should be pretty self-explanatory, but I've recorded a quick video demonstration that should help you get started with the add-on:

[![YouTube: Anki Add-on: Advanced Previewer](https://i.ytimg.com/vi/GcilF4S0QMc/mqdefault.jpg)](https://youtu.be/GcilF4S0QMc)

**ADDITIONAL FEATURES**

Aside from the three main features mentioned above, Advanced Previewer also updates the previewer window in the following ways:

- fixes a number of [smaller inconsistencies](https://github.com/dae/anki/pull/181) when navigating cards
- adds the ability to mark (`CTRL+M`) and suspend (`CTRL+J`) cards while the previewer is active
- adds five hotkeys to the previewer:
    - `ALT+Home`: go to first card
    - `ALT+End`: go to last card
    - `ALT+PgUp` to jump to previous card, skipping q/a sides
    - `ALT+PgDwn` to jump to next card, skipping q/a sides
    - `ALT+Delete` to delete current note selection

**OPTIONS**

Advanced Previewer comes with a simple options menu which can be invoked through *Tools* → *Advanced Previewer Options...*. You can use this to enable card reviewing support, among other things:

![showcasing options menu](https://github.com/Glutanimate/advanced-previewer/blob/master/screenshots/options.png?raw=true)

**IMPORTANT NOTES**

*Add-on Incompatibilities*

Advanced Previewer is incompatible with the following add-ons:

- [' Editor fontsize](https://anki.tenderapp.com/discussions/add-ons/10639-advanced-previewer-error)

Other add-ons that overwrite the previewer functions will also not work with Advanced Previewer.

For add-on authors that are interested in adding support for Advanced Previewer to their add-ons: Please refer to [anki-previewer-tagbrowser. py](https://github.com/glutanimate/anki-addons-misc/blob/master/anki-previewer-tagbrowser.py) for an example of how third-party add-ons can be integrated into the previewer.

*Performance Considerations*

Rendering multiple cards at once can be taxing on the system, so please don't try invoking the preview window on too many items. A couple hundred or so should still be fine in most cases.

*Reviewing Cards in Advance*

Advanced Previewer offers an option to review cards before their due date. This is disabled by default, but can be enabled through the options menu.

When reviewing cards in advance, please be mindful of the following:

- There are some [general caveats](https://apps.ankiweb.net/docs/manual.html#reviewingahead) to studying ahead which you should be aware of.
- In contrast to Anki's default custom study option, Advanced Previewer will present you with four answer buttons. These follow the same ease steps you see when reviewing cards regularly:
    + "Again" moves the card into the relearn queue
    + "Hard", "Good", and "Easy" will reschedule the card using the same ease as regular reviews, but also take the earliness of the review into account. For cards that are reviewed very early you will be presented with three very similar intervals because it's too early to draw viable conclusions on your actual review performance. As the scheduled due date draws nearer these intervals will start to diverge, ever moving closer to the intervals you would see if you were to review the card when it's actually due.
- Advanced Previewer implements a variation of the formula found in the [Remove "study ahead" penalty](https://ankiweb.net/shared/info/1607819937) add-on by rjgoif. The intervals scheduled by the add-on can stray pretty far from what you'd see when reviewing cards ahead in a custom study session. Please make sure to read the original add-on description linked above for more information on the rationale behind implementing this algorithm.

**CREDITS AND LICENSE**

*Advanced Previewer* is *Copyright © 2016-2017 [Aristotelis P.](https://github.com/Glutanimate)*

This add-on was originally developed on a commission by [BB on the Anki support forums](https://anki.tenderapp.com/discussions/add-ons/8504-100-for-add-on-developer). The card reviewing feature introduced in the latest update was commissioned by another fellow Anki user who would like to remain anonymous. I would like to thank both of them for their great ideas and generous support in writing this add-on.

Licensed under the [GNU AGPL v3](https://www.gnu.org/licenses/agpl.html). The source code for this add-on is available on [GitHub](https://github.com/Glutanimate/advanced-previewer).

**MORE RESOURCES**

A lot of my add-ons were commissioned by other Anki users. If you enjoy my work and would like to hire my services to work on an add-on or new feature, please feel free to reach out to me at:  ![Email icon](https://glutanimate.com/logos/email.svg) <em>ankiglutanimate [αt] gmail . com</em>

Want to stay up-to-date with my latest add-on releases and updates? Feel free to follow me on Twitter: [![Twitter bird](https://glutanimate.com/logos/twitter.svg)@Glutanimate](https://twitter.com/glutanimate)

New to Anki? Make sure to check out my YouTube channel where I post weekly tutorials on Anki add-ons and related topics: [![YouTube playbutton](https://glutanimate.com/logos/youtube.svg) / Glutanimate](https://www.youtube.com/c/glutanimate)