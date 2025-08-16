# module for handling gui elements (such as buttons)
import pygame as pyg
from os import path, environ
from typing import Callable, Union #, TypeAlias

flags = pyg.RESIZABLE | pyg.DOUBLEBUF

pyg.init()

def assetPath(file: str):
    return path.join(path.dirname(__file__), "assets", file)

def initDisplay(size: tuple = (100, 100), caption:str = "Pygame", pos: tuple = None):
    """
    Initializes a display at the desired lowest possible size\n
    Necessary for allowing the GUI to scale properly
    """
    global ogSize, currentSize, screen, scaleX, scaleY, scale
    ogSize, currentSize = size, size
    scaleX, scaleY, scale = 1, 1, 1

    windowInfo = pyg.display.Info()

    # taken from stackoverflow: https://stackoverflow.com/questions/4135928/pygame-display-position
    environ['SDL_VIDEO_WINDOW_POS'] = f"{pos[0]},{pos[1]}" if pos else f"{windowInfo.current_w/2},{windowInfo.current_h/2}"

    screen = pyg.display.set_mode(size = ogSize, flags = flags)
    pyg.display.set_caption(caption)

def scaleDisplay(event, *args):
    """
    Correctly scales everything when the pygame display is resized\n
    Accepts any sprite object, or object with a "scale" method, though a pixel may be lost.\n
    """
    global currentSize, scaleX, scaleY, scale
    # prevent the screen from getting smaller than the designated amount
    screen = pyg.display.set_mode((max(ogSize[0], event.x), max(ogSize[1], event.y)), flags = flags)

    displaySize = pyg.display.get_window_size()
    scaleX = displaySize[0]/ogSize[0]
    scaleY = displaySize[1]/ogSize[1]
    # maintain original aspect ratio
    scale = min(scaleX, scaleY)

    # this is exclusively used for calculating missing original attributes
    prevX = currentSize[0]/ogSize[0]
    prevY = currentSize[1]/ogSize[1]
    prev = min(prevX, prevY)

    for sprite in args:
        if isinstance(sprite, pyg.sprite.Sprite):
            if not all(hasattr(sprite, i) for i in ("ogimage", "pos", "dimensions")):
                sprite.ogimage = sprite.image
                sprite.pos = (sprite.rect.centerx/prevX, sprite.rect.centery/prevY)
                sprite.dimensions = (sprite.rect.w/prev, sprite.rect.h/prev)
            _scale(sprite)
            if hasattr(sprite, "fontInfo"):
                guiText = sprite.fontInfo["gui"]
                guiText.image = pyg.font.SysFont("uddigikyokashonr", sprite.rect.h).render(sprite.fontInfo["text"], False, sprite.fontInfo["color"])
                guiText.image.set_alpha(sprite.image.get_alpha())
                guiText.rect = guiText.image.get_rect(midtop = sprite.rect.midtop)
        if hasattr(sprite, "scale") and callable(sprite.scale):
            sprite.scale()

    currentSize = displaySize


# point: TypeAlias = tuple[int, int]
# guiEvent: TypeAlias = Callable[["GUI"], None]

class Spritesheet():
    """
    For GUI buttons\n
    Only supports sheets with one row
    """
    def __init__(self, dimensions: tuple[int, int], image: str):
        # NOTE: dimensions is the size of every sprite in the spritesheet, NOT the desired size
        self.state = 0
        self.width = dimensions[0]
        self.height = dimensions[1]
        self.spritesheet = pyg.image.load(assetPath(image)).convert_alpha()

    def returnState(self, state: int = None):
        """
        Every button has 3 states: default (0), pressed (1), and disabled (2)
        """
        if state == None:
            state = self.state
        else:
            self.state = state
        return self.spritesheet.subsurface((self.width*state, 0), (self.width, self.height))

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

    def __init__(self, pos: tuple[int, int], dimensions: tuple[int, int], image: Union[str, pyg.surface.Surface, Spritesheet] = assetPath("placeholder.png"), pressed:  Callable[["GUI"], None] = lambda x: None, freed: Callable[["GUI"], None] = lambda x: None, heave: Callable[["GUI"], None] = lambda x: None, active: Callable[["GUI"], None] = lambda x: None):
        super().__init__()
        self.pos: tuple[int, int] = pos
        self.dimensions: tuple[int, int] = dimensions
        if type(image) == str:
            self.ogimage = pyg.image.load(assetPath(image)).convert_alpha()
        elif type(image) == pyg.surface.Surface or type(image) == Spritesheet:
            self.ogimage = image
        else:
            raise TypeError("Invalid image type")
        _scale(self)

        self.dragging = False
        self.hovering = False
        self.enabled = True 

        self.pressed: Callable[["GUI"], None] = pressed
        self.freed: Callable[["GUI"], None] = freed
        self.heave: Callable[["GUI"], None] = heave
        self.active: Callable[["GUI"], None] = active
        GUI.allGUI.append(self)

    @classmethod
    def interaction(cls, event):
        """
        Goes into the event loop, handles most possible mouse interactions with GUI\n
        Requires the GUI to be updated to work
        """
        for obj in cls.activeGUI:
            if obj.hovering:
                if event.type == pyg.MOUSEBUTTONDOWN:
                    obj.clicked()
                if event.type == pyg.MOUSEMOTION and obj.dragging:
                    obj.dragged()
                if event.type == pyg.MOUSEBUTTONUP and obj.dragging:
                    obj.released()
            elif event.type == pyg.MOUSEBUTTONUP:
                    obj.dragging = False
                    obj.changeState(0) if hasattr(obj, "ogimage") and obj.enabled else None

    @classmethod
    def activate(cls, *args):
        cls.activeGUI.add(args)
        for i in args:
            if hasattr(i, "fontInfo"):
                cls.activeGUI.add(i.fontInfo["gui"])
        return args

    @classmethod
    def deactivate(cls, *args):
        cls.activeGUI.remove(args)
        for i in args:
            if hasattr(i, "fontInfo"):
                cls.activeGUI.remove(i.fontInfo["gui"])
        return args

    @staticmethod
    def enable(*args):
        for i in args:
            i.enabled = True
            i.changeState(0)

    @staticmethod
    def disable(*args):
        for i in args:
            i.enabled = False
            i.changeState(2)

    @staticmethod
    def trueTransform(sprite: pyg.sprite.Sprite, method:str, *args):
        "Affects image and ogimage (if possible)"
        getattr(sprite.image, method)(*args)
        if hasattr(sprite, "ogimage"):
            getattr(sprite.ogimage if isinstance(sprite.ogimage, pyg.surface.Surface) else sprite.ogimage.returnState(), method)(*args)

    def changeState(self, newState: int):
        """
        0: default\n
        1: being held down\n
        2: disabled\n
        """
        if not isinstance(self.ogimage, Spritesheet):
            return
        self.ogimage.state = newState
        _scale(self)

    def delete(self):
        GUI.allGUI.remove(self)
        GUI.deactivate(self)

    def write(self, text: str, color = "white"):
        """
        fontInfo = {\n
            "gui" : GUI,\n
            "text" : str,\n
            "color" : pyg.ColorValue\n
        }\n
        New text is a GUI object but is not stored in allGUI
        """
        if hasattr(self, "fontInfo"):
            GUI.deactivate(self.fontInfo["gui"])
        guiText = GUI.activate(GUI(self.pos, self.dimensions))[0]
        guiText.image = pyg.font.SysFont("uddigikyokashonr", self.rect.h).render(str(text), False, color)
        guiText.rect = guiText.image.get_rect(midtop = self.rect.midtop)
        # text scaling is handled separately from regular GUI
        GUI.allGUI.remove(guiText)
        self.fontInfo = {"gui" : guiText, "text" : text, "color" : color}

    def clicked(self):
        if self.enabled:
            self.dragging = True
            self.changeState(1)
            self.pressed(self)

    def released(self):
        if self.enabled:
            self.dragging = False
            self.changeState(0)
            self.freed(self)

    def dragged(self):
        if self.enabled:
            self.heave(self)

    def update(self, mouse_pos: tuple[int, int]):
        self.hovering = True if self.rect.collidepoint(mouse_pos) else False
        self.active(self)

def _scale(sprite: Union[pyg.sprite.Sprite, GUI]):
    "Only for updating when changing states/sizes"
    sprite.image = pyg.transform.scale(sprite.ogimage if isinstance(sprite.ogimage, pyg.surface.Surface) else sprite.ogimage.returnState(), [i*scale for i in sprite.dimensions])
    sprite.rect = sprite.image.get_rect(center = (sprite.pos[0]*scaleX, sprite.pos[1]*scaleY))

if __name__ == "__main__":
    # test rendering
    initDisplay((300, 300))
    promptGUI = GUI((150, 30), (30, 30), image = "grid.png")
    promptGUI.write("test")
    
    running = True

    while running:
        mouse_pos = pyg.mouse.get_pos()

        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                running = False
            elif event.type == pyg.WINDOWRESIZED:
                scaleDisplay(event, *GUI.allGUI)
            GUI.interaction(event)
        screen.fill("black")

        GUI.activeGUI.draw(screen)
        GUI.activeGUI.update(mouse_pos)

        pyg.display.flip()
pyg.display.quit()