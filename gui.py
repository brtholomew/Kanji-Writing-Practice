# module for handling gui elements (such as buttons)
import pygame as pyg
from typing import Callable, TypeAlias

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

def scaleDisplay(event):
    """
    Correctly scales everything when the pygame display is resized
    """
    # prevent the screen from getting smaller than the designated amount
    screen = pyg.display.set_mode((max(ogSize[0], event.x), max(ogSize[1], event.y)), flags = pyg.RESIZABLE)
    for i in GUI.allGUI:
        i.update()

pressed: TypeAlias = Callable[["GUI"], None]
freed: TypeAlias = Callable[["GUI"], None]
heave: TypeAlias = Callable[["GUI"], None]

class GUI(pyg.sprite.Sprite):
    """
    Subclass of pygame's sprite class for GUI elements\n

    pressed - function that runs when the GUI is clicked on\n
    released - function that runs when the GUI is no longer clicked on\n
    heave - function that runs when the GUI is being dragged\n

    pressed, released, and heave MUST HAVE A self PARAMETER LIKE A REGULAR CLASS METHOD\n
    """
    activeGUI = pyg.sprite.Group()
    allGUI = []

    def __init__(self, xpos:int, ypos:int, width:int, height:int, image:str = "assets\placeholder.png", pressed = lambda x: print(f"{x} was clicked!"), freed = lambda x: print(f"{x} was released!"), heave = lambda x: print(f"{x} is being dragged!")):
        super().__init__()
        self.pos = (xpos, ypos)
        self.dimensions = (width, height)
        self.ogimage = pyg.image.load(image).convert_alpha()
        self.image = pyg.transform.scale(self.ogimage, (width, height))
        self.rect = self.image.get_rect(center = self.pos)
        self.pressed = pressed
        self.freed = freed
        self.heave = heave
        GUI.allGUI.append(self)

    @classmethod
    def interaction(cls, event, mouse_pos):
        """
        Goes into the event loop, handles all possible mouse interactions with GUI\n
        """
        for obj in cls.activeGUI:
            if obj.rect.collidepoint(mouse_pos):
                if event.type == pyg.MOUSEBUTTONDOWN:
                    obj.clicked()
                if pyg.mouse.get_pressed()[0] and event.type == pyg.MOUSEMOTION:
                    obj.dragged()
                if event.type == pyg.MOUSEBUTTONUP:
                    obj.released()

    @classmethod
    def activate(cls, *args):
        cls.activeGUI.add(args)

    @classmethod
    def deactivate(cls, *args):
        cls.activeGUI.remove(args)

    # maybe ill add functionality for buttons physically going down, sound effects, etc
    def clicked(self):
        self.pressed(self)

    def released(self):
        self.freed(self)

    def dragged(self):
        self.heave(self)

    def update(self):
        """
        Properly scales every GUI object based on the new size of the window
        """
        displaySize = pyg.display.get_window_size()
        scaleX = displaySize[0]/ogSize[0]
        scaleY = displaySize[1]/ogSize[1]
        # take the min of the x/y scales so the image itself retains its original aspect ratio
        scale = min(scaleX, scaleY)

        self.image = pyg.transform.scale(self.ogimage, (self.dimensions[0]*scale, self.dimensions[1]*scale))
        self.rect = self.image.get_rect(center = (self.pos[0]*scaleX, self.pos[1]*scaleY))
