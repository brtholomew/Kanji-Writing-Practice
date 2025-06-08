# practice writing kanji
import sys
from os import path
# bundling pygame
sys.path.insert(0, path.dirname(__file__))

import pygame as pyg
import gui
import svg
#from aqt import gui_hooks

#gui_hooks.reviewer_did_answer_card.append()

pyg.init()
clock = pyg.time.Clock()

# pygame screen
gui.initDisplay((300, 300), "Kanji Writing Practice")

class Deck():
    """
    Processes the kanji anki deck selected for studying
    """
    def __init__(self):
        pass

class Stroke(pyg.sprite.Sprite):
    """
    Subclass of pygame's sprite class that handles every stroke drawn by the user\n
    An instance is created on the designated sprite\n
    """
    
    frame = pyg.image.load("assets/frame.png").convert_alpha()
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
    gui.GUI.disable(drawGUI, undoGUI, hintGUI)

    strokeMasks = [pyg.mask.from_surface(i.image) for i in drawGUI.strokes]
    #strokeMasks = [pyg.mask.from_surface(i.image) for i in animateFrames]
    testingKanjiMasks = [gui.GUI((150, 150), (175, 175), image = svg.Kanji.svgTextToSurf(svg.alterValue(i, **{"stroke-width" : 16}))) for i in kanji.svgList]
    kanjiMasks = [pyg.mask.from_surface(i.image) for i in testingKanjiMasks]
    scores = []
    for i in range(len(strokeMasks)):
        try:
            grade = min(kanjiMasks[i].overlap_area(strokeMasks[i], (0, 0))/max(kanji.maskList[i].count(), strokeMasks[i].count()), 1.0)
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
    print(score)

def newKanjiInit():
    pass

# -------------------- GUI Initializing --------------------
drawGUI = gui.GUI((150, 150), (175, 175), image = "assets/grid.png", pressed = drawInit, freed = drawPointsCheck, heave = drawDrag, active = drawCheck)
drawGUI.strokes = []
undoGUI = gui.GUI((85, 275), (40, 30), freed = undoStroke)
hintGUI = gui.GUI((150, 275), (30, 30), freed = hintAnimate)
submitGUI = gui.GUI((215, 275), (40, 30), freed = submit)
promptGUI = gui.GUI((150, 30), (30, 30), image = "assets/grid.png")
accuracyGUI = gui.GUI((215, 30), (60, 30))
gui.GUI.activate(drawGUI, undoGUI, hintGUI, submitGUI, promptGUI, accuracyGUI)

# -------------------- Kanji Variables --------------------
kanjiList = [
    ["良"],
    ["状", "態"],
    ["食"]
]
kanjiDict = {}
for i in kanjiList:
    for k in i:
        kanjiDict[k] = svg.Kanji(k, (175, 175), 8)

prompt = "良"
kanji = svg.Kanji("良", (175, 175), 8)
# TODO: uncomment this
#kanji = kanjiDict[prompt]
promptGUI.write(prompt)
accuracyGUI.write("--%")

# -------------------- Pygame Events --------------------
animateEvent = pyg.event.custom_type()
def animate():
    global animateCounter
    # draw every stroke from the prompt pBzPoints list
    index = int(animateCounter/len(kanji.pBzPoints[0]))
    point = animateCounter%len(kanji.pBzPoints[0])
    animateFrames[index].points.append(kanji.pBzPoints[index][point])
    animateFrames[index].scale()

    animateCounter += 1
    if int(animateCounter/len(kanji.pBzPoints[0])) == len(kanji.pBzPoints):
        pyg.time.set_timer(endAnimateEvent, 2500, 1)
    else:
        pyg.time.set_timer(animateEvent, 1, 1)

endAnimateEvent = pyg.event.custom_type()
def endAnimate():
    global animateCounter
    for i in animateFrames:
        i.points = []
        i.scale()
    animateCounter = 0
    gui.GUI.enable(hintGUI)

# -------------------- Animation Variables --------------------
# TODO: make sure to change the amount of animation frames when new prompt is selected
animateFrames = []
for i in range(len(kanji.pBzPoints)):
    animateFrames.append(Stroke(drawGUI))
    animateFrames[-1].color = "gray"
animateCounter = 0

# -------------------- Main Loop --------------------
# where does this go???
redYellowGreenBezier = svg.Bezier(' d="M255,0C255,255,255,255,0,255"')

running = True

while running:
    mouse_pos = pyg.mouse.get_pos()

    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            running = False
        elif event.type == pyg.WINDOWRESIZED:
            # TODO: find a replacement for kanjiDict.values() that actually works
            gui.scaleDisplay(event, *gui.GUI.allGUI, *Stroke.strokeGroup.sprites(), kanji)
        elif event.type == animateEvent:
            animate()
        elif event.type == endAnimateEvent:
            endAnimate()
        gui.GUI.interaction(event)
    gui.screen.fill("black")

    gui.GUI.activeGUI.draw(gui.screen)
    gui.GUI.activeGUI.update(mouse_pos)
    Stroke.strokeGroup.draw(gui.screen)

    pyg.display.flip()
    clock.tick(60)