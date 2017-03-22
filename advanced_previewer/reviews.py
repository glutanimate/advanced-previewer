# -*- coding: utf-8 -*-

"""
This file is part of the Advanced Previewer add-on for Anki

Card review methods extending the Previewer and Scheduler

Copyright: Glutanimate 2016-2017
License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from __future__ import division
import time

from anki.lang import _
from anki.consts import *

from aqt.utils import tooltip

from .consts import *
from .config import loadConfig
from .utils import trySetAttribute, transl


def updatePreviewAnswers(self):
    """Update review area of the previewer"""

    config = loadConfig()

    if not config["rev"][0]: # reviewing disabled
        return

    if config["rev"][3] and self._previewState != "answer": # only answer side
        self._previewRevArea.hide()
        return

    c = self.card
    sched = self.mw.col.sched
    early = c.queue != 0 and sched.today < c.due # not new, not due yet

    ret = False
    ahead = False
    if c.queue in (-1, -2): # buried or suspended
        self._previewAnsInfo.setText(
            transl("Buried or suspended cards cannot be reviewed"))
        self._previewAnsInfo.show()
        self._previewAns.hide()
        ret = True
    elif early and c.queue == 2: # early reviews
        if config["rev"][1]: # ahead of schedule enabled
            self._previewAnsInfo.setText(
                transl("Review Ahead of Schedule:"))
            self._previewAnsInfo.show()
            self._previewAns.show()
            ahead = True
        else:
            self._previewAnsInfo.setText(
                transl("Card is not due, yet"))
            self._previewAnsInfo.show()
            self._previewAns.hide()
            ret = True
    elif early and c.queue == 3: # early day learning cards
        self._previewAnsInfo.setText(
            transl("Day learning cards cannot be reviewed ahead"))
        self._previewAnsInfo.show()
        self._previewAns.hide()
        ret = True
    else: # scheduled reviews, regular learning cards, and new cards
        self._previewAnsInfo.hide()
        self._previewAns.show()

    if ret:
        self._previewRevArea.show()
        return

    # buttons and shortcuts

    sched._previewAnsEarly = ahead # early review?
    cnt = sched.answerButtons(c)
    if cnt == 2:
        answers = [_("Again"), _("Good"), None, None]
    elif cnt == 3:
        answers = [_("Again"), _("Good"), _("Easy"), None]
    elif cnt == 4:
        answers = [_("Again"), _("Hard"), _("Good"), _("Easy")]
    ease = 0
    for ans, btn, lbl in zip(answers,
      self._previewAnsBtns, self._previewAnsLbls):
        ease += 1
        if not ans:
            btn.hide()
            lbl.hide()
            continue
        btn.setText(ans)
        btn.show()
        if not self.mw.col.conf['estTimes']: # answer times disabled
            lbl.hide()
            continue
        ivl = sched.nextIvlStr(c, ease, True)
        lbl.setText(ivl)
        lbl.show()

    sched._previewAnsEarly = False # reset review mode
    self._previewAnsAhead = ahead # save review mode for onPreviewAnswer

    self._previewRevArea.show()
    self._previewAnswers = answers
    self._previewTimer = time.time()

def onPreviewAnswer(self, ease):
    """Answer card with given ease"""

    config = loadConfig()

    sched = self.mw.col.sched
    c = self.card
    answers = self._previewAnswers

    # sanity checks, none of these should ever be triggered
    if not c: # no card
        return
    if sched.answerButtons(c) < ease: # wrong ease
        return
    if c.queue in (-1, -2): # suspended/buried
        return

    # set queue attributes if not set
    for attr in ("newCount", "revCount", "lrnCount"):
        trySetAttribute(sched, attr, 1)

    for attr in ("_newQueue", "_lrnQueue", "_revQueue"):
        trySetAttribute(sched, attr, [])

    if c.queue == 0: # new
        if c.id not in sched._newQueue:
            sched._newQueue.append(c.id)
    elif c.queue in (1, 3): # lrn
        if c.id not in sched._lrnQueue:
            sched._lrnQueue.append(c.id)
    elif c.queue == 2: # new
        if c.id not in sched._revQueue:
            sched._revQueue.append(c.id)

    c.timerStarted = self._previewTimer

    print("==========================================")

    sched._previewAnsEarly = self._previewAnsAhead # early review?
    sched.answerCard(c, ease)

    print("after review")
    print("c.due", c.due)
    print("c.ivl", c.ivl)
    print("c.factor", c.factor)

    # reset attributes:
    sched._previewAnsEarly = False
    c.timerStarted = None
    # save:
    self.mw.autosave()
    self.mw.requireReset()
    self.model.reset()
    tooltip(answers[ease-1], period=2000)

    if config["rev"][2]: # automatically switch to next card
        self.onNextCard()

def nextRevIvl(self, card, ease, _old):
    "Ideal next interval for CARD, given EASE. Adjusted for early cards."

    if not getattr(self, "_previewAnsEarly", False): # regular review
        return _old(self, card, ease) # go back to default method
    if self.today >= card.due: # sanity check, should never be triggered
        return _old(self, card, ease)

    conf = self._revConf(card)

    # LEGEND

    # card.factor:  ease factor of card per mille (e.g. 2500 for 250%)
    # card.ivl:     card interval in days
    # card.due:     due date in days since collection was created
    # self.today:   today's date in days since collection was created
    # conf[ease4]:  ease bonus factor for cards marked as easy (e.g. 1.5)
    
    # EASE FACTOR CALCULATION

    # This is the formula used in _dynIvlBoost() for studying ahead
    # (ease averaged with "hard" ease, leading to a potentially 
    # severe penalty for reviewing cards only a few days ahead of
    # schedule)
    
    #fct = ((card.factor/1000)+1.2)/2

    # Instead, we use the formula for regular reviews (no ease penalty):

    fct = card.factor / 1000

    # (credits to rjgoif on the Anki support forums for discovering
    # this issue and the potential solution)

    # ELAPSED TIME CALCULATION

    # In calculating the new interval below, we factor in how many days
    # of the current interval have actually passed:

    elapsed = card.ivl - (card.due - self.today)

    # INTERVAL CALCULATION

    # These are based on the formulas for regular reviews, with two major
    # differences:
    #
    # 1.) We don't apply any ivl-specific weighting factor to the difference
    #     between due date and actual review date. I've experimented with
    #     using weighting factors, but I haven't been able to find any sensible
    #     values to apply
    # 2.) Instead of using self._constrainedivl, which factors in the 
    #     interval factor and increments each ivl by at least one day, we
    #     use a simpler approach with max(), similar to the default calculation
    #     for studying ahead

    # As you can see, the minimum interval across all eases is the current
    # interval of the card. This follows how _dynIvlBoost() works.
    # For that reason the intervals you will be presented with will often be
    # the same for all cards (just like the custom study option only offers
    # "good" as an answer for cards studied ahead).
    #
    # As the scheduled due date draws closer these intervals will start to
    # diverge, ever coming closer to the intervals you would see if you
    # were to review the card when it's actually due

    ivl2 = int(max(elapsed * 1.2, card.ivl, 1)) # hard (default fct = 1.2)
    ivl3 = int(max(elapsed * fct, ivl2, 1)) # good
    ivl4 = int(max(elapsed * fct * conf['ease4'], ivl3, 1)) # easy

    print("--------------------------------")
    print("card.ivl", card.ivl)
    print("elapsed", elapsed)
    print ("delta to due", card.due - self.today)
    print("fct", fct)
    print("ivl2", ivl2)
    print("ivl3", ivl3)
    print("ivl4", ivl4)

    if ease == 2:
        interval = ivl2
    elif ease == 3:
        interval = ivl3
    elif ease == 4:
        interval = ivl4
    # interval capped?
    return min(interval, conf['maxIvl'])
