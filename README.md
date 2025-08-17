# Kanji-Writing-Practice
An Anki add-on that uses Pygame to practice writing Japanese Kanji

# How to use?
Upon opening a deck for the first time, Kanji Writing Practice will ask if you would like to enable/disable it for that deck.

If enabled, once a card is revealed, the window where you write kanji will appear.

If a kanji character is found in the current card, you can begin drawing in the grid. 

If multiple kanji characters are present, you will draw them one after the other.

After submitting a kanji, your accuracy will be graded, and you have the option of retrying.

**Once you're done drawing and submit all the kanji, proceed using Anki as usual**

# Button Information

There are three buttons:
- Undo
- Hint
- Submit

Notably:
- The **hint button** shows the stroke order and balance of the current kanji.
- The **submit button** grades the stroke order and balance of every stroke drawn, and compiles it into a final percent (%) grade. The individual grade of every stroke is indicated on a **red-yellow-green** gradient. (red - lowest, green - highest)
- If the **stroke order is incorrect**, or **a stroke is completely wrong**, it will be colored **blue**, which represents a 0%.
- **Drawing more/less strokes** than required will **lower your score**.

Once you have a score for a specific kanji, it will be saved in the config. The next time you practice writing that kanji, the old score will appear after submitting.

# Config
In the config, settings for hint animation speed, kanji scores, and blacklisted/whitelisted decks are provided.

Hint animation speed ranges from 15-100. Higher animation speeds can result in certain kanji hints getting slightly distorted. This is due to limitations with Pygame.

# Supported Kanji
**This addon supports roughly 6500 different kanji characters**.

If the card has any of the following:
- No kanji characters
- Kanji characters that aren't supported
- Specific Chinese characters

Kanji Writing Practice will show a red X, and drawing will be disabled. Feel free to close the Pygame window if this happens.

If you run into a kanji that isn't supported by this addon, feel free to report it on github issue tracker. I cannot guarantee all kanji characters will receive support

# Acknowledgements
Data for kanji retrieved from KanjiVG.

(KanjiVG-r20250422-main)

https://kanjivg.tagaini.net

Special thanks to: 
- userrnameee0 for helping debug and showing me the basics of svg files. Also showed me how to implement hint animations into the add-on.
- dae and Shigeyuki for helping me debug a problem I was having on the Anki development forums.

# Important Note
This addon uses the Pygame library on a background thread. It may crash Anki/result in abnormal behavior. I have only tested this addon on version 25.02.1 of Anki on Windows. **I cannot guarantee it will work perfectly on older versions or other operating systems, such as Mac or Linux.**
