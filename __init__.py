# practice writing kanji
import sys
from os import path
from threading import Thread
from typing import Union
# bundling pygame
sys.path.insert(0, path.dirname(__file__))

import pygame as pyg
import gui
import svg
from aqt import gui_hooks, mw

pyg.init()
clock = pyg.time.Clock()

# pygame screen
gui.initDisplay((300, 300), "Kanji Writing Practice")

# where does this go???
redYellowGreenBezier = svg.Bezier(' d="M255,0C255,255,255,255,0,255"')

class Deck():
    """
    Processes the anki card
    """
    prompt = []
    kanjiDict = {"N/A" : "N/A"}
    counter = 0
    kanji: Union[svg.Kanji, str] = "N/A"

    @classmethod
    def newCard(cls, question: str):
        cls.reset()
        for c in question:
            # code taken from Kanji Colorizer: https://github.com/cayennes/kanji-colorize/blob/main/anki/kanji_colorizer.py
            print(ord(c) >= 19968 and ord(c) <= 40879)
            if ord(c) >= 19968 and ord(c) <= 40879:
                cls.prompt.append(c)
                try:
                    cls.kanjiDict[c] = svg.Kanji(c, (175, 175), 8)
                except FileNotFoundError:
                    pass
        if not cls.prompt:
            cls.prompt.append("N/A")
            cls.kanji = "N/A"
            return
        cls.kanji = cls.kanjiDict[cls.prompt[cls.counter]]

    @classmethod
    def next(cls):
        cls.counter += 1
        cls.kanji = cls.kanjiDict[cls.prompt[cls.counter]]
    
    @classmethod
    def reset(cls):
        cls.prompt = []
        cls.counter = 0

animateEvent = pyg.event.custom_type()
endAnimateEvent = pyg.event.custom_type()
class Animate():
    """
    Handles animating the kanji drawing
    """
    frames = []
    counter = 0

    @classmethod
    def newAnimation(cls, kanji: svg.Kanji):
        for i in range(len(kanji.pBzPoints)):
            cls.frames.append(Stroke(drawGUI))
            cls.frames[-1].color = "gray"

    @classmethod
    def begin(cls):
        # draw every stroke from the prompt pBzPoints list
        index = int(cls.counter/len(Deck.kanji.pBzPoints[0]))
        point = cls.counter%len(Deck.kanji.pBzPoints[0])
        cls.frames[index].points.append(Deck.kanji.pBzPoints[index][point])
        cls.frames[index].scale()

        cls.counter += 1
        if int(cls.counter/len(Deck.kanji.pBzPoints[0])) == len(Deck.kanji.pBzPoints):
            pyg.time.set_timer(endAnimateEvent, 2500, 1)
        else:
            pyg.time.set_timer(animateEvent, 1, 1)

    @classmethod
    def end(cls):
        for i in cls.frames:
            i.points = []
            # TODO: is this necessary?
            i.scale()
        cls.counter = 0
        gui.GUI.enable(hintGUI)

class Stroke(pyg.sprite.Sprite):
    """
    Subclass of pygame's sprite class that handles every stroke drawn by the user\n
    An instance is created on the designated sprite\n
    """
    
    frame = pyg.image.load(gui.assetPath("frame.png")).convert_alpha()
    strokeGroup = pyg.sprite.Group()

    width = 8

    def __init__(self, sprite):
        super().__init__()
        self.image = pyg.transform.scale(Stroke.frame, sprite.rect.size)
        self.rect = self.image.get_rect(center = sprite.rect.center)

        self.parent = sprite
        self.pos: tuple[int, int] = sprite.pos
        self.dimensions = sprite.dimensions
        self.color = "white"
        self.points = []

        Stroke.strokeGroup.add(self)

    def draw(self, finalPos: tuple[int, int]):
        """
        Draws a line on the frame\n
        """
        self.points.append([finalPos[0]/gui.scale, finalPos[1]/gui.scale])
        pyg.draw.circle(self.image, self.color, finalPos, Stroke.width/2)
        pyg.draw.line(self.image, self.color, self.initPos, finalPos, int(Stroke.width))
        self.initPos = finalPos

    def scale(self):
        """
        Redraws the frame with the correct scaling
        """
        
        Stroke.width = 8*gui.scale
        # reset the frame
        self.image = pyg.transform.scale(Stroke.frame, self.rect.size)

        if not self.points:
            return
        
        # redraw every point onto it
        temp = self.points.copy()
        self.points = []
        self.initPos = (temp[0][0]*gui.scale, temp[0][1]*gui.scale)

        for i in temp:
            self.draw((i[0]*gui.scale, i[1]*gui.scale))

# -------------------- GUI Events --------------------
# drawGUI events
def drawInit(self:gui):
    # create a new frame
    global translationX, translationY
    self.strokes.append(Stroke(drawGUI))

    # localize coordinates
    translationX, translationY = self.rect.topleft
    finalPos = (mouse_pos[0] - translationX, mouse_pos[1] - translationY)

    self.strokes[-1].initPos = finalPos
    self.strokes[-1].draw(finalPos)

def drawDrag(self:gui):
    # draw circles on that frame
    finalPos = (mouse_pos[0] - translationX, mouse_pos[1] - translationY)

    self.strokes[-1].draw(finalPos)

def drawPointsCheck(self:gui):
    pass
    #print(len(Stroke.strokeGroup))
    #print(self.strokes[-1].points)

def drawCheck(self:gui):
    # my terrible solution to a mild problem
    if not self.hovering and self.dragging:
        self.strokes[-1].initPos = (mouse_pos[0] - translationX, mouse_pos[1] - translationY)

#undoGUI events
def undoStroke(self:gui):
    if drawGUI.strokes:
        stroke = drawGUI.strokes.pop()
        Stroke.strokeGroup.remove(stroke)
        stroke.points.pop()

# hintGUI events
def hintAnimate(self:gui):
    pyg.time.set_timer(animateEvent, 10, 0)
    gui.GUI.disable(self)

# submitGUI events
def submit(self:gui):
    gui.GUI.disable(drawGUI, undoGUI, hintGUI, submitGUI)

    strokeMasks = [pyg.mask.from_surface(i.image) for i in drawGUI.strokes]
    #strokeMasks = [pyg.mask.from_surface(i.image) for i in animateFrames]
    testingKanjiMasks = [gui.GUI((150, 150), (175, 175), image = svg.Kanji.svgTextToSurf(svg.alterValue(i, **{"stroke-width" : 16}))) for i in Deck.kanji.svgList]
    kanjiMasks = [pyg.mask.from_surface(i.image) for i in testingKanjiMasks]
    scores = []
    for i in range(len(strokeMasks)):
        try:
            grade = min(kanjiMasks[i].overlap_area(strokeMasks[i], (0, 0))/max(Deck.kanji.maskList[i].count(), strokeMasks[i].count()), 1.0)
            scores.append(grade)
            redGreen = redYellowGreenBezier.functions[0](grade)
            pyg.pixelarray.PixelArray(testingKanjiMasks[i].ogimage).replace((0, 0, 0), (redGreen[0], redGreen[1], 0) if grade > 0 else (0, 0, 255))
            pyg.pixelarray.PixelArray(testingKanjiMasks[i].image).replace((0, 0, 0), (redGreen[0], redGreen[1], 0) if grade > 0 else (0, 0, 255))
            testingKanjiMasks[i].ogimage.set_alpha(127)
            testingKanjiMasks[i].image.set_alpha(127)
        except IndexError:
            scores.append(0)
    
    if len(strokeMasks) < len(kanjiMasks):
        for i in range(len(kanjiMasks)-len(strokeMasks)):
            scores.append(0)
            pyg.pixelarray.PixelArray(testingKanjiMasks[i].ogimage).replace((0, 0, 0), (0, 0, 255))
            pyg.pixelarray.PixelArray(testingKanjiMasks[i].image).replace((0, 0, 0), (0, 0, 255))
            testingKanjiMasks[i].ogimage.set_alpha(127)
            testingKanjiMasks[i].image.set_alpha(127)
    
    gui.GUI.activate(*testingKanjiMasks)

    score = round(sum(scores)/len(kanjiMasks), 2)
    redGreen = redYellowGreenBezier.functions[0](score)
    accuracyGUI.write(f"{int(score*100)}%", (redGreen[0], redGreen[1], 0))

def newKanjiInit():
    pass

# -------------------- GUI Initializing --------------------
drawGUI = gui.GUI((150, 150), (175, 175), image = gui.assetPath("grid.png"), pressed = drawInit, freed = drawPointsCheck, heave = drawDrag, active = drawCheck)
drawGUI.strokes = []
undoGUI = gui.GUI((85, 275), (40, 30), image = gui.Spritesheet((500, 500), "undogui.png"), freed = undoStroke)
hintGUI = gui.GUI((150, 275), (30, 30), image = gui.Spritesheet((500, 500), "hintgui.png"), freed = hintAnimate)
submitGUI = gui.GUI((215, 275), (40, 30), image = gui.Spritesheet((500, 500), "submitgui.png") , freed = submit)
promptGUI = gui.GUI((150, 30), (30, 30), image = gui.assetPath("grid.png"))
accuracyGUI = gui.GUI((215, 30), (60, 30))
gui.GUI.activate(drawGUI, undoGUI, hintGUI, submitGUI, promptGUI, accuracyGUI)

# -------------------- Main Loop --------------------
pyg.display.quit()
running = False

def cardNote(card):
    pass
    pyg.display.init()
    gui.initDisplay((300, 300), "Kanji Writing Practice")

    Deck.newCard(card.note().fields[0])
    print(f"kanji: {Deck.kanji}, str: {Deck.kanji.str}")
    if Deck.kanji == "N/A":
        gui.GUI.disable(drawGUI, undoGUI, hintGUI, submitGUI)
        promptGUI.write("N/A")
        accuracyGUI.write("--%")

        pyg.display.quit()
        return
    Animate.newAnimation(Deck.kanji)
    promptGUI.write(Deck.kanji.str)
    accuracyGUI.write("--%")

    pyg.display.quit()
    

def kanjiWritingPractice_bg(a):
    global mouse_pos, running

    if not hasattr(mw.reviewer, "state") or mw.state != "review" or running:
        print("returning")
        return
    print("proceeding")

    pyg.display.init()
    gui.initDisplay((300, 300), "Kanji Writing Practice")
    running = True

    while running:
        mouse_pos = pyg.mouse.get_pos()

        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                running = False
            elif event.type == pyg.WINDOWRESIZED:
                # TODO: sometimes Deck.kanji will be a string "N/A", which DOES NOT HAVE A SCALE METHOD
                gui.scaleDisplay(event, *gui.GUI.allGUI, *Stroke.strokeGroup.sprites(), Deck.kanji)
            elif event.type == animateEvent:
                Animate.begin()
            elif event.type == endAnimateEvent:
                Animate.end()
            gui.GUI.interaction(event)
        gui.screen.fill("black")

        gui.GUI.activeGUI.draw(gui.screen)
        gui.GUI.activeGUI.update(mouse_pos)
        Stroke.strokeGroup.draw(gui.screen)

        pyg.display.flip()
        clock.tick(60)
    pyg.display.quit()

# code taken from the Anki development forums: https://forums.ankiweb.net/t/pygame-addon-has-trouble-switching-from-overview-to-review/62502/5
# thank you!
def kanjiWritingPractice(a):
    t = Thread(target=kanjiWritingPractice_bg, args=(a,), daemon=True)
    t.start()

def terminateKWP(*args):
    global running
    running = False

def testFunc(a,b):
    print(f"current state: {mw.state}")

gui_hooks.reviewer_did_show_question.append(cardNote)
gui_hooks.state_did_change.append(testFunc)
gui_hooks.reviewer_did_show_question.append(kanjiWritingPractice)
gui_hooks.reviewer_did_show_answer.append(terminateKWP)
gui_hooks.reviewer_will_end.append(terminateKWP)
gui_hooks.profile_will_close.append(terminateKWP)