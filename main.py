# practice writing kanji
import pygame as pyg
import gui

pyg.init()
clock = pyg.time.Clock()

# pygame screen
gui.initDisplay((300, 300), "Kanji Writing Practice")

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
        self.pos: gui.point = sprite.pos
        self.dimensions = sprite.dimensions
        self.points = []

        Stroke.strokeGroup.add(self)

    def draw(self, finalPos: gui.point):
        """
        Draws a line on the frame\n
        """
        self.points.append([finalPos[0]/gui.scale, finalPos[1]/gui.scale])
        pyg.draw.circle(self.image, "white", finalPos, Stroke.width/2)
        pyg.draw.line(self.image, "white", self.initPos, finalPos, int(Stroke.width))
        self.initPos = finalPos

    def scale(self):
        """
        Redraws the frame with the correct scaling
        """
        Stroke.width = 8*gui.scale
        # reset the frame
        self.image = pyg.transform.scale(Stroke.frame, self.rect.size)

        # redraw every point onto it
        temp = self.points
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

    #Stroke.initPos = finalPos
    self.strokes[-1].initPos = finalPos
    self.strokes[-1].draw(finalPos)

def drawDrag(self:gui):
    # draw circles on that frame
    finalPos = (mouse_pos[0] - translationX, mouse_pos[1] - translationY)

    self.strokes[-1].draw(finalPos)

def drawPointsCheck(self:gui):
    print(len(Stroke.strokeGroup))
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

# -------------------- GUI Initializing --------------------
drawGUI = gui.GUI((150, 150), (175, 175), image = "assets/grid.png", pressed = drawInit, freed = drawPointsCheck, heave = drawDrag, active = drawCheck)
drawGUI.strokes = []
undoGUI = gui.GUI((85, 275), (40, 30), freed = undoStroke)
submitGUI = gui.GUI((215, 275), (40, 30))
hintGUI = gui.GUI((150, 275), (30, 30))
gui.GUI.activate(drawGUI, undoGUI, submitGUI, hintGUI)

# -------------------- Main Loop --------------------
prompt = "食"

running = True

while running:
    mouse_pos = pyg.mouse.get_pos()
    #print(f"mouse x:{mouse_pos[0]}, translateX: {drawGUI.rect.topleft[0]}")
    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            running = False
        if event.type == pyg.WINDOWRESIZED:
            gui.scaleDisplay(event, *gui.GUI.allGUI, *Stroke.strokeGroup.sprites())
        gui.GUI.interaction(event, mouse_pos)

    gui.screen.fill("black")

    gui.GUI.activeGUI.draw(gui.screen)
    gui.GUI.activeGUI.update(mouse_pos)
    Stroke.strokeGroup.draw(gui.screen)

    pyg.display.flip()
    clock.tick(60)