# practice writing kanji
import pygame as pyg
import gui

pyg.init()
clock = pyg.time.Clock()

# pygame screen
gui.init_display((300, 300), "Kanji Writing Practice")

class Stroke(pyg.sprite.Sprite):
    """
    Subclass of pygame's sprite class that handles every stroke drawn by the user\n
    An instance is created on the designated sprite\n
    """
    strokeGroup = pyg.sprite.Group()

    def __init__(self, sprite):
        super().__init__()
        self.image = pyg.transform.scale(pyg.image.load("assets/frame.png").convert_alpha(), sprite.rect.size)
        self.rect = self.image.get_rect(center = sprite.rect.center)
        Stroke.strokeGroup.add(self)

# -------------------- GUI Events --------------------
# drawGUI events
def drawInit(self:gui):
    self.strokes.append(Stroke(drawGUI))

def drawDrag(self:gui):
    translationX = (gui.screen.get_width()-self.rect.w)/2
    translationY = (gui.screen.get_height()-self.rect.h)/2

    pyg.draw.circle(self.strokes[-1].image, "white", (mouse_pos[0] - translationX, mouse_pos[1] - translationY), gui.screen.get_width()*5/gui.ogSize[0])

#undoGUI events
def undoStroke(self:gui):
    if drawGUI.strokes:
        Stroke.strokeGroup.remove(drawGUI.strokes.pop())

# -------------------- GUI Initializing --------------------
drawGUI = gui.GUI((150, 150), (175, 175), image = "assets/grid.png", pressed = drawInit, heave = drawDrag)
drawGUI.strokes = []
undoGUI = gui.GUI((85, 275), (40, 30), freed = undoStroke)
redoGUI = gui.GUI((215, 275), (40, 30))
submitGUI = gui.GUI((150, 275), (30, 30))
gui.GUI.activate(drawGUI, undoGUI, redoGUI, submitGUI)

# -------------------- Main Loop --------------------
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
    Stroke.strokeGroup.draw(gui.screen)

    pyg.display.flip()
    clock.tick(120)