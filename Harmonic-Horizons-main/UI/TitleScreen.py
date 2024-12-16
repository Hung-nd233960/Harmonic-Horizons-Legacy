import pygame
import sys, os
import time, math, random

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from resources.UIElements import Button, Background, Stars
from Settings.settings import SettingsManager
from Settings.SoundManager import SoundManager
from resources.tools import load_frames_from_spritesheet, BackgroundArtifacts
from resources.environment import MusicStaff, generate_bird_positions
# Constants

BUTTON_WIDTH = 350
BUTTON_HEIGHT = 85
BUTTON_MARGIN = 25
BORDER_RADIUS = 50  # Radius for rounded corners

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Ship(pygame.sprite.Sprite):
    def __init__(self,center_x, center_y, image_path, frame_count):
        super().__init__()
        self.current_frame = 0
        self.frame_delay = 50 / 1000
        self.frames, frame_width, frame_height = load_frames_from_spritesheet(image_path, frame_count, 1)
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.center = (center_x, center_y)
        self.accumulated_time = 0
    def update(self, dt):
        self.accumulated_time += dt  # Accumulate the delta time
        # If accumulated time exceeds the threshold, shift to the next frame
        if self.accumulated_time >= self.frame_delay:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.accumulated_time = 0  # Reset accumulated time after switching frame

class Stars(pygame.sprite.Sprite):
    def __init__(self, x, y, move_direction, radius=1):
        super().__init__()
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)  # Surface with transparency
        self.image.fill((0, 0, 0, 0))  # Transparent fill
        pygame.draw.circle(self.image, (255, 255, 255), (radius, radius), radius)  # Draw a white circle (star)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)  # Position the star at the specified coordinates
        self.speed = random.randint(1,3)
        self.move_direction = move_direction
        
    def update(self, screen_width, dt):
        self.rect.x += self.move_direction * math.ceil(self.speed * dt)
        
        # Keep stars within bounds (reset to the other side)
        if self.rect.x < 0:
            self.rect.x = screen_width  # Reset to the right side
        elif self.rect.x > screen_width:
            self.rect.x = 0  # Reset to the left side

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y, move_direction, speed, radius=1):
        super().__init__()
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)  # Surface with transparency
        #self.image.fill((0, 0, 0, 0))  # Transparent fill
        #pygame.draw.circle(self.image, (255, 255, 255), (radius, radius), radius)  # Draw a white circle (star)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)  # Position the star at the specified coordinates
        self.speed = speed
        self.move_direction = move_direction

    def update(self, frame,screen_width, dt):
        self.image = frame
        self.rect.x += self.move_direction * math.ceil(self.speed * dt)
        
        # Keep stars within bounds (reset to the other side)
        if self.rect.x < 0:
            self.rect.x = screen_width  # Reset to the right side
        elif self.rect.x > screen_width:
            self.rect.x = 0  # Reset to the left side

class BirdGroup(pygame.sprite.Group):
    def __init__(self, bird_frames, *sprites):
        super().__init__(*sprites)
        self.bird_frames = bird_frames
        self.frame_delay_static = 50 / 1000
        self.frame_delay_collision = 1 / 2000
        self.accumulated_time = 0
        self.frame_delay = self.frame_delay_static
        self.current_frame = 0
        self.image = pygame.Surface((1,1), pygame.SRCALPHA)
    def update(self, screen_width, dt):
        self.accumulated_time += dt
        if self.accumulated_time >= self.frame_delay:
            self.current_frame = (self.current_frame + 1) % 18
            self.accumulated_time = 0
            self.image = self.bird_frames[self.current_frame]
        super().update(self.image, screen_width, dt)

class TitleBackground():
    def __init__(self, screen_width, screen_height, image_path, bird_path):

        self.width = screen_width
        self.height = screen_height  # Half the screen height
        self.background_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.assets, self.frame_width, self.frame_height = load_frames_from_spritesheet(image_path, 5, 1)
        self.base_speed = 50
        
        # Define speeds and offsets
        self.layer_configs = {
            "background": {"asset": self.assets[0], "speed": 0.2, "y_offset": 0},
            "big_clouds": {"asset": self.assets[2], "speed": 0.8, "y_offset": 0},
            "small_cloud": {"asset": self.assets[1], "speed": 0.8, "y_offset": 0},
            "water": {"asset": self.assets[3], "speed": 1, "y_offset": 0},
            #"birds": {"asset": self.assets[4], "speed": 4, "y_offset": 0},
        }
        
        # Create artifacts for each layer
        self.layers_group = pygame.sprite.Group()
        for layer, config in self.layer_configs.items():
            artifact = BackgroundArtifacts(
                self.frame_width,
                self.frame_height,
                screen_width,
                screen_height,
                config["speed"] * self.base_speed,
                config["y_offset"],
                config["asset"]
            )
            self.layers_group.add(artifact)

        self.bird_path = bird_path
        above_layer = Background(self.width, self.height*10/20, "custom", "none", (0, 14, 107), (47,23,54))
        middle_layer = Background(self.width, self.height*10/20, "custom", "none", (72, 178, 184), (21, 41, 176))
        gradient1_layer = Background(self.width, self.height/10, "custom", "none", (21, 41, 176),  (139, 59, 219))
        gradient2_layer = Background(self.width, self.height*4/10, "custom", "none", (139, 59, 219),  (47,23,54))
        self.image.blit(above_layer.image, (0,0))
        self.image.blit(middle_layer.image, (0,self.height*10/20))
        self.image.blit(gradient1_layer.image, (0, self.height*10/20))
        self.image.blit(gradient2_layer.image, (0, self.height*2/20))
        # Load frames from the spritesheet (parallax layers)

        # Pre-render snowflake images
        self.create_birds(50)
        # Re-create snow with optimized snowflakes
        self.stars_group = pygame.sprite.Group()
        self.create_stars(200)
        
    def create_birds(self, num_birds = 100):
        self.bird_frames, bird_width, bird_height = load_frames_from_spritesheet(self.bird_path, 24, 1)
        self.birds_group = BirdGroup(self.bird_frames)
        bird_positions = generate_bird_positions(num_birds, self.width, self.height*5/6)
        for position in bird_positions:
            bird = Bird(round(position[0]), round(position[1]), 1, position[2])
            self.birds_group.add(bird)
    def create_stars(self, num_drops=500):
        for _ in range(num_drops):
            x = random.randint(0, self.width)
            y = random.randint(-self.height, self.height//3)
            speed = random.uniform(500, 550)
            star = Stars(x, y, 1, 2)
            self.stars_group.add(star)

    def update(self, dt):
        self.stars_group.update(self.width, dt)
        self.birds_group.update(self.width, dt)
        self.layers_group.update(dt)

    def draw(self, surface, y_pos):

        self.background_surface.blit(self.image, (0, 0))
        for i, artifact in enumerate(self.layers_group):
            artifact.draw(self.background_surface)
            if i == 0:
                self.stars_group.draw(self.background_surface)
            elif i == 1:
                for bird in self.birds_group:
                    self.background_surface.blit(bird.image, bird.rect)
        surface.blit(self.background_surface, (0, y_pos))

class TitleScreen:
    def __init__(self,setting, screen):
        self.setting = setting
        self.screen = screen
          # Larger font for the title
        self.title_text = "HARMONIC HORIZONS"  # Game title
        self.sound_manager = SoundManager()
        self.sound_manager.set_music_volume(self.setting.music_volume) 
        self.sound_manager.set_sfx_volume(self.setting.sfx_volume)
        self.choosen_state = ""
        self.loading_assets()
        self.background_init()
        self.set_fonts()

        self.title_surface_list, title_width, title_height = load_frames_from_spritesheet(self.title_path, 3, 1)
        self.title_surface = pygame.Surface((title_width, title_height), pygame.SRCALPHA)
        self.title_surface.blit(self.title_surface_list[2])
        self.title_width = title_width
        self.title_height = title_height
        self.right_hand_up_flag = False  # Second debounce layer for right hand up
        self.right_hand_down_flag = False  # Second debounce layer for right hand down
        self.left_hand_up_flag = False  # Second debounce layer for left hand up
        self.left_hand_down_flag = False  # Second debounce layer for left hand down

        self.start_time = time.time()
        self.last_update_time = time.time()
        self.last_frame_time = 0
        self.ship1 = Ship(self.setting.screen_width*5//6, self.setting.screen_height*3//5, self.ship1_path, 11)
        self.ship2 = Ship(self.setting.screen_width//6, self.setting.screen_height*3//5, self.ship2_path, 18)
        # Button setup
        start_x = self.setting.screen_width // 2 - BUTTON_WIDTH // 2 
        start_y = self.setting.screen_height // 2 - (3 * BUTTON_HEIGHT + 2 * BUTTON_MARGIN) // 2 + 100
        self.buttons = [
            Button(start_x, start_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Play", BORDER_RADIUS),
            Button(start_x, start_y + BUTTON_HEIGHT + BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT, "Settings", BORDER_RADIUS),
            Button(start_x, start_y + 2 * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT, "Quit Game", BORDER_RADIUS)
        ]
        
        
        self.selected_index = 0
        self.update_hover_states()

    
        
    def loading_assets(self):

        script_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(script_dir, "..", "assets")  # Path to the assets directory
        tracks_dir = os.path.join(assets_dir, "tracks")  # Path to the assets directory
        fonts_dir = os.path.join(assets_dir, "fonts")
        self.clef_path = os.path.join(assets_dir, "sol_clef.png")
        self.title_path = os.path.join(assets_dir, "bigger logo.png")
        self.background_path = os.path.join(assets_dir, "sea sky.png")
        self.bird_path = os.path.join(assets_dir, "bird.png")
        self.ship1_path = os.path.join(assets_dir, "noel boat large.png")
        self.ship2_path = os.path.join(assets_dir, "balloon large.png")
        self.font_path = os.path.join(fonts_dir, "DynaPuff-Regular.ttf")

    def set_fonts(self):
        self.font = pygame.font.Font(self.font_path, 42)

    def background_init(self):
        wave_params = [
        {"amplitude": 50, "frequency": 0.001, "speed": 1.2, "offset": -math.pi / 2, "y_offset": self.setting.screen_height * 0.15 + 75 * i}
        for i in range(5)]
        separator_positions = [20, self.setting.screen_width - 100]
        self.music_staff = MusicStaff(self.setting.screen_width, self.setting.screen_height, wave_params, self.clef_path, separator_positions)
        self.background = TitleBackground(self.setting.screen_width, self.setting.screen_height, self.background_path, self.bird_path)

    def apply_settings(self):
        pass

    def on_enter(self):
        self.start_time = time.time()
        """Optional initialization logic when entering the scene."""

    def update_hover_states(self):
        """Update which button is hovered based on the selected index."""
        for i, button in enumerate(self.buttons):
            button.is_hovered = (i == self.selected_index)

    def handle_events(self, event, detection_results, lock):
        def disengage():
            detection_results['clapped'] = False
            detection_results["right_hand_up"] = False
            detection_results["left_hand_up"] = False
            detection_results["right_hand_down"] = False
            detection_results["left_hand_down"] = False
            detection_results["cross_arm"] = False
        """Handle input events."""
        current_time = time.time()

        # Check if 0.5 seconds have passed since the last update
        if current_time - self.last_update_time >= 0.2:
            # Debounce layer: Right hand up
            if detection_results["right_hand_up"]:
                if not self.right_hand_up_flag:
                    self.right_hand_up_flag = True
                    self.selected_index = (self.selected_index - 1) % len(self.buttons)
                    self.update_hover_states()
            else:
                self.right_hand_up_flag = False  # Reset the flag when signal is False

            # Debounce layer: Right hand down
            if detection_results["right_hand_down"]:
                if not self.right_hand_down_flag:
                    self.right_hand_down_flag = True
                    self.selected_index = (self.selected_index + 1) % len(self.buttons)
                    self.update_hover_states()
            else:
                self.right_hand_down_flag = False  # Reset the flag when signal is False

            # Debounce layer: Left hand up
            if detection_results["left_hand_up"]:
                if not self.left_hand_up_flag:
                    self.left_hand_up_flag = True
                    self.selected_index = (self.selected_index - 1) % len(self.buttons)
                    self.update_hover_states()
            else:
                self.left_hand_up_flag = False  # Reset the flag when signal is False

            # Debounce layer: Left hand down
            if detection_results["left_hand_down"]:
                if not self.left_hand_down_flag:
                    self.left_hand_down_flag = True
                    self.selected_index = (self.selected_index + 1) % len(self.buttons)
                    self.update_hover_states()
            else:
                self.left_hand_down_flag = False  # Reset the flag when signal is False

            if detection_results["clapped"]:
                if self.selected_index == 0:
                    print("Starting game...") # Placeholder for starting the game
                    return "level_chooser"
                elif self.selected_index == 1:
                    print("Opening settings...")  # Placeholder for settings
                    return "settings"
                elif self.selected_index == 2:
                    detection_results["ended"] = True
                    pygame.quit()
            self.last_update_time = current_time

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.buttons)
                self.update_hover_states()

            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.buttons)
                self.update_hover_states()

            elif event.key == pygame.K_SPACE:
                if self.selected_index == 0:
                    print("Starting game...") # Placeholder for starting the game
                    return "level_chooser"
                elif self.selected_index == 1:
                    print("Opening settings...")  # Placeholder for settings
                    return "settings"
                elif self.selected_index == 2:
                    detection_results["ended"] = True
                    pygame.quit()
             
    def update(self):
        current_time = time.time() - self.start_time
        dt = current_time - self.last_frame_time
        for button in self.buttons:
            button.update(dt)
        self.background.update(dt)
        self.ship1.update(dt)
        self.ship2.update(dt)
        self.music_staff.update(dt)
        self.last_frame_time = current_time

    def draw(self):
        """Draw the title screen."""
        self.screen.fill("white")
        self.background.draw(self.screen, 0)
        
        self.music_staff.draw(self.screen)
        self.screen.blit(self.ship1.image, self.ship1.rect)
        self.screen.blit(self.ship2.image, self.ship2.rect)
        self.screen.blit(self.title_surface, (self.setting.screen_width/2 - self.title_width/2, self.setting.screen_height/4 - self.title_height/2))
        for button in self.buttons:
            button.draw(self.screen, self.font)
        


    def on_out(self):
        pass

if __name__ == "__main__":
    detection_result = {
            "right_hand_up": False,
            "left_hand_up": False,
            "right_hand_down": False,
            "left_hand_down": False,
            "clapped": False,
            "cross_arm": False,
            "ended": False
        }
    # Initialize Pygame
    pygame.init()
    setting = SettingsManager()
    screen = pygame.display.set_mode((setting.screen_width, setting.screen_height))
    pygame.display.set_caption("Title Screen")

    # Initialize the title screen
    title_screen = TitleScreen(setting, screen)
    clock = pygame.time.Clock()
    running = True
    lock = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            title_screen.handle_events(event, detection_result, lock)
        title_screen.update()
        title_screen.draw()
        pygame.display.flip()
        clock.tick(setting.fps)

    pygame.quit()
    sys.exit()