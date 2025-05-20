# practice writing kanji
import pygame as pyg
import gui

pyg.init()
clock = pyg.time.Clock()

# pygame screen
gui.init_display((300, 300), "Kanji Writing Practice")

# GUI events
def drawInit(self):
    pyg.draw.circle(gui.screen, "white", mouse_pos, 5)

def drawDrag(self):
    pass

# GUI initializing
drawGUI = gui.GUI(150, 150, 175, 175, image = "assets/grid.png", pressed = drawInit)
drawGUI.strokes = []
undoGUI = gui.GUI(85, 275, 40, 30)
redoGUI = gui.GUI(215, 275, 40, 30)
submitGUI = gui.GUI(150, 275, 30, 30)
gui.GUI.activate(drawGUI, undoGUI, redoGUI, submitGUI)

running = True

while running:
    mouse_pos = pyg.mouse.get_pos()

    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            running = False
        if event.type == pyg.WINDOWRESIZED:
            gui.scaleDisplay(event)
        gui.GUI.interaction(event, mouse_pos)

    gui.GUI.activeGUI.draw(gui.screen)

    pyg.display.flip()
    clock.tick(60)