# -*- coding: utf-8 -*-

"""
This file is part of the Advanced Previewer add-on for Anki

General previewer user interface

Copyright: Glutanimate 2016-2017
License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html
"""

# import modules this add-on depends on
import re

import aqt
from aqt.qt import *
from aqt.browser import Browser
from aqt.webview import AnkiWebView

from aqt.utils import getBase, mungeQA, openLink, saveGeom, restoreGeom
from anki.hooks import wrap
from anki.sound import clearAudioQueue, playFromText, play
from anki.js import browserSel
from anki.utils import json

from .html import *
from .config import loadConfig
from .utils import trySetAttribute, transl

# Shortcuts for each ease button
PRIMARY_KEYS = (Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4) # 1,2,3,4
SECONDARY_KEYS = (Qt.Key_J, Qt.Key_K, Qt.Key_L, Qt.Key_Odiaeresis) # J,K,L,Ö

# support for JS Booster add-on
try:
    from jsbooster.location_hack import getBaseUrlText, stdHtmlWithBaseUrl
    preview_jsbooster = True
except ImportError:
    preview_jsbooster = False

def onTogglePreview(self):
    """only used to set the link handler after loading the preview window
    (required in order to be compatible with "Replay Buttons on Card")"""
    if self._previewWindow:
        self._previewWeb.setLinkHandler(self._previewLinkHandler)

def openPreview(self):
    """Creates and launches the preview window"""
    # Initialize a number of variables used by the add-on:
    config = loadConfig()


    if config["dsp"][0]:
        trySetAttribute(self, "_previewBoth", True) 
    else:
        trySetAttribute(self, "_previewBoth", False)
    if self._previewBoth:
        self._previewState = "answer"
    else:
        self._previewState = "question"

    self._previewCurr = [] # list of currently previewed card ids
    self._previewLinkClicked = False # indicates whether user clicked on card in preview

    # Set up window and layout:
    self._previewWindow = QDialog(None, Qt.Window)
    self._previewWindow.setWindowTitle(_("Preview"))
    self._previewWindow.finished.connect(self._onPreviewFinished)
    vbox = QVBoxLayout()
    vbox.setContentsMargins(0,0,0,0)

    # Set up web view
    self._previewWeb = AnkiWebView()
    self._previewWeb.setLinkHandler(self._previewLinkHandler) # set up custom link handler
    vbox.addWidget(self._previewWeb, 10)

    # Set up buttons:
    bottom = QWidget()
    bottom_l = QHBoxLayout()
    bottom_l.setContentsMargins(0,0,0,5)
    bottom.setLayout(bottom_l)
    bottom.setMaximumHeight(80)
    left = QHBoxLayout()
    right = QHBoxLayout()
    left.setAlignment(Qt.AlignBottom)
    right.setAlignment(Qt.AlignBottom)
    left.setContentsMargins(0,0,0,0)
    right.setContentsMargins(0,0,0,0)

    # 1: answer buttons
    if config["rev"][0]: # reviewing enabled?
        self._setupPreviewRev(left)

    # 2: other buttons
    bbox = QDialogButtonBox()
    self._previewToggle = bbox.addButton(transl("Both sides"), QDialogButtonBox.ActionRole)
    self._previewToggle.setAutoDefault(False)
    self._previewToggle.setShortcut(QKeySequence("B"))
    self._previewToggle.setToolTip(_("Shortcut key: %s" % "B"))
    self._previewToggle.setCheckable(True)
    self._previewToggle.setChecked(self._previewBoth)
    self._previewReplay = bbox.addButton(_("Replay Audio"), QDialogButtonBox.ActionRole)
    self._previewReplay.setAutoDefault(False)
    self._previewReplay.setShortcut(QKeySequence("R"))
    self._previewReplay.setToolTip(_("Shortcut key: %s" % "R"))
    self._previewPrev = bbox.addButton("<", QDialogButtonBox.ActionRole)
    self._previewPrev.setAutoDefault(False)
    self._previewPrev.setShortcut(QKeySequence("Left"))
    self._previewPrev.setToolTip(_("Shortcut key: Right arrow"))
    self._previewNext = bbox.addButton(">", QDialogButtonBox.ActionRole)
    self._previewNext.setToolTip(_("Shortcut key: Right arrow or Enter"))
    self._previewNext.setAutoDefault(True)
    self._previewNext.setShortcut(QKeySequence("Right"))

    self._previewToggle.clicked.connect(self._onPreviewModeToggle)
    self._previewPrev.clicked.connect(self._onPreviewPrev)
    self._previewNext.clicked.connect(self._onPreviewNext)
    self._previewReplay.clicked.connect(self._onReplayAudio)

    right.addWidget(bbox)
    bottom_l.addLayout(left)
    bottom_l.addLayout(right)

    # Hotkeys

    undoCut = QShortcut(QKeySequence(_("Ctrl+Z")), 
            self._previewWindow, activated=self.mw.onUndo)
    susCut = QShortcut(QKeySequence(_("Ctrl+J")), 
            self._previewWindow, activated=self.onSuspend)
    susCut = QShortcut(QKeySequence(_("Ctrl+K")), 
            self._previewWindow, activated=self.onMark)
    startCut = QShortcut(QKeySequence(_("Alt+Home")), 
            self._previewWindow, 
            activated=lambda: self._onPreviewMove("s"))
    endCut = QShortcut(QKeySequence(_("Alt+End")), 
            self._previewWindow, 
            activated=lambda: self._onPreviewMove("e"))
    nextCut = QShortcut(QKeySequence(_("Alt+PgDown")), 
            self._previewWindow, 
            activated=lambda: self._onPreviewMove("n"))
    prevCut = QShortcut(QKeySequence(_("Alt+PgUp")), 
            self._previewWindow, 
            activated=lambda: self._onPreviewMove("p"))

    # Set up window and launch preview
    vbox.addWidget(bottom, 0)
    self._previewWindow.setLayout(vbox)
    restoreGeom(self._previewWindow, "preview")
    self._previewWindow.show()
    self._renderPreview(True)

def onPreviewMove(self, target):
    """Move row selection to new target"""
    if target == "s":
        self.form.tableView.selectRow(0)
    elif target == "e":
        max = self.model.rowCount(None)
        self.form.tableView.selectRow(max-1)
    elif target == "p":
        self.onPreviousCard()
    elif target == "n":
        self.onNextCard()

def setupPreviewRev(self, layout):
    """Sets up review area of the preview window"""
    self._previewRevArea = QWidget()
    review_layout = QVBoxLayout()
    review_layout.setContentsMargins(0,0,0,0)
    self._previewRevArea.setLayout(review_layout)

    self._previewAns = QWidget()
    answer_layout = QHBoxLayout()
    answer_layout.setContentsMargins(0,0,0,0)
    self._previewAns.setLayout(answer_layout)

    self._previewAnsBtns = []
    self._previewAnsLbls = []

    for idx in range(1,5):
        v = QVBoxLayout()
        btn = QPushButton("", self._previewWindow)
        btn.clicked.connect(lambda _, o=idx: self._onPreviewAnswer(o))
        btn.setToolTip(_("Shortcut key: %s" % str(idx)))
        # primary and secondary hotkeys:
        act1 = QAction(self._previewWindow, triggered=btn.animateClick)
        act1.setShortcut(QKeySequence(PRIMARY_KEYS[idx-1]))
        act2 = QAction(self._previewWindow, triggered=btn.animateClick)
        act2.setShortcut(QKeySequence(SECONDARY_KEYS[idx-1]))
        btn.addActions([act1, act2])
        # labels
        btn.setAutoDefault(False)
        btn.setAutoRepeat(False)
        btn.setToolTip(_("Shortcut key: %s" % str(idx)))
        label = QLabel("")
        label.setAlignment(Qt.AlignCenter)
        v.addWidget(label)
        v.addWidget(btn)
        answer_layout.addLayout(v)
        self._previewAnsBtns.append(btn)
        self._previewAnsLbls.append(label)

    self._previewAnsInfo = QLabel()
    self._previewAnsInfo.setAlignment(Qt.AlignCenter)

    review_layout.addWidget(self._previewAnsInfo)
    review_layout.addWidget(self._previewAns)

    self._previewRevArea.hide()
    layout.addWidget(self._previewRevArea)

def updatePreviewButtons(self):
    """Toggle next/previous buttons"""
    if not self._previewWindow:
        return
    current = self.currentRow()
    # improve the default behaviour of the previewer:
    canBack = (current > 0 or (current == 0 and self._previewState == "answer" 
            and not self._previewBoth))
    self._previewPrev.setEnabled(not not (self.singleCard and canBack))
    canForward = self.currentRow() < self.model.rowCount(None) - 1 or \
                 self._previewState == "question"
    self._previewNext.setEnabled(not not (self.singleCard and canForward))

def onPreviewPrev(self):
    if self._previewState == "answer" and not self._previewBoth:
        self._previewState = "question"
        self._renderPreview()
    else:
        self.onPreviousCard()
    self._updatePreviewButtons()

def onPreviewNext(self):
    if self._previewState == "question":
        self._previewState = "answer"
        self._renderPreview()
    else:
        self.onNextCard()
    self._updatePreviewButtons()

def onPreviewModeToggle(self):
    """Switches between preview modes ('front' vs 'back and front')"""
    self._previewBoth = self._previewToggle.isChecked()
    if self._previewBoth:
        self._previewState = "answer"
    else:
        self._previewState = "question"
    self._renderPreview()

def previewLinkHandler(self, url):
    """Executed when clicking on a card"""
    if url.startswith("focus"):
        # bring card into focus
        cid = int(url.split()[1])
        self._previewLinkClicked = True
        self.focusCid(cid)
    elif url.startswith("tagdeck"):
        # support for anki-reviewer-clickable-tags
        tag = url.split()[1]
        deck = self.mw.col.decks.name(self.card.did)
        search = 'tag:{0} deck:"{1}"'.format(tag, deck)
        browser = aqt.dialogs.open("Browser", self.mw)
        # not using setfilter because it grabs keyboard modifiers
        browser.form.searchEdit.lineEdit().setText(search)
        browser.onSearch()
    elif url.startswith("ankiplay"):
        # support for 'Replay Buttons on Card' add-on
        clearAudioQueue() # stop current playback
        play(url[8:])
    else:
        # handle regular links with the default link handler
        openLink(url)

def scrollToPreview(self, cid):
    """Adjusts preview window scrolling position to show supplied card"""
    self._previewWeb.eval("""
        const elm = document.getElementById('%i');
        const elmRect = elm.getBoundingClientRect();
        const absElmTop = elmRect.top + window.pageYOffset;
        const elmHeight = elmRect.top - elmRect.bottom
        const middle = absElmTop - (window.innerHeight/2) - (elmHeight/2);
        window.scrollTo(0, middle);
        toggleActive(elm);
        """ % cid)

def renderPreview(self, cardChanged=False):
    """Generates the preview window content"""
    if not self._previewWindow:
        return

    oldfocus = None
    cids = self.selectedCards()
    multi = len(cids) > 1 # multiple cards selected?
    if not cids:
        txt = "Please select one or more cards"
        self._previewWeb.stdHtml(txt)
        self._updatePreviewButtons()
        return

    if cardChanged and not self._previewBoth:
        self._previewState = "question"

    self._updatePreviewAnswers()

    if not multi and cids[0] in self._previewCurr:
        # moved focus to another previously selected card
        if cardChanged:
            # focus changed without any edits
            if not self._previewLinkClicked and len(self._previewCurr) > 1:
                # only scroll when coming from browser and multiple cards shown
                self.scrollToPreview(cids[0])
            self._previewLinkClicked = False
            return
        else:
            # focus changed on card edit
            oldfocus = cids[0]
            cids = self._previewCurr
            multi = len(cids) > 1   

    txt = ""
    css = self.mw.reviewer._styles() + preview_css
    html = u"""<div id="{0}" class="card card{1}">{2}</div>"""
    # RegEx to remove multiple imports of external JS/CSS (JS-Booster-specific)
    jspattern = r"""(<script type=".*" src|<style>@import).*(</script>|</style>)"""
    scriptre = re.compile(jspattern)
    js = browserSel
    if multi:
        # only apply custom CSS and JS when previewing multiple cards
        html = u"""<div id="{0}" onclick="py.link('focus {0}');toggleActive(this);" \
               class="card card{1}">{2}</div>"""
        css += multi_preview_css
        js += multi_preview_js
    for idx, cid in enumerate(cids):
        # add contents of each card to preview
        c = self.col.getCard(cid)
        if self._previewState == "answer":
            ctxt = c.a()
        else:
            ctxt = c.q()
        # Remove subsequent imports of external JS/CSS
        if idx >= 1:
            ctxt = scriptre.sub("", ctxt)
        txt += html.format(cid, c.ord+1, ctxt)
    txt = re.sub("\[\[type:[^]]+\]\]", "", txt)
    ti = lambda x: x
    base = getBase(self.mw.col)
    if preview_jsbooster:
        # JS Booster available
        baseUrlText = getBaseUrlText(self.mw.col) + "__previewer__.html"
        stdHtmlWithBaseUrl(self._previewWeb,
            ti(mungeQA(self.col, txt)), baseUrlText,
            css, head=base, js=browserSel + multi_preview_js)
    else:
        # fall back to default
        self._previewWeb.stdHtml(
            ti(mungeQA(self.col, txt)), css, head=base, js=js)

    if oldfocus and multi:
        self.scrollToPreview(oldfocus)
    self._previewCurr = cids
    if multi:
        self._previewPrev.setEnabled(False)
        self._previewNext.setEnabled(False)
    else:
        self._updatePreviewButtons()
    clearAudioQueue()
    if not multi and self.mw.reviewer.autoplay(c):
        playFromText(txt)


def updatePreviewHtml(self, note):
    replacements = self._selectiveCardRender(note)
    for cid, html in replacements.items():
        self._previewWeb.eval(
            js_replace.format(str(cid), json.dumps(html)))
    self.scrollToPreview(cid)


def selectiveCardRender(self, note):
    cards = note.cards()
    replacements = {}
    for card in cards:
        cid = card.id
        if self._previewState == "answer":
            inner_html = card.a()
        else:
            inner_html = card.q()
        replacements[cid] = inner_html
    return replacements

js_replace = u"""
const elm = document.getElementById('{}');
elm.innerHTML = {}
"""

def refreshCurrentCard(self, note):
    self.model.refreshNote(note)
    self.updatePreviewHtml(note)
