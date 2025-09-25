import os
import pygame

# Game configuration
WIDTH = 800
HEIGHT = 600
FPS = 60

# Try to load fonts
pygame.font.init()

# Define font paths
font_dir = "assets/fonts"
os.makedirs(font_dir, exist_ok=True)

# Font settings - with fallbacks
try:
    # Try to load custom fonts if available
    GAME_FONT = os.path.join(font_dir, "Roboto-Regular.ttf")
    GAME_FONT_BOLD = os.path.join(font_dir, "Roboto-Bold.ttf")
    GAME_FONT_MONO = os.path.join(font_dir, "RobotoMono-Regular.ttf")
    
    # Test if files exist, otherwise use system fonts
    if not (os.path.exists(GAME_FONT) and os.path.exists(GAME_FONT_BOLD) and os.path.exists(GAME_FONT_MONO)):
        raise FileNotFoundError("Custom fonts not found")
        
except:
    # Fallback to system fonts
    GAME_FONT = None
    GAME_FONT_BOLD = None
    GAME_FONT_MONO = None

# Font sizes
FONT_TINY = 14
FONT_SMALL = 18
FONT_MEDIUM = 24
FONT_LARGE = 36
FONT_XL = 48
FONT_XXL = 64

# Colors with alpha support (RGBA)
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
BLUE = (30, 144, 255, 255)
LIGHT_BLUE = (173, 216, 230, 255)
GREEN = (50, 205, 50, 255)
LIGHT_GREEN = (144, 238, 144, 255)
RED = (220, 20, 60, 255)
LIGHT_RED = (255, 182, 193, 255)
GRAY = (128, 128, 128, 255)
DARK_GRAY = (50, 50, 50, 255)
LIGHT_GRAY = (200, 200, 200, 255)

# UI Colors
HEADER_COLOR = (240, 248, 255, 255)
UI_BG_COLOR = (240, 248, 255, 200)
UI_BORDER_COLOR = (30, 144, 255, 255)

# Difficulty settings
DIFFICULTY_MULTIPLIERS = {
    "easy": 0.8,
    "normal": 1.0,
    "hard": 1.2
}

# Game settings
DEFAULT_DIFFICULTY = "normal"
MAX_LEVELS = 10
LIVES = 5
MAX_BUGS = 5

# Sound settings
SOUND_ENABLED = True
MUSIC_VOLUME = 0.5
SFX_VOLUME = 0.7

# Define asset directories
ASSET_DIR = "assets"
SOUND_DIR = os.path.join(ASSET_DIR, "sounds")
IMAGE_DIR = os.path.join(ASSET_DIR, "images")

# Create directories if they don't exist
for directory in [ASSET_DIR, SOUND_DIR, IMAGE_DIR, font_dir]:
    os.makedirs(directory, exist_ok=True)

# Try to create readme file with font instructions if it doesn't exist
readme_path = os.path.join(font_dir, "README.txt")
if not os.path.exists(readme_path):
    try:
        with open(readme_path, "w") as f:
            f.write("Place the following fonts in this directory:\n")
            f.write("- Roboto-Regular.ttf\n")
            f.write("- Roboto-Bold.ttf\n")
            f.write("- RobotoMono-Regular.ttf\n\n")
            f.write("These fonts can be downloaded from Google Fonts.\n")
    except:
        pass