# practice writing kanji
import pygame as pyg
import gui

pyg.init()
clock = pyg.time.Clock()

# pygame screen
gui.init_display((300, 300), "Kanji Writing Practice")

# start initializing stuff

test = gui.GUI(150, 150, 100, 100)
gui.GUI.activate(test)

running = True

while running:
    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            running = False
        if event.type == pyg.WINDOWRESIZED:
            # prevent the screen from getting smaller than the designated amount
            gui.screen = pyg.display.set_mode((max(gui.ogSize[0], event.x), max(gui.ogSize[1], event.y)), flags = pyg.RESIZABLE)
            for i in gui.GUI.allGUI:
                i.update()

    gui.GUI.activeGUI.draw(gui.screen)

    pyg.display.flip()
    clock.tick(60)