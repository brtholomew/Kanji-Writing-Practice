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

    width = 4
    
    initPos = (0, 0)

    def __init__(self, sprite):
        super().__init__()
        self.image = pyg.transform.scale(Stroke.frame, sprite.rect.size)
        self.rect = self.image.get_rect(center = sprite.rect.center)
        self.points = []

        Stroke.strokeGroup.add(self)

    def draw(self, finalPos: gui.point, width):
        """
        Draws a line on the frame\n
        If you're using the mouse with this function, make sure to localize the coordinates to the frame
        """
        pyg.draw.circle(self.image, "white", finalPos, width/2)
        pyg.draw.line(self.image, "white", Stroke.initPos, finalPos, int(width))
        Stroke.initPos = finalPos


    def scale(self, scaleX, scaleY):
        pass


# -------------------- GUI Events --------------------
# drawGUI events
def drawInit(self:gui):
    # create a new frame
    global translationX, translationY, width
    self.strokes.append(Stroke(drawGUI))

    # localize the coordinates to the frame
    translationX = (gui.screen.get_width()-self.rect.w)/2
    translationY = (gui.screen.get_height()-self.rect.h)/2
    width = 4*gui.scale

    finalPos = (mouse_pos[0] - translationX, mouse_pos[1] - translationY)
    Stroke.initPos = finalPos
    self.strokes[-1].points.append(list(finalPos))
    self.strokes[-1].draw(finalPos, width)


def drawDrag(self:gui):
    # draw circles on that frame
    finalPos = (mouse_pos[0] - translationX, mouse_pos[1] - translationY)

    self.strokes[-1].points.append(list(finalPos))
    self.strokes[-1].draw(finalPos, width)

def drawPointsCheck(self:gui):
    print(self.strokes[-1].points)

def drawCheck(self:gui):
    # my terrible solution to a mild problem
    if not self.hovering and self.dragging:
        Stroke.initPos = (mouse_pos[0] - translationX, mouse_pos[1] - translationY)

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