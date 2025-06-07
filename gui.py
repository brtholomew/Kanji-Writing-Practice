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

    screen = pyg.display.set_mode(size = ogSize, flags = pyg.RESIZABLE)
    pyg.display.set_caption(caption)

def scaleDisplay(event, *args):
    """
    Correctly scales everything when the pygame display is resized\n
    Accepts any sprite object, or object with a "scale" method
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
        if isinstance(sprite, pyg.sprite.Sprite):
            if not isinstance(sprite, GUI):
                # sprite is probably missing all the necessary attributes
                sprite.ogimage = sprite.image
                sprite.pos = (sprite.rect.centerx/prevX, sprite.rect.centery/prevY)
                sprite.dimensions = (sprite.rect.w/prev, sprite.rect.h/prev)
            sprite.image = pyg.transform.scale(sprite.ogimage, (sprite.dimensions[0]*scale, sprite.dimensions[1]*scale))
            sprite.rect = sprite.image.get_rect(center = (sprite.pos[0]*scaleX, sprite.pos[1]*scaleY))
            # im too lazy to code good text scaling so here's my terrible solution
            if hasattr(sprite, "fontInfo"):
                guiText = sprite.fontInfo["gui"]
                guiText.image = pyg.font.SysFont("uddigikyokashonr", sprite.rect.h).render(sprite.fontInfo["text"], False, sprite.fontInfo["color"])
                guiText.rect = guiText.image.get_rect(center = (guiText.pos[0]*scaleX, guiText.pos[1]*scaleY))
        if hasattr(sprite, "scale") and callable(sprite.scale):
            sprite.scale()

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

    def __init__(self, pos: point, dimensions: point, image: str | pyg.surface.Surface = "assets/placeholder.png", pressed: guiEvent = lambda x: print(f"{x} was clicked!"), freed: guiEvent = lambda x: print(f"{x} was released!"), heave: guiEvent = lambda x: print(f"{x} is being dragged!"), active: guiEvent = lambda x: None):
        super().__init__()
        self.pos: point = pos
        self.dimensions: point = dimensions
        if isinstance(image, str):
            self.ogimage = pyg.image.load(image).convert_alpha()
        elif isinstance(image, pyg.surface.Surface):
            self.ogimage = image
        else:
            raise TypeError("Invalid image type")
        self.image = pyg.transform.scale(self.ogimage, [i*scale for i in self.dimensions])
        self.rect = self.image.get_rect(center = (pos[0]*scaleX, pos[1]*scaleY))

        self.dragging = False
        self.hovering = False
        self.enabled = True 

        self.pressed: guiEvent = pressed
        self.freed: guiEvent = freed
        self.heave: guiEvent = heave
        self.active: guiEvent = active
        GUI.allGUI.append(self)

    @classmethod
    def interaction(cls, event):
        """
        Goes into the event loop, handles most possible mouse interactions with GUI\n
        Requires the gui to be updated to work
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
        return args

    @classmethod
    def deactivate(cls, *args):
        cls.activeGUI.remove(args)
        return args

    @staticmethod
    def enable(*args):
        for i in args:
            i.enabled = True

    @staticmethod
    def disable(*args):
        for i in args:
            i.enabled = False

    def delete(self):
        GUI.deactivate(GUI.allGUI.pop(GUI.allGUI.index(self)))

    def write(self, text: str, color = "white"):
        if hasattr(self, "fontInfo"):
            GUI.deactivate(self.fontInfo["gui"])
        # im too lazy to code good text scaling so here's my terrible solution
        guiText = GUI.activate(GUI(self.pos, self.dimensions, image = pyg.font.SysFont("uddigikyokashonr", self.rect.h).render(text, False, color)))[0]
        # i forgot so im leaving a note here but IM REMOVING guiText FROM THE ALL GUI LIST BECAUSE THAT'S HOW IT WILL SCALE PROPERLY
        GUI.allGUI.remove(guiText)
        self.fontInfo = {"gui" : guiText, "text" : text, "color" : color}

    # maybe ill add functionality for buttons physically going down, sound effects, etc
    def clicked(self):
        if self.enabled:
            self.dragging = True
            self.pressed(self)

    def released(self):
        if self.enabled:
            self.dragging = False
            self.freed(self)

    def dragged(self):
        if self.enabled:
            self.heave(self)

    def update(self, mouse_pos: point):
        self.hovering = True if self.rect.collidepoint(mouse_pos) else False
        self.active(self)