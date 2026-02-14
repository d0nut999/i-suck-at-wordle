# Wordle Screenshot Solver

Simple script that automates playing Wordle by reading the board from screen captures and suggesting/typing guesses.

## Requirements
- Install Python dependencies:

```bash
pip install -r requirements.txt
```

Note: `easyocr` often requires `torch` (CPU or GPU build). See EasyOCR docs if installation fails.

## How to Use
1. Open the Wordle website in your browser and set the theme to dark.
2. In your terminal, run:

```bash
python main.py
```

3. **Important:** As soon as you run the script, go to the Wordle webpage and click anywhere on the screen. This gives focus to the browser window so the script can type the words.
4. The script will then automatically take screenshots, run OCR on the tiles, and type guesses.

## Documentation
I documented the entire process in a YouTube video:

**https://youtu.be/aBI6rF-dQSA**

## Important Notes / Configuration
- Supports both the New York Times Wordle and the unlimited Wordle, but you must adjust the RGB color checks in `main.py` when switching variants because their tile colors differ.
- If your screen resolution is not 1920x1080 (the values I used), update the coordinate variables in `main.py` (`begin_x`, `finish_x`, `begin_y`, `finish_y`, and `step`) so the screenshot bbox matches your browser window and tile layout.
- The script assumes the website theme is dark; tile RGB comparisons are written for a dark theme. If your theme is light, change the RGB values used for comparison.
- The script may continue running even after the correct word is entered — I still need to fine-tune and fix some bugs to prevent that. Treat this as a known issue.
- The word list used (fetched from the URL in `main.py`) sometimes contains words that the OCR or the game does not accept; the script is designed to skip those and pick another word automatically, but be aware this behavior exists.
 
## Example RGB values
Below are example RGB tuples (R, G, B) observed for dark-theme Wordle variants. Use these as starting points and update the comparisons inside `main.py` where tile colors are checked.

- New York Times (real) Wordle (dark theme):
	- Correct (green): (83, 141, 78)
	- Wrong place (yellow): (181, 159, 59)
	- Wrong (grey): (58, 58, 60)

- Unlimited / alternate Wordle (dark theme) — values used in this script:
	- Correct (green): (121, 184, 81)
	- Wrong place (yellow): (243, 194, 55)
	- Wrong (grey): (61, 64, 84)

- Other useful pixels checked in `main.py`:
	- "Game over" / all-correct indicator: (38, 40, 58)
	- "Word doesn't exist" indicator used in checks: (25, 26, 36)

Where to change them in `main.py`:
- The color checks for correct / yellow / wrong tiles are in `capture_and_save_screenshot()` (look for the tuples compared to `(r, g, b)`).
- The "word exists" pixel color is checked in `check_if_word_exists()`.
- The game-over color is checked in `did_we_win()`.

If tile colors look slightly off, take a screenshot and inspect the pixel RGB at the center of a tile to get exact values for your setup.

## Troubleshooting
- OCR errors: try increasing the upscaling/thresholding parameters in `main.py` or run on a machine with a GPU and install the GPU build of `torch` for better `easyocr` performance.
- If screenshots are off, adjust the `begin_*` / `finish_*` coordinates and `step` until the captured tiles align with the visible Wordle grid.

## Screen coordinates
- The script assumes a 1920x1080 screen and the following top-level variables in `main.py` near the top: `begin_x`, `finish_x`, `begin_y`, `finish_y`, and `step`.
- If your screen size or browser zoom differs, update those variables so the screenshot bounding box matches your Wordle grid.

## Files
- `main.py` — main automation script
- `requirements.txt` — detected third-party libraries
