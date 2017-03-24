This is the add-on description for Advanced Previewer, as found on [AnkiWeb](https://ankiweb.net/shared/info/544521385).

-------------

Extends the card previewer window with the following new features:

- **Preview multiple cards** at once
- **Review cards** from the previewer
- **Show question or answer side** by default

![showcasing multiple card previews](https://github.com/Glutanimate/advanced-previewer/blob/master/screenshots/multiple-cards.png?raw=true)

![showcasing card reviewing support](https://github.com/Glutanimate/advanced-previewer/blob/master/screenshots/card-reviews.png?raw=true)

![showcasing options menu](https://github.com/Glutanimate/advanced-previewer/blob/master/screenshots/options.png?raw=true)

**Changelog**

- 2017-03-23 – Completely reworked add-on from the ground up, introducing card reviewing and a new options menu
- 2016-12-09 – Added support for the "Replay Buttons on Card" and "JS Booster" add-ons
- 2016-12-04 – Initial release

**Update Notice**

**This update introduces a new add-on structure, so please make sure to remove any previous versions of the add-on you might have installed before updating to the latest release.**

**Usage**

Most of the features should be pretty self-explanatory, but I've recorded a quick video demonstration that should help you get started with the add-on:

[![YouTube: Anki Add-on: Advanced Previewer](https://i.ytimg.com/vi/?/mqdefault.jpg)](https://youtu.be/?)

**Options**

Advanced Previewer comes with a simple options menu which can be invoked through *Tools* → *Advanced Previewer Options...*. You can use this to enable card reviewing support, among other things.

**Important Remarks**

*Performance considerations*

Rendering multiple cards at once can be taxing on the system, so please don't try invoking the preview window on too cards notes. A couple hundred or so should still be fine in most cases.

*Reviewing cards in advance*

Advanced Previewer offers an option to review cards before their due date. This is disabled by default, but can be enabled through the options menu.

When reviewing cards in advance, please be mindful of the following:

- There are some [caveats](https://apps.ankiweb.net/docs/manual.html#reviewingahead) to studying ahead which you should be aware of.
- In contrast to Anki's default custom study option, Advanced Previewer will present you with 4 answer buttons. These follow the same ease steps you see when reviewing cards regularly:
    + "Again" behaves in the same way as the corresponding custom study option, moving the card into the relearn queue
    + "Hard", "Good", and "Easy" will reschedule the card using the same ease as regular reviews, but also take the earliness of the review into account. For cards that are reviewed very early you will be presented with intervals that are very similar - if not identical - to each other. As the scheduled due date draws nearer these intervals will start to diverge, ever moving closer to the intervals you would see if you were to review the card when it's actually due.
- Advanced Previewer implements a variation of the formula found in the [Remove "study ahead" penalty](https://ankiweb.net/shared/info/1607819937) add-on by rjgoif in order to avoid drastic interval penalties for reviewing cards just a few days ahead of schedule. For that reason the intervals scheduled by the add-on can stray pretty far from what you'd see when reviewing cards ahead in a custom study session. Please make sure to read the add-on description linked above for more information on the rationale behind this change.

**Credits and License**

*Advanced Previewer* is *Copyright © 2016-2017 [Aristotelis P.](https://github.com/Glutanimate)*

This add-on was originally developed on a commission by [BB on the Anki support forums](https://anki.tenderapp.com/discussions/add-ons/8504-100-for-add-on-developer). The card reviewing feature introduced in the latest update was commissioned by another fellow Anki user who would like to remain anonymous. I would like to thank both of them for their great ideas and generous support in writing this add-on.

If you have an idea for an add-on or new feature, please feel free to reach out to me on [Twitter](https://twitter.com/glutanimate), or at glutanimate [αt] gmail . com.

Licensed under the [GNU AGPL v3](https://www.gnu.org/licenses/agpl.html).