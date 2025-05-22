# test rendering svgs
import pygame as pyg
from io import BytesIO
import gui

pyg.init()

gui.initDisplay((300, 300))

def findKanji(kanji):
    """
    Returns the file path for a desired kanji
    """
    fileName = hex(ord(kanji)).replace("x", "")
    return f"kanji/{fileName}.svg"


def deconstructKanji(kanji):
    """
    Returns a list containing every stroke of a particular kanji
    """
    with open(findKanji(kanji), "r", encoding = "utf-8") as svg:
        file = svg.read().split("\n")
        paths = []
        for line in file:
            # find the svg tag
            if "<svg" in line:
                svgTag = line
            # and every "path" which is basically a drawn line
            elif "<path" in line:
                paths.append(line.replace("\t", ""))
        # brush info is always 1 line below svg tag (at least for kanjivg files)
        brushInfo = file[file.index(svgTag)+1]
    strokeList = []
    for path in paths:
        # code taken from https://python-forum.io/thread-40976.html
        # i don't really get it but basically it turns a string into bytes, which is then turned into a filelike object, which can be read by pygame's image loader
        strokeList.append(BytesIO(bytes(f"{svgTag}\n{brushInfo}\n\t{path}\n</g>\n</svg>", "utf-8")))
    return strokeList

temp = []
for i in deconstructKanji("食"):
    temp.append(gui.GUI((150, 150), (200, 200), image = i))
gui.GUI.activate(temp)

running = True

while running:

    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            running = False

    gui.screen.fill("white")

    gui.GUI.activeGUI.draw(gui.screen)

    pyg.display.flip()