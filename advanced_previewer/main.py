# -*- coding: utf-8 -*-

"""
This file is part of the Advanced Previewer add-on for Anki

Main Module, hooks add-on methods into Anki

Copyright: Glutanimate 2016-2017
License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from aqt import mw

from aqt.browser import Browser
from anki.sched import Scheduler

from anki.hooks import wrap, addHook

from .previewer import *
from .reviews import *
from .config import AdvPrevOptions

# Menus

def onAdvPrevOptions(mw):
    """Invoke global config dialog"""
    dialog = AdvPrevOptions(mw)
    dialog.exec_()

options_action = QAction("A&dvanced Previewer Options...", mw)
options_action.triggered.connect(lambda _, m=mw: onAdvPrevOptions(m))
mw.form.menuTools.addAction(options_action)

# Add-on setup

def setupAddon():
    loadConfig()

# Monkey patches and hooks into Anki's default methods

addHook("profileLoaded", setupAddon)

Browser.onTogglePreview = wrap(Browser.onTogglePreview, onTogglePreview)
Browser.scrollToPreview = scrollToPreview
Browser._openPreview = openPreview
Browser._renderPreview = renderPreview
Browser._previewLinkHandler = previewLinkHandler
Browser._onPreviewModeToggle = onPreviewModeToggle
Browser._updatePreviewButtons = updatePreviewButtons
Browser._onPreviewPrev = onPreviewPrev
Browser._onPreviewNext = onPreviewNext

Browser._setupPreviewRev = setupPreviewRev
Browser._onPreviewAnswer = onPreviewAnswer
Browser._updatePreviewAnswers = updatePreviewAnswers

Scheduler._nextRevIvl = wrap(Scheduler._nextRevIvl, nextRevIvl, "around")