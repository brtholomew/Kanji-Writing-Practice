# test rendering svgs
import pygame as pyg
from io import BytesIO
import gui

pyg.init()

gui.initDisplay((300, 300))

class Kanji():
    """
    Class for breaking down written kanji into its individual strokes
    """

    def __init__(self, kanji: str):
        self.svgList, self.metadata = Kanji.deconstructKanji(kanji)
        self.IOList = Kanji.svgTextToIO(self.svgList)

    @staticmethod
    def extractPosition(svg: str, value: str):
        """
        Returns the start and end index of a number associated to a specific value in an svg file as a tuple
        """
        startIndex = svg.find(value)

        # SURELY THERE'S A BETTER WAY OF DOING THIS???
        while svg[startIndex] not in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
            startIndex += 1
        endIndex = startIndex
        while svg[endIndex] in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
            endIndex += 1
        return (startIndex, endIndex)
    
    @staticmethod
    def extractValue(svg: str, value: str):
        """
        Returns the number associated to a specific value in an svg file
        """
        startIndex, endIndex = Kanji.extractPosition(svg, value)
        number = []
        for i in range(startIndex, endIndex):
            number.append(svg[i])
        return int("".join(number))

    @staticmethod
    def findKanji(kanji: str):
        """
        Returns the file path for a desired kanji
        """
        fileName = hex(ord(kanji)).replace("x", "")
        return f"kanji/{fileName}.svg"

    @staticmethod
    def deconstructKanji(kanji: str):
        """
        Returns a list where every item is a stroke of a kanji in svg text format, as well as the metadata
        """
        with open(Kanji.findKanji(kanji), "r", encoding = "utf-8") as svg:
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
        svgList = []
        for path in paths:
            svgList.append(f"{svgTag}\n{brushInfo}\n\t{path}\n</g>\n</svg>")

        metadata = dict(width = Kanji.extractValue(svgTag, "width"), height = Kanji.extractValue(svgTag, "height"), strokeWidth = Kanji.extractValue(brushInfo, "stroke-width"))
        print(metadata)
        return svgList, metadata

    @staticmethod
    def svgTextToIO(*args):
        """
        Converts an svg in text format to a filelike object
        """
        IOList = []
        for i in args:
            # code taken from https://python-forum.io/thread-40976.html
            # i don't really get it but basically it turns a string into bytes, which is then turned into a filelike object, which can be read by pygame's image loader
            IOList.append(BytesIO(bytes(i, encoding = "utf-8")))
        return IOList if len(IOList) > 1 else IOList[0]
    
    def scale(self, scale):
        for i in self.svgList.split("\n"):
            pass

temp = []
for i in Kanji.deconstructKanji("飲")[0]:
    temp.append(gui.GUI((150, 150), (109, 109), image = Kanji.svgTextToIO(i)))
gui.GUI.activate(temp)

running = True

while running:

    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            running = False

    gui.screen.fill("white")

    gui.GUI.activeGUI.draw(gui.screen)

    pyg.display.flip()