# Kanji Writing Practice
import sys
from os import path, environ
from threading import Thread
from typing import Union
# bundling pygame
sys.path.insert(0, path.dirname(__file__))

import pygame as pyg
from pygame._sdl2 import Window
import gui
import svg
from aqt import gui_hooks, mw
from aqt.utils import ask_user, show_warning

# monkey patching to prevent pygame from crashing anki (seems the wrap function doesn't work)
from aqt.qt import QWidget
def cancelKWP(self):
    if Deck.running:
        terminateKWP()
        Deck.paused = True
        show_warning("Kanji Writing Practice has been terminated due to an external window opening. Reload deck to reopen KWP.")
    self._ogshow(self)

QWidget._ogshow = QWidget.show
QWidget.show = cancelKWP

# def resumeKWP(self, event):
#     self._ogcloseEvent(self, event)
#     if Deck.paused:
#         kanjiWritingPractice()

# QWidget._ogcloseEvent = QWidget.closeEvent
# QWidget.closeEvent = resumeKWP

# config
config = mw.addonManager.getConfig(__name__)

def fixConfig():
    # 100 = max speed, 15 = min speed
    conSpeed = config["speed"]
    if "speed" in config and type(conSpeed) == int or type(conSpeed) == float:
        config["speed"] = max(min(int(conSpeed), 100), 15)
    else:
        config["speed"] = 65

    # # TODO: convert deckIDs in config to deck name automatically, also prevents config from being cluttered with custom studies
    # deckList = (config["blacklist"], config["whitelist"])
    # for i in deckList:
    #     for k in range(len(i)):
    #         print(mw.col.decks.get(i[k], False))
    #         try:
    #             pass
    #         except:
    #             pass

    mw.addonManager.writeConfig(__name__, config)
gui_hooks.main_window_did_init.append(fixConfig)

pyg.init()
clock = pyg.time.Clock()

# pygame screen
gui.initDisplay((300, 300), "Initializing", (-300, -300))

# -------------------- Classes --------------------
class Deck():
    """
    Processes the anki card, also has some gamestate attributes/methods
    """
    # card attributes
    prompt = []
    kanjiDict = {"X" : "X"}
    counter = 0
    kanji: Union[svg.Kanji, str] = "X"

    # pygame window attributes
    # NOTE: do not change the names of the x/y attributes, the deck class becomes a parameter for the resize screen function
    x = gui.screen.get_rect().w
    y = gui.screen.get_rect().h
    pos = None
    # pygame window is active
    running = False
    # exclusively for handling when KWP is paused by an Anki window GUI
    paused = False
    # user is allowed to draw
    active = False

    @classmethod
    def newCard(cls, question: str):
        cls.reset()
        for c in question:
            # if conditional taken from Kanji Colorizer: https://github.com/cayennes/kanji-colorize/blob/main/anki/kanji_colorizer.py
            if ord(c) >= 19968 and ord(c) <= 40879:
                if not c in cls.kanjiDict:
                    try:
                        # range inversion formula for points (so to the user, speed value is intuitive) (thanks issai)
                        cls.kanjiDict[c] = svg.Kanji(c, drawGUI.dimensions, Stroke.width, 100 - config["speed"] + 15)
                    except FileNotFoundError:
                        cls.prompt.append("X")
                        continue
                        # pyg.display.quit()
                        # raise FileNotFoundError(f"Could not find an svg file for this kanji: {c}")
                    except svg.SvgError:
                        pyg.display.quit()
                        raise svg.SvgError(f"An error occured while working with this kanji: {c}")
                cls.prompt.append(c)
        if not cls.prompt:
            cls.prompt.append("X")

    @classmethod
    def shouldContinue(cls):
        cls.counter += 1
        if cls.counter < len(cls.prompt):
            gui.GUI.deactivate(hintGUI, submitGUI)
            gui.GUI.activate(continueGUI)

    @classmethod
    def initKanji(cls):
        try:
            cls.kanji = cls.kanjiDict[cls.prompt[cls.counter]]
        except KeyError:
            cls.kanji = "X"
    
    @classmethod
    def reset(cls):
        cls.prompt = []
        cls.counter = 0

    # gamestate methods
    @staticmethod
    def clearCanvas():
        for i in Stroke.strokeGroup:
            i.points = []
            i.colors = []
            i.scale()
        gui.GUI.trueTransform(drawStroke, "set_alpha", 255)
        gui.GUI.disable(undoGUI)
        gui.GUI.deactivate(gradeGUI)

    @classmethod
    def newRound(cls):
        cls.initKanji()
        cls.clearCanvas()
        gui.GUI.deactivate(continueGUI, oldAccuracyGUI, retryGUI)
        gui.GUI.activate(undoGUI, hintGUI, submitGUI)

        if Deck.kanji == "X":
            gui.GUI.disable(drawGUI, hintGUI, submitGUI)
            promptGUI.write("X", "red")
            accuracyGUI.write("--%")
            Deck.shouldContinue()
        else:
            gui.GUI.enable(drawGUI, hintGUI, submitGUI)
            Animate.newAnimation(Deck.kanji)
            promptGUI.write(Deck.kanji.str)
            accuracyGUI.write("--%")

            cls.active = True

    @classmethod
    def retryRound(cls, *args):
        cls.counter -= 1
        cls.newRound()

    @classmethod
    def shouldEnable(cls, shouldEnable):
        # only should be called by ask_user
        if shouldEnable:
            prepKWP(mw.reviewer.card)
            config["whitelist"].append(deckID)
        else:
            config["blacklist"].append(deckID)
        mw.addonManager.writeConfig(__name__, config)

animateEvent = pyg.event.custom_type()
endAnimateEvent = pyg.event.custom_type()
class Animate():
    """
    Handles animating the kanji drawing
    """
    frame = None # Stroke object
    counter = 0
    endNow: bool = False
    animatedKanji: str = None

    @classmethod
    def newAnimation(cls, kanji: svg.Kanji):
        if kanji.pBzPoints == "N/A": # No animation
            gui.GUI.disable(hintGUI)
            hintGUI.changeState(3)
            return
        
        cls.counter = 0
        cls.endNow = False

        colors = ("red", "orange", "yellow", "green", "blue", "purple")
        cls.frame.colors = [colors[i%6] for i in range(len(kanji.pBzPoints))]

    @classmethod
    def begin(cls):
        if cls.endNow:
            return

        if cls.counter == 0:
            cls.frame.points.append([])
            cls.frame.initPos = tuple(i*gui.scale for i in Deck.kanji.pBzPoints[cls.currentFrame][0])

        cls.frame.draw(tuple(i*gui.scale for i in Deck.kanji.pBzPoints[Animate.currentFrame][cls.counter]), cls.currentFrame)

        cls.counter += 1
        if cls.counter == len(Deck.kanji.pBzPoints[cls.currentFrame]):
            cls.currentFrame += 1
            cls.counter = 0

        if cls.currentFrame == len(Deck.kanji.pBzPoints):
            cls.animatedKanji = Deck.kanji.str
            pyg.time.set_timer(endAnimateEvent, 2500, 1)
        else:
            pyg.time.set_timer(animateEvent, 1 if cls.counter != 0 else 250, 1)

    @classmethod
    def end(cls):
        if cls.animatedKanji != Deck.kanji.str or not Deck.active:
            return

        cls.frame.points = []
        cls.frame.scale()
        cls.counter = 0
        gui.GUI.enable(hintGUI)

    @classmethod
    def tryEnd(cls):
        cls.endNow = True
        Animate.animatedKanji = Deck.kanji.str
        cls.end()

class Stroke(pyg.sprite.Sprite):
    """
    Subclass of pygame's sprite class that handles every stroke drawn by the user\n
    An instance is created on the designated sprite\n
    """
    
    frame = pyg.image.load(gui.assetPath("frame.png")).convert_alpha()
    strokeGroup = pyg.sprite.Group()

    width = 8

    def __init__(self, sprite: pyg.sprite.Sprite):
        super().__init__()
        self.image = pyg.transform.scale(Stroke.frame, sprite.rect.size)
        self.rect = self.image.get_rect(center = sprite.rect.center)
        self.parent = sprite

        self.colors = []
        self.points = []

        Stroke.strokeGroup.add(self)

    def draw(self, finalPos: tuple[int, int], colorIndex: int = 0):
        """
        Draws a line on the frame\n
        Every new line should have a new list appended to self.points before drawing anything
        """
        self.points[-1].append(tuple(i/gui.scale for i in finalPos))
        pyg.draw.circle(self.image, self.colors[colorIndex], finalPos, Stroke.width*gui.scale/2)
        pyg.draw.line(self.image, self.colors[colorIndex], self.initPos, finalPos, int(Stroke.width*gui.scale))
        self.initPos = finalPos

    def explode(self, deactivate: bool = True):
        "Returns a list of Stroke objects derrived from an original Stroke"
        temp = []
        for i in range(len(self.points)):
            s = Stroke(self.parent)
            s.points.append(self.points[i])
            s.colors.append(self.colors[i])
            s.scale()
            temp.append(s)
            if deactivate:
                Stroke.strokeGroup.remove(s)
        return temp

    def scale(self):
        """
        Redraws the frame with the correct scaling\n
        Also used for updating a Stroke if the points list is ever updated
        """
        alpha = self.image.get_alpha()
        
        # reset the frame
        self.image = pyg.transform.scale(Stroke.frame, self.rect.size)
        gui.GUI.trueTransform(self, "set_alpha", alpha)

        if not self.points or not self.points[0]:
            return
        
        temp = self.points.copy()
        self.points = []

        for s in temp:
            if not s:
                break
            self.initPos = tuple(i*gui.scale for i in s[0])
            self.points.append([])
            colorIndex = temp.index(s)
            for p in s:
                self.draw((p[0]*gui.scale, p[1]*gui.scale), colorIndex)

# -------------------- GUI Events --------------------
# drawGUI events
def drawInit(self:gui.GUI):
    finalPos = (mouse_pos[0] - self.rect.left, mouse_pos[1] - self.rect.top)

    drawStroke.points.append([])
    drawStroke.colors.append("white")
    drawStroke.initPos = finalPos
    drawStroke.draw(finalPos)
    gui.GUI.enable(undoGUI)

def drawDrag(self:gui.GUI):
    finalPos = (mouse_pos[0] - self.rect.left, mouse_pos[1] - self.rect.top)

    drawStroke.draw(finalPos)

def drawCheck(self:gui.GUI):
    # allows for the user to drag mouse outside of drawGUI
    if not self.hovering and self.dragging:
        drawStroke.initPos = (mouse_pos[0] - self.rect.left, mouse_pos[1] - self.rect.top)

#undoGUI events
def undoStroke(self:gui.GUI):
    if drawStroke.points:
        drawStroke.points.pop()
        drawStroke.scale()
        if not drawStroke.points:
            gui.GUI.disable(self)

# hintGUI events
def hintAnimate(self:gui.GUI):
    Animate.currentFrame = 0
    pyg.time.set_timer(animateEvent, 10, 0)
    gui.GUI.disable(self)

# submitGUI events
redYellowGreenBezier = svg.Bezier(' d="M255,0C255,255,255,255,0,255"')
def submit(self:gui.GUI):
    Animate.tryEnd()
    Deck.active = False
    gui.GUI.deactivate(undoGUI)
    gui.GUI.disable(drawGUI, hintGUI, submitGUI)

    strokeMasks = [pyg.mask.from_surface(i.image) for i in drawStroke.explode()]
    testingKanjiMasks = svg.Kanji.svgTextToSurf(*[svg.alterValue(i, width = drawGUI.dimensions[0]*gui.scale, height = drawGUI.dimensions[1]*gui.scale, **{"stroke-width" : 16*gui.scale}) for i in Deck.kanji.svgList])
    kanjiMasks = [pyg.mask.from_surface(i) for i in testingKanjiMasks]
    mergedSurface = pyg.surface.Surface((drawGUI.dimensions[0]*gui.scale, drawGUI.dimensions[1]*gui.scale), pyg.SRCALPHA)
    strokeNumber = pyg.font.SysFont("uddigikyokashonr", int(Stroke.width*gui.scale), bold=True)

    scores = []
    for i in range(len(strokeMasks)):
        try:
            kjm = testingKanjiMasks[i]
            grade = min(kanjiMasks[i].overlap_area(strokeMasks[i], (0, 0))/max(Deck.kanji.maskList[i].count(), strokeMasks[i].count()), 1.0)
            scores.append(grade)
            redGreen = redYellowGreenBezier.functions[0](grade)
            pyg.pixelarray.PixelArray(kjm).replace((0, 0, 0), (redGreen[0], redGreen[1], 0) if grade > 0 else (0, 0, 255))
            kjm.set_alpha(127)
            if not Deck.kanji.pBzPoints == "N/A":
                mergedSurface.blits(blit_sequence=((kjm, (0, 0)), (strokeNumber.render(str(i+1), False, "white"), [j*gui.scale for j in Deck.kanji.pBzPoints[i][int(len(Deck.kanji.pBzPoints[i])/8)]]))) # goodbye readability
            else:
                mergedSurface.blit(kjm, (0, 0))

        except IndexError:
            scores.append(0)
    
    # TODO: once the next version is dropped fix the redundant code
    if len(strokeMasks) < len(kanjiMasks):
        for i in range(len(strokeMasks), len(kanjiMasks)):
            kjm = testingKanjiMasks[i]
            scores.append(0)
            pyg.pixelarray.PixelArray(kjm).replace((0, 0, 0), (0, 0, 255))
            kjm.set_alpha(127)
            if not Deck.kanji.pBzPoints == "N/A":
                mergedSurface.blits(blit_sequence=((kjm, (0, 0)), (strokeNumber.render(str(i+1), False, "white"), [j*gui.scale for j in Deck.kanji.pBzPoints[i][int(len(Deck.kanji.pBzPoints[i])/8)]]))) # goodbye readability
            else:
                mergedSurface.blit(kjm, (0, 0))
    
    gui.GUI.trueTransform(drawStroke, "set_alpha", 127)

    score = round(sum(scores)/len(kanjiMasks), 2)
    redGreen = redYellowGreenBezier.functions[0](score)
    accuracyGUI.write(f"{int(score*100)}%", (redGreen[0], redGreen[1], 0))

    gui.GUI.activate(retryGUI)

    global gradeGUI
    gradeGUI.delete()
    gradeGUI = gui.GUI.activate(gui.GUI(drawGUI.pos, drawGUI.dimensions, image = mergedSurface))[0]

    if Deck.kanji.str in config["kanjiScore"]:
        gui.GUI.activate(oldAccuracyGUI)
        oldAccuracyGUI.write(f"{int(config['kanjiScore'][Deck.kanji.str]*100)}%")
        gui.GUI.trueTransform(oldAccuracyGUI.fontInfo["gui"], "set_alpha", 127)
    config["kanjiScore"][Deck.kanji.str] = score
    mw.addonManager.writeConfig(__name__, config)

    Deck.shouldContinue()

# continueGUI events
def continueClicked(self: gui.GUI):
    Deck.newRound()


# -------------------- GUI Initializing --------------------
drawGUI = gui.GUI((150, 150), (175, 175), image = "grid.png", pressed = drawInit, heave = drawDrag, active = drawCheck)
undoGUI = gui.GUI((85, 275), (30, 30), image = gui.Spritesheet((500, 500), "undogui.png"), freed = undoStroke)
hintGUI = gui.GUI((150, 275), (30, 30), image = gui.Spritesheet((500, 500), "hintgui.png"), freed = hintAnimate)
submitGUI = gui.GUI((215, 275), (30, 30), image = gui.Spritesheet((500, 500), "submitgui.png"), freed = submit)
continueGUI = gui.GUI((150, 275), (30, 30), image = gui.Spritesheet((500, 500), "continuegui.png"), freed = continueClicked)
retryGUI = gui.GUI((85, 275), (30, 30), image = gui.Spritesheet((500, 500), "retrygui.png"), freed = Deck.retryRound)

promptGUI = gui.GUI((150, 30), (30, 30), image = "grid.png")
accuracyGUI = gui.GUI((215, 30), (60, 30), image = "accuracygui.png")
oldAccuracyGUI = gui.GUI((85, 30), (60, 30), image = "accuracygui.png")
gradeGUI = gui.GUI(drawGUI.pos, drawGUI.dimensions)
gui.GUI.trueTransform(oldAccuracyGUI, "set_alpha", 127)
gui.GUI.activate(drawGUI, undoGUI, hintGUI, submitGUI, promptGUI, accuracyGUI)
gui.GUI.disable(undoGUI)

# -------------------- Stroke Initializing --------------------
drawStroke = Stroke(drawGUI)
Animate.frame = Stroke(drawGUI)
gui.GUI.trueTransform(Animate.frame, "set_alpha", 127)

# -------------------- Anki Hooks --------------------
pyg.display.quit()

def enableKWP(card):
    global deckID
    deckID = mw.col.decks.current()["id"]
    if Deck.paused:
        return

    if not deckID in config["whitelist"] + config["blacklist"]:
        ask_user("Would you like to enable Kanji Writing Practice for this deck?", callback = Deck.shouldEnable, defaults_yes = False)
    elif deckID in config["whitelist"]:
        prepKWP(card)

def prepKWP(card):
    # pygame can't have two displays inited at the same time
    if Deck.running:
        return
    Deck.running = True

    # initing display and setting mode for convert method to function
    pyg.display.init()

    gui.initDisplay((300, 300), "Initializing", (-300, -300))
    Deck.newCard(card.note().fields[0])
    
    Deck.newRound()
    pyg.display.quit()
    kanjiWritingPractice()

def kanjiWritingPractice_bg():
    global mouse_pos

    if not hasattr(mw.reviewer, "state") or mw.state != "review":
        Deck.running = False
        return

    pyg.display.init()
    gui.initDisplay((300, 300), "Kanji Writing Practice", Deck.pos)
    gui.scaleDisplay(Deck, *gui.GUI.allGUI, *Stroke.strokeGroup.sprites(), Deck.kanji)

    # NOTE: pygame's sdl2 module seems weird, also taken from stackoverflow: https://stackoverflow.com/questions/4135928/pygame-display-position
    window = Window.from_display_module()

    while Deck.running:
        mouse_pos = pyg.mouse.get_pos()

        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                Deck.running = False
            elif event.type == pyg.WINDOWRESIZED:
                gui.scaleDisplay(event, *gui.GUI.allGUI, *Stroke.strokeGroup.sprites(), Deck.kanji)
                Deck.x, Deck.y = pyg.display.get_window_size()
            elif event.type == animateEvent:
                Animate.begin()
            elif event.type == endAnimateEvent:
                Animate.end()
            gui.GUI.interaction(event)
        gui.screen.fill("black")

        gui.GUI.activeGUI.draw(gui.screen)
        gui.GUI.activeGUI.update(mouse_pos)
        Stroke.strokeGroup.draw(gui.screen)
        pyg.display.update([i.rect for i in gui.GUI.allGUI])
        clock.tick(60)
    Deck.pos = window.position
    pyg.display.quit()

# code taken from the Anki development forums: https://forums.ankiweb.net/t/pygame-addon-has-trouble-switching-from-overview-to-review/62502/5
# thank you!
def kanjiWritingPractice():
    t = Thread(target=kanjiWritingPractice_bg, args=(), daemon=True)
    t.start()

def terminateKWP(*args):
    Deck.running = False
    Deck.paused = False

gui_hooks.reviewer_did_show_question.append(enableKWP)
gui_hooks.reviewer_did_show_answer.append(terminateKWP)
gui_hooks.reviewer_will_end.append(terminateKWP)
gui_hooks.profile_will_close.append(terminateKWP)