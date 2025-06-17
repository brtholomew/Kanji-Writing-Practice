# Kanji-Writing-Practice
An Anki add-on that uses Pygame to practice writing Japanese Kanji

# How to use?
Upon opening a deck and revealing a card, the Pygame window where you write kanji will appear.

If a kanji character is found in the current card, you can begin drawing in the grid. 

If multiple kanji characters are present, they will be drawn one after the other.

# Buttons
There are three buttons:
- Undo
- Hint
- Submit

Notably:
- The hint button shows the stroke order and balance of the current kanji
- Some kanji do NOT have a hint animation. This is indicated by the hint button being crossed out by a red X. The program will function as intended, but you cannot view a hint for that kanji.


- The submit button grades the stroke order and balance of every stroke drawn, and compiles it into a final percent (%) grade. The individual grade of every stroke is indicated on a red-yellow-green gradient. (red - lowest, green - highest)
- If the stroke order is incorrect, or a stroke is completely wrong, it will be colored blue, which represents a 0%

# Acknowledgements
Data for kanji retrieved from KanjiVG

https://kanjivg.tagaini.net

Special thanks to: 
- userrnameee0 for helping debug and showing me the basics of svg files. Also showed me how to implement hint animations into the add-on
- dae and Shigeyuki for helping me debug a problem I was having on the Anki development forums
