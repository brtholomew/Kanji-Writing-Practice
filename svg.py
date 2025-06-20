# module for handling svgs
import pygame as pyg
import gui
from io import BytesIO
from typing import Union
from os import path

class SvgError(Exception):
    "An error occured while parsing data related to SVGs"
    pass

# -------------------- SVG Functions --------------------
def listToFloat(list: list):
    return float("".join(list))

def lolToCoords(list: list):
    "List of lists where lists is a float broken into strings, converts to x/y coordinates"
    return (listToFloat(list[0]), listToFloat(list[1]))

def distanceFormula(p1: tuple[int, int], p2: tuple[int, int]):
    return ((p2[0]-p1[0])**2+(p2[1]-p1[1])**2)**0.5

def replaceSubstring(stri: str, newValue: Union[str, float], index: tuple):
    """
    Returns a string with part of it changed based on a start/end index\n
    Also returns the part that was changed
    """
    stri = list(stri)
    oldValue = []
    for i in range(*index):
        oldValue.append(stri.pop(index[0]))
    stri.insert(index[0], str(newValue))
    return "".join(stri), "".join(oldValue)

def standardizePath(svg: str, startIndex: int, endIndex: int):
    "Fixes any inconsistencies in the path parameter for extractPathParameter"
    # hopefully i won't have to update this too often
    temp = []
    for i in range(startIndex, endIndex):
        if not svg[i] == " ":
            temp.append(svg[i])
        else:
            if svg[i-1].isnumeric() and svg[i+1].isnumeric():
                temp.append(",")
    return replaceSubstring(svg, "".join(temp), (startIndex, endIndex))[0]


def extractPathParameter(svg: str):
    """
    Special function specifically designed for extracting the d parameter in the path of an svg text file\n
    Every move command is mapped to a list of xy coordinates, where every x/y is stored as a list\n
    ex.\n
    d = [\n
        "C": [\n
            [["5","0"], ["2","5"]],\n
            [["-","0",".","2"], ["0",".","4"]],\n
            [["x3"], ["y3"]]\n
        ],\n
        "m" : ...
    ]\n
    """
    try:
        # temporary solution
        startIndex = svg.index(' d="')
    except ValueError:
        raise SvgError(f"Could not find d parameter in: {svg}")
    startIndex = svg.index('"', startIndex) + 1
    endIndex = svg.index('"', startIndex)
    svg = standardizePath(svg, startIndex, endIndex)
    endIndex = svg.index('"', startIndex) # im crying
    d = []
    # counter tracks if we're on an x or y coordinate; 0 = x, 1 = y
    counter = 0
    # coordinate counter 
    cCounter = 1

    # this for loop might be the most horrid abombination i've ever created in my entire life
    for i in range(startIndex, endIndex):
        # link current command to a list of list of x and y coordinates
        # every x/y coordinate will be represented as a list
        if svg[i].isalpha():
            currentCommand = svg[i]
            d.append({currentCommand: []})
            # create new x/y coordinate list
            counter = 0
            d[-1][currentCommand].append([])
            cCounter = 1
        elif svg[i] not in (",", "-"):
            try:
                d[-1][currentCommand][-1][counter].append(svg[i])
            except IndexError: # missing x/y coordinate list
                d[-1][currentCommand][-1].append([svg[i]])
        else: # svg[i] is either a dash or comma
            # if there's an empty x/y list and svg[i] is a dash
            try:
                if svg[i] == "-" and not d[-1][currentCommand][-1][-1]:
                    d[-1][currentCommand][-1][-1].append(svg[i])
                    continue
            except IndexError: # missing x/y coordinate list
                    d[-1][currentCommand][-1].append([svg[i]])
                    continue
            # if a x/y coordinate is missing
            if len(d[-1][currentCommand][-1]) < 2:
                # only move to the y coordinate if the x coordinate is there
                counter += 1 if len(d[-1][currentCommand][-1]) == 1 else 0
                # for SOME REASON "-" represents a comma AND a negative number thanks a lot
                d[-1][currentCommand][-1].append(["-"] if svg[i] == "-" else [])
            else: # create new list of x/y coordinates
                counter = 0
                if cCounter == 3: # handles when a curveto command is given a multiple of 3 coordinates
                    # NOTE: if something regarding svgs breaks, it's probably because i need to code functionality for this for EVERY command
                    d.append({currentCommand: []})
                    cCounter = 0
                d[-1][currentCommand].append([["-"]] if svg[i] == "-" else [])
                cCounter += 1
    # real quick check if the svg has been processed properly
    for i in d:
        for k,v in i.items():
            if k.upper() == "C" and not len(v) == 3:
                raise SvgError(f"An error occured while processing this svg: {svg}")
    return d

def extractPosition(svg: str, keyword: str, start: int = 0):
    """
    Returns the start and end index of a value associated to a specific keyword in an svg file as a tuple\n
    If endIndex is -1, no value is associated with keyword, and startIndex becomes the starting index of the keyword
    """
    startIndex = svg.index(keyword, start)

    try:
        while svg[startIndex] not in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", " "):
            startIndex += 1
    except ValueError:
        # no value associated with keyword
        return svg.index(keyword, start), -1
    endIndex = startIndex
    try:
        while svg[endIndex] in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", " "):
            endIndex += 1
    except ValueError:
        # svg file ends in a number somehow
        raise SvgError(f"This SVG file is invalid: {svg}")
    return (startIndex, endIndex)

def extractValue(svg: str, keyword: str):
    "Returns the value associated to a specific keyword in an svg file"
    startIndex, endIndex = extractPosition(svg, keyword)
    value = []
    for i in range(startIndex, endIndex):
        value.append(svg[i])
    return int("".join(value))

def alterValue(svg: str, **kwargs):
    """
    Returns an svg string file with specific values changed\n
    Will also properly apply width and height dilations
    """
    for keyword, value in kwargs.items():
        startIndex, endIndex = extractPosition("".join(svg), keyword)
        svg, oldValue = replaceSubstring(svg, value, (startIndex, endIndex))

        if keyword == "width" or keyword == "height":
            # hey why didn't you just use an external library for this?
            d = extractPathParameter(svg)

            temp = ""
            # for every move command
            for i in d:
                for k, v in i.items():
                    temp = f"{temp}{k}"
                    # for every x/y coordinate
                    for c in v:
                        x = float("".join(c[0]))*(value/float(oldValue) if keyword == 'width' else 1)
                        y = float("".join(c[1]))*(value/float(oldValue) if keyword == 'height' else 1)
                        temp = f"{temp}{round(x, 2)},{round(y, 2)},"
                    temp = list(temp)
                    del temp[-1]
                    temp = "".join(temp)
            temp = temp.replace(",-", "-")

            startIndex = svg.index('"', svg.index(' d="')) + 1
            endIndex = svg.index('"', startIndex)
            svg = replaceSubstring(svg, temp, (startIndex, endIndex))[0]
            
    return svg

# -------------------- Bezier Class --------------------
class Bezier():
    "Converts a svg into an object that contains a list of bezier curves"
    def __init__(self, svg: str):
        self.controlPoints = []
        finalPos = (0, 0)

        for i in extractPathParameter(svg):
            for k, v in i.items():
                if k.upper() == "M":
                    for c in v:
                        x, y = lolToCoords(c)
                        # final point becomes the initial point of the next curve
                        finalPos = (x, y) if k.isupper() else (finalPos[0]+x, finalPos[1]+y)
                elif k.upper() == "C":
                    self.controlPoints.append([])
                    self.controlPoints[-1].append(finalPos)
                    for c in v:
                        x, y = lolToCoords(c)
                        self.controlPoints[-1].append((x, y) if k.isupper() else (finalPos[0]+x, finalPos[1]+y))
                    # final point becomes the initial point of the next curve
                    finalPos = self.controlPoints[-1][-1]
                elif k.upper() == "S":
                    controlPoint = self.controlPoints[-1][-2]
                    reflectedPoint = (2*finalPos[0]-controlPoint[0], 2*finalPos[1]-controlPoint[1])

                    self.controlPoints.append([])
                    self.controlPoints[-1].extend((finalPos, reflectedPoint))
                    for c in v:
                        x, y = lolToCoords(c)
                        self.controlPoints[-1].append((x, y) if k.isupper() else (finalPos[0]+x, finalPos[1]+y))
                    finalPos = self.controlPoints[-1][-1]
                else:
                    raise SvgError(f"Bezier class not built for processing this command: {k}")
        
        # build the equations for every bezier curve
        self.functions = []
        for i in self.controlPoints:
            # explicit form of equation for cubic bezier curve
            self.functions.append(lambda t, i=i: ((1-t)**3*i[0][0] + 3*(1-t)**2*t*i[1][0] + 3*(1-t)*t**2*i[2][0] + t**3*i[3][0], (1-t)**3*i[0][1] + 3*(1-t)**2*t*i[1][1] + 3*(1-t)*t**2*i[2][1] + t**3*i[3][1]))

    def distInfoInit(self):
        # get the dist info across all bezier curves
        # code taken from roblox blog given to me by issai
        # thank you issai https://web.archive.org/web/20201115172941/https://developer.roblox.com/en-us/articles/Bezier-curves
        self.distInfo = {}
        total = 0
        for f in self.functions:
            for n in range(0, 100, 1):
                p1, p2 = f(n/100), f((n+1)/100)
                dist = distanceFormula(p1, p2)
                self.distInfo[total] = [dist, p1, p2]
                total += dist
            self.total = total

    def bezierPercent(self, t: float):
        """
        Returns the approximate point of the combined beziers based on the percent linear distance it has traveled in total\n
        """
        if not hasattr(self, "distInfo"):
            self.distInfoInit()
        # thank you issai https://web.archive.org/web/20201115172941/https://developer.roblox.com/en-us/articles/Bezier-curves
        dist = t*self.total
        if dist == 0 or dist == self.total:
            # no interpolation needed
            return list(self.distInfo.values())[0][1] if dist == 0 else list(self.distInfo.values())[-1][2]
        for k, v in self.distInfo.items():
            # if we go past the percent linear distance
            if dist - k < 0:
                break
            length = k
        info = self.distInfo[length]
        # calculate the percent off we are
        percent = (dist - length)/info[0]
        # linearly interpolate the point
        return (round(info[1][0]+(info[2][0]-info[1][0])*percent, 2), round(info[1][1]+(info[2][1]-info[1][1])*percent, 2))

# -------------------- Kanji Class --------------------

class Kanji():
    """
    Class for breaking down written kanji into its individual strokes
    """
    def __init__(self, kanji: str, dimensions: tuple[int, int], strokeWidth: float, points: int = 50):
        self.str = kanji
        svgList = Kanji.deconstructKanji(kanji)[0]
        self.svgList = []
        for i in svgList:
            self.svgList.append(alterValue(i, width = dimensions[0], height = dimensions[1], **{"stroke-width" : strokeWidth}, viewBox = f"0 0 {dimensions[0]} {dimensions[1]}"))

        self.metadata = dict(width = dimensions[0], height = dimensions[1], strokeWidth = strokeWidth)

        # linearly interpolated points for every stroke in this list
        self.pBzPoints = []
        
        try:
            for b in [Bezier(i) for i in self.svgList]:
                self.pBzPoints.append([])
                for p in range(0, points):
                    self.pBzPoints[-1].append(b.bezierPercent(p/(points-1)))
        except SvgError:
            self.pBzPoints = "N/A"
            print(f"This kanji doesn't have an animation: {self.str}, file: {Kanji.findKanji(self.str)}")
        
        self.surfList = Kanji.svgTextToSurf(*self.svgList)
        self.maskList = [pyg.mask.from_surface(i) for i in self.surfList]

    @staticmethod
    def findKanji(kanji: str):
        """
        Returns the file path for a desired kanji
        """
        fileName = hex(ord(kanji)).replace("x", "")
        return path.join(path.dirname(__file__), "kanji", f"{fileName}.svg")

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

        metadata = dict(width = extractValue(svgTag, "width"), height = extractValue(svgTag, "height"), strokeWidth = extractValue(brushInfo, "stroke-width"))
        return svgList, metadata

    @staticmethod
    def svgTextToSurf(*args):
        """
        Converts an svg in text format to a list of pygame surfaces
        """
        IOList = []
        for i in args:
            # code taken from https://python-forum.io/thread-40976.html
            # i don't really get it but basically it turns a string into bytes, which is then turned into a filelike object, which can be read by pygame's image loader
            IOList.append(pyg.image.load(BytesIO(bytes(i, encoding = "utf-8"))).convert_alpha())
        return [pyg.image.load(BytesIO(bytes(i, encoding = "utf-8"))).convert_alpha() for i in args]
    
    def scale(self):
        self.surfList = Kanji.svgTextToSurf(*[alterValue(i, width = self.metadata["width"]*gui.scale, height = self.metadata["height"]*gui.scale, **{"stroke-width": self.metadata["strokeWidth"]*gui.scale}, viewBox = f"0 0 {self.metadata['width']*gui.scale} {self.metadata['height']*gui.scale}") for i in self.svgList])
        self.maskList = [pyg.mask.from_surface(i) for i in self.surfList]


if __name__ == "__main__":
    pyg.init()

    gui.initDisplay((300, 300))  

    # TEST EVERY SINGLE KANJI FILE
    # from os import scandir
    # import csv
    # with scandir(path.join(path.dirname(__file__), "kanji")) as entries:
    #     with open("kanji_csv_data.csv", mode = "w", newline = "") as csvFile:
    #         csvWriter = csv.DictWriter(csvFile, fieldnames = ["Kanji", "did_load", "anim_did_load"])
    #         csvWriter.writeheader()
    #         for entry in entries:
    #             if not entry.is_file():
    #                 continue
    #             fileName = path.splitext(path.basename(entry))[0]
    #             kanjiStr = chr(int(fileName, 16))
    #             if not ord(kanjiStr) >= 19968 and ord(kanjiStr) <= 40879:
    #                 continue
    #             try:
    #                 kanji = Kanji(kanjiStr, (175, 175), 8)
    #             except FileNotFoundError:
    #                 print(f"Failed to load this file: {fileName}")
    #                 continue
    #             except SvgError:
    #                 csvWriter.writerow({"Kanji": fileName, "did_load": False, "anim_did_load": False})
    #                 continue
    #             if kanji.pBzPoints == "N/A":
    #                 csvWriter.writerow({"Kanji": fileName, "did_load": True, "anim_did_load": False})
    #                 continue
    #             else:
    #                 csvWriter.writerow({"Kanji": fileName, "did_load": True, "anim_did_load": True})

    # test rendering

#     print(extractPathParameter("""<svg xmlns="http://www.w3.org/2000/svg" width="109" height="109" viewBox="0 0 109 109">
# <g id="kvg:StrokePaths_06163" style="fill:none;stroke:#000000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;">
# 	<path id="kvg:06163-s4" kvg:type="㇛" d="m51.6,15.24c0.83,0.83,1.14,2.12,1.02,3.3-0.74,7.34-1.75,14.09-3.1,18.7-0.5,1.69,0.19,2.75,1.57,2.46,8.11,-1.7,15.02,-2.59,24.42,-3.15,2.09,-0.13,4.3,-0.23,6.68,-0.33"/>
# </g>
# </svg>"""))
    print(hex(ord("𠂊")))
    testKanji = Kanji(chr(int("2008a", 16)), (300, 300), 8)
    #print(testKanji.pBzPoints)
    blitSequence = [(surf, (0, 0)) for surf in testKanji.surfList]
    # TODO: cannot change color of svg with altervalue

    # pygame

    running = False

    while running:

        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                running = False
            if event.type == pyg.WINDOWRESIZED:
                gui.scaleDisplay(event, *gui.GUI.allGUI)
        gui.screen.fill("white")
        pyg.Surface.blits(gui.screen, blitSequence)
        gui.GUI.activeGUI.draw(gui.screen)

        pyg.display.flip()