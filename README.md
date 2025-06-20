# Kanji-Writing-Practice
An Anki add-on that uses Pygame to practice writing Japanese Kanji

# How to use?
Upon opening a deck for the first time, Kanji Writing Practice will ask if you would like to enable/disable it for that deck.

If enabled, once a card is revealed, the Pygame window where you write kanji will appear.

If a kanji character is found in the current card, you can begin drawing in the grid. 

If multiple kanji characters are present, you will draw them one after the other.

**Buttons**

There are three buttons:
- Undo
- Hint
- Submit

Notably:
- The hint button shows the stroke order and balance of the current kanji
- The submit button grades the stroke order and balance of every stroke drawn, and compiles it into a final percent (%) grade. The individual grade of every stroke is indicated on a red-yellow-green gradient. (red - lowest, green - highest)
- If the stroke order is incorrect, or a stroke is completely wrong, it will be colored blue, which represents a 0%
- Drawing more/less strokes than required will lower your score

Once you have a score for a specific kanji, it will be saved in the config. The next time you practice writing that kanji, the old score will appear after submitting.

# Config
In the config, settings for hint animation speed, kanji scores, and blacklisted/whitelisted decks are provided.

Hint animation speed ranges from 15-100. Note that higher animation speeds can result in certain kanji getting slightly distorted, while slower animation speeds might lag the program at fullscreen. This is due to limitations with Pygame.

# Kanji
This addon supports roughly 6500 different kanji characters. If it tries rendering a kanji it doesn't recognize or certain Chinese characters, the addon will crash.

# Acknowledgements
Data for kanji retrieved from KanjiVG.

(KanjiVG-r20250422-main)

https://kanjivg.tagaini.net

Special thanks to: 
- userrnameee0 for helping debug and showing me the basics of svg files. Also showed me how to implement hint animations into the add-on.
- dae and Shigeyuki for helping me debug a problem I was having on the Anki development forums.
