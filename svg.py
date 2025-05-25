# module for handling svgs
import pygame as pyg
from io import BytesIO
import gui

pyg.init()

gui.initDisplay((300, 300))

# -------------------- SVG Functions --------------------

def replaceSubstring(stri: str, newValue: str | float, index: tuple):
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
        raise ValueError(f"Could not find d parameter in: {svg}")
    # start index begins at the first character after the quotation mark, end index is at the quotation mark that closes the d parameter
    startIndex = svg.index('"', startIndex) + 1
    endIndex = svg.index('"', startIndex)
    listSVG = list(svg)
    d = []
    # counter tracks if we're on an x or y coordinate; 0 = x, 1 = y
    counter = 0
    for i in range(startIndex, endIndex):
        # link current command to a list of list of x and y coordinates
        # every x/y coordinate will be represented as a list
        if svg[i].isalpha():
            #d[svg[i]] = []
            currentCommand = svg[i]
            d.append({currentCommand: []})
            # create new x/y coordinate list
            counter = 0
            d[-1][currentCommand].append([])
        elif svg[i] not in (",", "-"):
            try:
                d[-1][currentCommand][-1][counter].append(svg[i])
            except IndexError:
                # missing x/y coordinate list
                d[-1][currentCommand][-1].append([svg[i]])
        else: # svg[i] is either a dash or comma
            # if a x/y coordinate is missing
            if len(d[-1][currentCommand][-1]) < 2:
                # only move to the y coordinate if the x coordinate is there
                counter += 1 if len(d[-1][currentCommand][-1]) == 1 else 0
                # for SOME REASON "-" represents a comma AND a negative number thanks a lot
                d[-1][currentCommand][-1].append(["-"] if svg[i] == "-" else [])
            else: # create new list of x/y coordinates
                counter = 0
                d[-1][currentCommand].append([["-"]] if svg[i] == "-" else [])
    return d


def extractPosition(svg: str, keyword: str, start: int = 0):
    """
    Returns the start and end index of a value associated to a specific keyword in an svg file as a tuple\n
    If endIndex is -1, no value is associated with keyword, and startIndex becomes the starting index of the keyword
    """
    startIndex = svg.index(keyword, start)

    # SURELY THERE'S A BETTER WAY OF DOING THIS???
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
        raise ValueError("SVG file is invalid")
    return (startIndex, endIndex)

def extractValue(svg: str, keyword: str):
    """
    Returns the value associated to a specific keyword in an svg file
    """
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
        # svg = list(svg)
        startIndex, endIndex = extractPosition("".join(svg), keyword)
        # oldValue = []
        # for i in range(startIndex, endIndex):
        #     #del svg[startIndex]
        #     oldValue.append(svg.pop(startIndex))
        # svg.insert(startIndex, str(value))
        # # inserting the value whole without spliting it into individual elements will misallign the index found using extractPosition
        # # instead of using an external library or coding my own solution to this problem, i will write code that looks redundant
        # svg = "".join(svg)
        svg, oldValue = replaceSubstring(svg, value, (startIndex, endIndex))

        if keyword == "width" or keyword == "height":
            # hey why didn't you just use an external library for this?
            # ... extract what's inside of the d parameter
            d = extractPathParameter(svg)
            # reconstruct d parameter while applying the transformations
            #print(d)
            #print(svg)
            temp = ""
            # for every move command
            for i in d:
                for k, v in i.items():
                    temp = f"{temp}{k}"
                    # for every x/y coordinate
                    for q in v:
                        x = float("".join(q[0]))
                        y = float("".join(q[1]))
                        temp = f"{temp}{x*(value/float(oldValue) if keyword == 'width' else 1)},{y*(value/float(oldValue) if keyword == 'height' else 1)},"
                    # pop the last comma off
                    temp = list(temp)
                    del temp[-1]
                    temp = "".join(temp)
            temp = temp.replace(",-", "-")
            startIndex = svg.index('"', svg.index(' d="')) + 1
            endIndex = svg.index('"', startIndex)
            svg = replaceSubstring(svg, temp, (startIndex, endIndex))[0]
            #print(f"extracted d parameter: {temp}")
            
    return svg

# -------------------- Kanji Class --------------------

class Kanji():
    """
    Class for breaking down written kanji into its individual strokes
    """
    def __init__(self, kanji: str, dimensions: gui.point, strokeWidth: float):
        svgList = Kanji.deconstructKanji(kanji)[0]
        self.svgList = []
        for i in svgList:
            self.svgList.append(alterValue(i, width = dimensions[0], height = dimensions[1], **{"stroke-width" : strokeWidth}, viewBox = f"0 0 {dimensions[0]} {dimensions[1]}"))
        #print(self.svgList)
        self.metadata = dict(width = dimensions[0], height = dimensions[1], strokeWidth = strokeWidth)
        
        self.surfList = Kanji.svgTextToSurf(*self.svgList)

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

        metadata = dict(width = extractValue(svgTag, "width"), height = extractValue(svgTag, "height"), strokeWidth = extractValue(brushInfo, "stroke-width"))
        #print(metadata)
        return svgList, metadata

    @staticmethod
    def svgTextToSurf(*args):
        """
        Converts an svg in text format to a pygame surface
        """
        IOList = []
        for i in args:
            # code taken from https://python-forum.io/thread-40976.html
            # i don't really get it but basically it turns a string into bytes, which is then turned into a filelike object, which can be read by pygame's image loader
            IOList.append(pyg.image.load(BytesIO(bytes(i, encoding = "utf-8"))).convert_alpha())
        return IOList if len(IOList) > 1 else IOList[0]
    
    def scale(self, scale: float):
        newSvgList = []
        for i in self.svgList:
            newSvgList.append(alterValue(i, width = self.metadata["width"]*scale, height = self.metadata["height"]*scale, **{"stroke-width": self.metadata["strokeWidth"]*scale}))
        self.surfList = Kanji.svgTextToSurf(*newSvgList)

        # global blitSequence
        # blitSequence = [(surf, (0, 0)) for surf in kanji.surfList]



# temp = []
# for i in Kanji.deconstructKanji("飲")[0]:
#     temp.append(gui.GUI((150, 150), (109, 109), image = Kanji.svgTextToSurf(i)))
#gui.GUI.activate(temp)
# Kanji.alterValue("""<svg xmlns="http://www.w3.org/2000/svg" width="109" height="109" viewBox="0 0 109 109">
# <g id="kvg:StrokePaths_098df" style="fill:none;stroke:#000000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;">
# 	<path id="kvg:098df-s1" kvg:type="㇒" d="M52.75,10.5c0.11,0.98-0.19,2.67-0.97,3.93C45,25.34,31.75,41.19,14,51.5"/>
# </g>
# </svg>""", "width", 300)

kanji = Kanji("食", (175, 175), 8)
blitSequence = [(surf, (0, 0)) for surf in kanji.surfList]
# print("""<svg xmlns="http://www.w3.org/2000/svg" width="300" height="109" viewBox="0 0 109 109">
# <g id="kvg:StrokePaths_098df" style="fill:none;stroke:#000000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;">
#         <path id="kvg:098df-s4" kvg:type="㇕" d="M38,40c0.83,0.47,2.19,1,3.86,0.83c9.39-0.96,21.95-2.76,23.25-2.84c1.67-0.1,3.14,0.88,3.11,2.53C68.2,41.8,67,53.25,66.34,62.4c-0.07,0.94-0.13,1.36-0.13,1.99"/>
# </g>
# </svg>""".index("c-0.07"))
# print(extractPathParameter("""<svg xmlns="http://www.w3.org/2000/svg" width="300" height="109" viewBox="0 0 109 109">
# <g id="kvg:StrokePaths_098df" style="fill:none;stroke:#000000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;">
#         <path id="kvg:098df-s4" kvg:type="㇕" d="M38,40c0.83,0.47,2.19,1,3.86,0.83c9.39-0.96,21.95-2.76,23.25-2.84c1.67-0.1,3.14,0.88,3.11,2.53C68.2,41.8,67,53.25,66.34,62.4c-0.07,0.94-0.13,1.36-0.13,1.99"/>
# </g>
# </svg>"""))

scale = 1
running = True

while running:

    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            running = False
        if event.type == pyg.KEYUP:
            if event.key == pyg.K_a:
                scale -= 0.1
            elif event.key == pyg.K_d:
                scale += 0.1

    kanji.scale(scale)
    gui.screen.fill("white")
    pyg.Surface.blits(gui.screen, blitSequence)
#     pyg.Surface.blit(gui.screen, Kanji.svgTextToSurf("""<svg xmlns="http://www.w3.org/2000/svg" width="109" height="109" viewBox="0 0 109 109">
# <g id="kvg:StrokePaths_098df" style="fill:none;stroke:#000000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;">
# 	<path id="kvg:098df-s1" kvg:type="㇒" d="M52.75,10.5c0.11,0.98-0.19,2.67-0.97,3.93C45,25.34,31.75,41.19,14,51.5"/>
# </g>
# </svg>"""), (87.5, 87.5))
#     pyg.Surface.blit(gui.screen, Kanji.svgTextToSurf("""<svg xmlns="http://www.w3.org/2000/svg" width="329" height="329" viewBox="0 0 327 327">
# <g id="kvg:StrokePaths_098df" style="fill:none;stroke:#000000;stroke-width:9;stroke-linecap:round;stroke-linejoin:round;">
# 	<path id="kvg:098df-s1" kvg:type="㇒" d="M158.25,31.5c0.33,2.94-0.57,8.01-2.91,11.79C135,76.02,95.25,123.57,42,154.5"/>
# </g>
# </svg>"""), (87.5, 87.5))
    gui.GUI.activeGUI.draw(gui.screen)

    pyg.display.flip()