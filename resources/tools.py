import pygame, json
from datetime import datetime

def update_score(level, score, missed, perfect, is_first_star, is_second_star, is_third_star, filename="level_score.json"):
    # Default structure for the JSON file
    data = {
        "latest_level": level
    }

    # Read existing file if it exists
    try:
        with open(filename, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        pass  # No existing file, start with default structure

    # Update the latest level at the top
    data["latest_level"] = level

    # Ensure the current level exists in the data
    if level not in data:
        data[level] = {
            "High Score": {
                "time": None,
                "is_first_star": False,
                "is_second_star": False,
                "is_third_star": False,
                "score": 0,
                "missed": 0,
                "perfect": 0
            },
            "Latest Attempt": {
                "time": None,
                "is_first_star": False,
                "is_second_star": False,
                "is_third_star": False,
                "score": 0,
                "missed": 0,
                "perfect": 0
            }
        }

    # Update Latest Attempt for the current level
    data[level]["Latest Attempt"] = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_first_star": is_first_star,
        "is_second_star": is_second_star,
        "is_third_star": is_third_star,
        "score": score,
        "missed": missed,
        "perfect": perfect
    }

    # Check if the new score is a high score for the current level
    if score > data[level]["High Score"]["score"]:
        data[level]["High Score"] = data[level]["Latest Attempt"].copy()

    # Write updated data back to the file
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def load_frames_from_spritesheet(image_path, columns, rows):
    """
    Extract frames from a spritesheet and return frame dimensions.

    Args:
        image_path (str): Path to the spritesheet image.
        columns (int): Number of columns in the spritesheet.
        rows (int): Number of rows in the spritesheet.

    Returns:
        tuple: (frames, frame_width, frame_height)
            - frames (list): A list of Pygame surfaces, each representing a frame.
            - frame_width (int): Width of a single frame.
            - frame_height (int): Height of a single frame.
    """
    # Ensure Pygame is initialized
    pygame.init()

    # Load the spritesheet image
    spritesheet = pygame.image.load(image_path)

    # If the image has transparency, use convert_alpha() to keep it
    if spritesheet.get_flags() & pygame.SRCALPHA:
        spritesheet = spritesheet.convert_alpha()
    else:
        spritesheet = spritesheet.convert()

    # Get the size of each frame
    sheet_width, sheet_height = spritesheet.get_size()
    frame_width = sheet_width // columns
    frame_height = sheet_height // rows

    # Extract each frame
    frames = []
    for row in range(rows):
        for col in range(columns):
            x = col * frame_width
            y = row * frame_height
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(spritesheet, (0, 0), (x, y, frame_width, frame_height))
            frames.append(frame)

    return frames, frame_width, frame_height


class BackgroundArtifacts(pygame.sprite.Sprite):
    def __init__(self, width, height, screen_width, screen_height, speed, y_offset, asset):
        super().__init__()
        self.width = width
        self.height = height
        self.image = asset
        self.rect = self.image.get_rect()
        self.tiles = screen_width//width + 1
        self.scroll = 0
        self.y_offset = y_offset
        self.speed = speed
    def draw(self, surface):
        for i in range(self.tiles):
            surface.blit(self.image, (i*self.width + self.scroll, self.y_offset))
        
    def update(self, dt):
        self.scroll -= round(self.speed * dt)
        if abs(self.scroll) > self.width:
            self.scroll = 0

class EffectManager:
    def __init__(self, surface, lightning_surface=None):
        self.surface = surface
        self.lightning_surface = lightning_surface
        self.dimming_alpha = 0
        self.lightning_alpha = 0
        self.lightning_decay_rate = 150
        self.dimming_decay_rate = 400
        self.dimming_increase_rate = 900
        self.is_dimming_active = False
        self.is_lightning_active = False

    def trigger_dimming(self, intensity=180):
        self.is_dimming_active = True
        self.dimming_alpha = min(255, intensity)

    def apply_dimming(self, dt):
        if self.dimming_alpha > 0:
            # Create and apply a dimming overlay
            overlay = pygame.Surface(self.surface.get_size())
            overlay.fill((0, 0, 0))  # Black color for dimming
            overlay.set_alpha(int(self.dimming_alpha))
            self.surface.blit(overlay, (0, 0))

            # Gradually fade out the dimming effect
            self.dimming_alpha = max(0, self.dimming_alpha - self.dimming_decay_rate * dt)
            if self.dimming_alpha == 0:
                self.is_dimming_active = False

    def trigger_lightning(self, intensity=180):
        self.is_lightning_active = True
        self.lightning_alpha = intensity

    def apply_lightning(self, dt):
        if self.lightning_alpha > 0:
            if self.lightning_surface:
                lightning_effect = self.lightning_surface.copy()
                lightning_effect.set_alpha(int(self.lightning_alpha))
                self.surface.blit(lightning_effect, (0, 0))
            else:
                flash = pygame.Surface(self.surface.get_size())
                flash.fill((255, 255, 255))
                flash.set_alpha(int(self.lightning_alpha))
                self.surface.blit(flash, (0, 0))

            # Gradually fade the lightning effect
            self.lightning_alpha = max(0, self.lightning_alpha - self.lightning_decay_rate * dt)
            if self.lightning_alpha == 0:
                self.is_lightning_active = False