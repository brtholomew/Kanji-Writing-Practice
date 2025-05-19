# module for handling gui elements (such as buttons)
import pygame as pyg
from typing import Callable

pyg.init()

def init_display(size = (100, 100), caption:str = "Pygame"):
    """
    Initializes a display at the desired lowest possible size\n
    Necessary for allowing the GUI to scale properly
    """
    global ogSize, screen
    ogSize = size
    screen = pyg.display.set_mode(size = ogSize, flags = pyg.RESIZABLE)
    pyg.display.set_caption(caption)

class GUI(pyg.sprite.Sprite):
    """
    Subclass of pygame's sprite class for GUI elements\n
    pressed - function that runs when the GUI is clicked on\n
    released - function that runs when the GUI is no longer clicked on
    """
    activeGUI = pyg.sprite.Group()
    allGUI = []

    def __init__(self, xpos:int, ypos:int, width:int, height:int, image:str = "assets\placeholder.png", pressed: Callable[[], None] = lambda: None, released: Callable[[], None] = lambda: None):
        super().__init__()
        self.pos = (xpos, ypos)
        self.dimensions = (width, height)
        self.image = pyg.transform.scale(pyg.image.load(image).convert_alpha(), (width, height))
        self.rect = self.image.get_rect(center = self.pos)
        self.pressed = pressed
        self.released = released
        GUI.allGUI.append(self)

    @classmethod
    def activate(cls, *args):
        cls.activeGUI.add(args)

    @classmethod
    def deactivate(cls, *args):
        cls.activeGUI.remove(args)

    def update(self):
        """
        Properly scales every GUI object based on the new size of the window
        """
        displaySize = pyg.display.get_window_size()
        scaleX = displaySize[0]/ogSize[0]
        scaleY = displaySize[1]/ogSize[1]
        # take the max of the x/y scales so the image itself retains its original aspect ratio
        scale = max(scaleX, scaleY)

        self.image = pyg.transform.scale(self.image, (self.dimensions[0]*scale, self.dimensions[1]*scale))
        self.rect = self.image.get_rect(center = (self.pos[0]*scaleX, self.pos[1]*scaleY))


