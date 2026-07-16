import os
import json
import pygame
# WINDOW / GAME CONSTANTS
WIDTH = 1280
HEIGHT = 720
FPS = 60

GRAVITY = 0.35
JUMP_STRENGTH = -7.2

PIPE_SPEED = 4
PIPE_GAP = 280
PIPE_SPAWN_DISTANCE = 400

BIRD_SIZE = (75, 52)
PIPE_SIZE = (120, 600)

GROUND_HEIGHT = 120
CLOUD_LAYER_HEIGHT = 300

# PATHS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CLASSIC_DIR = os.path.join(ASSETS_DIR, "classic")
NEUTRAL_DIR = os.path.join(ASSETS_DIR, "neutral")
UI_DIR = os.path.join(NEUTRAL_DIR, "ui")
FONTS_DIR = os.path.join(NEUTRAL_DIR, "fonts")

HIGH_SCORE_FILE = os.path.join(BASE_DIR, "highscore.json")

UI_FILES = {
    "title_logo": "title_logo.png",
    "btn_restart": "btn_restart.png",
    "btn_menu": "btn_menu.png",
    "btn_keyboard": "btn_keyboard.png",
    "btn_visual": "btn_visual.png",
    "score_panel": "score_panel.png",
    "get_ready_banner": "get_ready_banner.png",
}

FONT_FILE = os.path.join(FONTS_DIR, "PressStart2P-Regular.ttf")


# PLACEHOLDER GENERATION
# (keeps the game runnable even if an asset hasn't been generated yet)
def _placeholder(size, color, label=""):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill(color)
    pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 2)
    if label:
        font = pygame.font.SysFont("Arial", 14)
        text = font.render(label, True, (0, 0, 0))
        surf.blit(text, text.get_rect(center=(size[0] // 2, size[1] // 2)))
    return surf


_PLACEHOLDER_SPECS = {
    "sky": ((WIDTH, HEIGHT), (135, 206, 235)),
    "clouds": ((WIDTH, CLOUD_LAYER_HEIGHT), (255, 255, 255, 0)),
    "ground": ((WIDTH, GROUND_HEIGHT), (150, 111, 51)),
    "pipe": (PIPE_SIZE, (60, 180, 60)),
    "bird_1": (BIRD_SIZE, (230, 200, 40)),
    "bird_2": (BIRD_SIZE, (230, 200, 40)),
    "bird_3": (BIRD_SIZE, (230, 200, 40)),
    "icon": ((150, 150), (200, 200, 200)),
}

_UI_PLACEHOLDER_SPECS = {
    "title_logo": ((600, 200), (250, 200, 50)),
    "btn_restart": ((250, 80), (80, 200, 80)),
    "btn_menu": ((250, 80), (80, 140, 220)),
    "btn_keyboard": ((300, 90), (200, 200, 200)),
    "btn_visual": ((300, 90), (200, 200, 200)),
    "score_panel": ((500, 300), (230, 210, 170)),
    "get_ready_banner": ((500, 150), (255, 255, 255, 0)),
}


def _load_image(path, size, color, label=""):
    """Load an image if it exists, otherwise return a labeled placeholder."""
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            if img.get_size() != size:
                img = pygame.transform.smoothscale(img, size)
            return img
        except pygame.error:
            pass
    return _placeholder(size, color, label)


# ASSET MANAGER
class AssetManager:
    """
    Loads and caches all image/font assets.
    Usage:
        assets = AssetManager()
        assets.load_all()
        logo = assets.ui["title_logo"]
        font = assets.font(24)
    """

    def __init__(self):
        self.sky = None
        self.clouds = None
        self.ground = None
        self.pipe = None
        self.bird_frames = []
        self.icon = None
        self.ui = {}
        self._font_cache = {}

    def load_all(self):
        self._load_classic_assets()
        self.ui = self._load_ui()
        return self

    def _load_classic_assets(self):
        self.sky = _load_image(os.path.join(CLASSIC_DIR, "sky.png"), _PLACEHOLDER_SPECS["sky"][0], _PLACEHOLDER_SPECS["sky"][1], label="classic:sky")
        self.clouds = _load_image(os.path.join(CLASSIC_DIR, "clouds.png"), _PLACEHOLDER_SPECS["clouds"][0], _PLACEHOLDER_SPECS["clouds"][1], label="classic:clouds")
        self.ground = _load_image(os.path.join(CLASSIC_DIR, "ground.png"), _PLACEHOLDER_SPECS["ground"][0], _PLACEHOLDER_SPECS["ground"][1], label="classic:ground")
        self.pipe = _load_image(os.path.join(CLASSIC_DIR, "pipe.png"), _PLACEHOLDER_SPECS["pipe"][0], _PLACEHOLDER_SPECS["pipe"][1], label="classic:pipe")
        self.bird_frames = [
            _load_image(os.path.join(CLASSIC_DIR, "bird_1.png"), _PLACEHOLDER_SPECS["bird_1"][0], _PLACEHOLDER_SPECS["bird_1"][1], label="classic:bird_1"),
            _load_image(os.path.join(CLASSIC_DIR, "bird_2.png"), _PLACEHOLDER_SPECS["bird_2"][0], _PLACEHOLDER_SPECS["bird_2"][1], label="classic:bird_2"),
            _load_image(os.path.join(CLASSIC_DIR, "bird_3.png"), _PLACEHOLDER_SPECS["bird_3"][0], _PLACEHOLDER_SPECS["bird_3"][1], label="classic:bird_3"),
        ]
        self.icon = _load_image(os.path.join(CLASSIC_DIR, "icon.png"), _PLACEHOLDER_SPECS["icon"][0], _PLACEHOLDER_SPECS["icon"][1], label="classic:icon")

    def _load_ui(self):
        loaded = {}
        for key, filename in UI_FILES.items():
            size, color = _UI_PLACEHOLDER_SPECS[key]
            path = os.path.join(UI_DIR, filename)
            loaded[key] = _load_image(path, size, color, label=key)
        return loaded

    def font(self, size):
        if size not in self._font_cache:
            if os.path.exists(FONT_FILE):
                self._font_cache[size] = pygame.font.Font(FONT_FILE, size)
            else:
                self._font_cache[size] = pygame.font.SysFont("Arial", size)
        return self._font_cache[size]


# HIGH SCORE PERSISTENCE
def load_high_scores():
    """Returns the single global best score."""
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, int):
                    return data
        except (json.JSONDecodeError, OSError):
            pass
    return 0


def save_high_scores(score):
    try:
        with open(HIGH_SCORE_FILE, "w") as f:
            json.dump(score, f)
    except OSError:
        pass
