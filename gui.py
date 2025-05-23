# module for handling gui elements (such as buttons)
import pygame as pyg
from typing import Callable, TypeAlias

pyg.init()

def initDisplay(size: tuple = (100, 100), caption:str = "Pygame"):
    """
    Initializes a display at the desired lowest possible size\n
    Necessary for allowing the GUI to scale properly
    """
    global ogSize, currentSize, screen, scaleX, scaleY, scale
    ogSize, currentSize = size, size
    scaleX, scaleY, scale = 1, 1, 1
    # take the min of the x/y scales so the image itself retains its original aspect ratio
    screen = pyg.display.set_mode(size = ogSize, flags = pyg.RESIZABLE)
    pyg.display.set_caption(caption)

def scaleDisplay(event, *args):
    """
    Correctly scales everything when the pygame display is resized\n
    Accepts any sprite object, or object with a scale method
    """
    global currentSize, scaleX, scaleY, scale
    # prevent the screen from getting smaller than the designated amount
    screen = pyg.display.set_mode((max(ogSize[0], event.x), max(ogSize[1], event.y)), flags = pyg.RESIZABLE)

    displaySize = pyg.display.get_window_size()
    scaleX = displaySize[0]/ogSize[0]
    scaleY = displaySize[1]/ogSize[1]
    # take the min of the x/y scales so the image itself retains its original aspect ratio
    scale = min(scaleX, scaleY)

    # this is exclusively used for calculating missing original attributes
    prevX = currentSize[0]/ogSize[0]
    prevY = currentSize[1]/ogSize[1]
    prev = min(prevX, prevY)

    for sprite in args:
        if not isinstance(sprite, GUI):
            # sprite is probably missing all the necessary attributes
            sprite.ogimage = sprite.image
            sprite.pos = (sprite.rect.centerx/prevX, sprite.rect.centery/prevY)
            sprite.dimensions = (sprite.rect.w/prev, sprite.rect.h/prev)
        sprite.image = pyg.transform.scale(sprite.ogimage, (sprite.dimensions[0]*scale, sprite.dimensions[1]*scale))
        sprite.rect = sprite.image.get_rect(center = (sprite.pos[0]*scaleX, sprite.pos[1]*scaleY))

    currentSize = displaySize

point: TypeAlias = tuple[int, int]
guiEvent: TypeAlias = Callable[["GUI"], None]

class GUI(pyg.sprite.Sprite):
    """
    Subclass of pygame's sprite class for GUI elements\n

    pressed - function that runs when the GUI is clicked on\n
    released - function that runs when the GUI is no longer clicked on\n
    heave - function that runs when the GUI is being dragged\n
    active - function that runs if the GUI is being updated (useful for hovering)\n

    pressed, released, heave, and active SHOULD HAVE A self PARAMETER LIKE A REGULAR CLASS METHOD\n

    if you're using active, make sure to use activeGUI.update()\n
    """
    activeGUI = pyg.sprite.Group()
    allGUI = []

    def __init__(self, pos: point, dimensions: point, image = "assets/placeholder.png", pressed: guiEvent = lambda x: print(f"{x} was clicked!"), freed: guiEvent = lambda x: print(f"{x} was released!"), heave: guiEvent = lambda x: print(f"{x} is being dragged!"), active: guiEvent = lambda x: None):
        super().__init__()
        self.pos: point = pos
        self.dimensions: point = dimensions
        self.ogimage = pyg.image.load(image).convert_alpha()
        self.image = pyg.transform.scale(self.ogimage, self.dimensions)
        self.rect = self.image.get_rect(center = self.pos)

        self.dragging = False
        self.hovering = False
        self.pressed: guiEvent = pressed
        self.freed: guiEvent = freed
        self.heave: guiEvent = heave
        self.active: guiEvent = active
        GUI.allGUI.append(self)

    @classmethod
    def interaction(cls, event, mouse_pos):
        """
        Goes into the event loop, handles all possible mouse interactions with GUI\n
        """
        for obj in cls.activeGUI:
            if obj.hovering:
                if event.type == pyg.MOUSEBUTTONDOWN:
                    obj.clicked()
                if event.type == pyg.MOUSEMOTION and obj.dragging: #and pyg.mouse.get_pressed()[0]:
                    obj.dragged()
                if event.type == pyg.MOUSEBUTTONUP and obj.dragging:
                    obj.released()
            elif event.type == pyg.MOUSEBUTTONUP:
                    obj.dragging = False

    @classmethod
    def activate(cls, *args):
        cls.activeGUI.add(args)

    @classmethod
    def deactivate(cls, *args):
        cls.activeGUI.remove(args)

    # maybe ill add functionality for buttons physically going down, sound effects, etc
    def clicked(self):
        self.dragging = True
        self.pressed(self)

    def released(self):
        self.dragging = False
        self.freed(self)

    def dragged(self):
        self.heave(self)

    def update(self, mouse_pos: point):
        self.hovering = False if not self.rect.collidepoint(mouse_pos) else True
        self.active(self)