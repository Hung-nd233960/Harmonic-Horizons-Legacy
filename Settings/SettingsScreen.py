import pygame, time
import sys, os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from Settings.settings import SettingsManager
from Settings.AssesibilitySettings import AssessibilitySettingsScreen
from Settings.SoundSettings import SoundSettingsScreen
from Settings.ImageSetting import ImageSettingsScreen
from resources.UIElements import Background
from Settings.SoundManager import SoundManager

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT = (0, 255, 0)
BOX_COLOR = (250, 202, 236)
SELECTED_BOX_COLOR = (240, 201, 255)


class SettingsScreen:
    def __init__(self, settings_manager, screen):
        self.settings_manager = settings_manager
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 40)
        
        self.sound_manager = SoundManager()
        self.sound_manager.set_music_volume(self.settings_manager.music_volume) 
        self.sound_manager.set_sfx_volume(self.settings_manager.sfx_volume)
        self.selected_index = 0
        self.last_frame_time = 0
        self.loading_assets()
        self.settings_keys = ["Image Settings", "Sound Settings", "Accessibility Settings", "Back"]
        self.right_hand_up_flag = False  # Second debounce layer for right hand up
        self.right_hand_down_flag = False  # Second debounce layer for right hand down
        self.left_hand_up_flag = False  # Second debounce layer for left hand up
        self.left_hand_down_flag = False  # Second debounce layer for left hand down
        # Store the subscreens within a dictionary
        self.background = Background(self.settings_manager.screen_width, self.settings_manager.screen_height, "night")
        self.subscreens = {
            "accessibility": AssessibilitySettingsScreen(self.sound_manager, settings_manager, screen, self.background),
            "image_settings": ImageSettingsScreen(self.sound_manager, settings_manager, screen, self.background),
            "sound_settings": SoundSettingsScreen(self.sound_manager, settings_manager, screen, self.background ),
        }

        # Active screen starts as the main settings screen
        self.active_screen = None
        self.last_update_time = time.time()
        self.start_time = time.time()
        
    def on_enter(self):
        pass
    def apply_settings(self):
        pass
    def loading_assets(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Current script directory
        assets_dir = os.path.join(script_dir, "..", "assets")  # Path to the assets directory
        tracks_dir = os.path.join(assets_dir, "tracks")
        fonts_dir = os.path.join(assets_dir, "fonts")

        self.title_font_path = os.path.join(fonts_dir, "DynaPuff-Bold.ttf")
        self.title_font = pygame.font.Font(self.title_font_path, 80)

    def draw_rounded_rect(self, surface, color, rect, radius=30):
        pygame.draw.rect(surface, color, rect, border_radius=radius)

    def update(self):
        # Update the current active screen or the main settings screen
        current_time = time.time() - self.start_time
        dt = current_time - self.last_frame_time
        if self.active_screen:
            self.subscreens[self.active_screen].update()
        self.background.update(dt)
        self.last_frame_time = current_time

    def draw(self):
        if self.active_screen:
            self.subscreens[self.active_screen].draw()
        else:
            # Draw the main settings menu
            self.screen.fill(WHITE)
            self.background.draw(self.screen, 0)
            self._draw_title()
            self._draw_menu_options()

    def _draw_title(self):
        title_text = "Settings"
        title_surface = self.title_font.render(title_text, True, (238, 186, 255))
        title_width = title_surface.get_width()
        title_height = title_surface.get_height()
        title_rect_x = (self.screen.get_width() - title_width) // 2
        title_rect_y = self.screen.get_height() // 12
        self.screen.blit(title_surface, (title_rect_x, title_rect_y))

    def _draw_menu_options(self):
        y_pos = self.screen.get_height() // 4
        box_height = self.screen.get_height() // 14
        box_width = self.screen.get_width() // 2
        for i, setting in enumerate(self.settings_keys):
            text_surface = self.font.render(setting, True, BLACK)
            text_width = text_surface.get_width()
            x_pos = self.screen.get_width() // 2 - box_width // 2
            box_color = SELECTED_BOX_COLOR if i == self.selected_index else BOX_COLOR
            self.draw_rounded_rect(self.screen, box_color, (x_pos, y_pos, box_width, box_height))
            self.screen.blit(text_surface, (x_pos + (box_width - text_width) // 2, y_pos + 10))
            y_pos += box_height + 30

    def handle_events(self, event, detection_results, lock):
        current_time = time.time()
        if self.active_screen:
            # Redirect event to the active subscreen
            result = self.subscreens[self.active_screen].handle_event(event, detection_results, lock)
            if result == "settings":
                self.active_screen = None  # Return to the main settings screen
        else:
            def disengage():
                detection_results['clapped'] = False
                detection_results["right_hand_up"] = False
                detection_results["left_hand_up"] = False
                detection_results["right_hand_down"] = False
                detection_results["left_hand_down"] = False
                detection_results["cross_arm"] = False
            # Handle events in the main settings menu
            current_time = time.time()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.settings_keys)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.settings_keys)
                elif event.key == pygame.K_SPACE:
                    setting = self.settings_keys[self.selected_index]
                    if setting == "Image Settings":
                        self.active_screen = "image_settings"
                    elif setting == "Sound Settings":
                        self.active_screen = "sound_settings"
                    elif setting == "Accessibility Settings":
                        self.active_screen = "accessibility"
                    elif setting == "Back":
                        if self.settings_manager.check_changes():
                            self.settings_manager.save_settings()
                            self.settings_manager.changes_needed = True
                        return "title"
            else:
                if current_time - self.last_frame_time >= 1:
                    
                    if detection_results["right_hand_up"]:
                        if not self.right_hand_up_flag:
                            self.right_hand_up_flag = True
                            self.selected_index = (self.selected_index - 1) % len(self.settings_keys)
                        else:
                            self.right_hand_up_flag = False
                    if detection_results["left_hand_up"]:
                        if not self.left_hand_up_flag:
                            self.left_hand_up_flag = True
                            self.selected_index = (self.selected_index - 1) % len(self.settings_keys)
                        else:
                            self.left_hand_up_flag = False
                    if detection_results["left_hand_down"]:
                        if not self.left_hand_down_flag:
                            self.left_hand_down_flag = True
                            self.selected_index = (self.selected_index + 1) % len(self.settings_keys)
                        else:
                            self.left_hand_down_flag = False
                    if detection_results["right_hand_down"]:
                        if not self.right_hand_down_flag:
                            self.right_hand_down_flag = True
                            self.selected_index = (self.selected_index + 1) % len(self.settings_keys)
                        else:
                            self.right_hand_down_flag = False
                            
                    if detection_results["clapped"]:
                        setting = self.settings_keys[self.selected_index]
                        if setting == "Image Settings":
                            self.active_screen = "image_settings"
                        elif setting == "Sound Settings":
                            self.active_screen = "sound_settings"
                        elif setting == "Accessibility Settings":
                            self.active_screen = "accessibility"
                        elif setting == "Back":
                            if self.settings_manager.check_changes():
                                self.settings_manager.save_settings()
                                self.settings_manager.changes_needed = True
                            return "title"


# Main loop
if __name__ == "__main__":
    detection_results = {
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
    
    # Initialize SettingsManager (mock object if needed)
    
    settings_manager = SettingsManager()
    
    # Set up the screen
    screen = pygame.display.set_mode(
        (settings_manager.screen_width, settings_manager.screen_height),
        pygame.FULLSCREEN if settings_manager.full_screen else 0
    )
    pygame.display.set_caption("Settings Test")
    
    # Create the SettingsScreen
    settings_screen = SettingsScreen(settings_manager, screen)
    
    clock = pygame.time.Clock()
    running = True
    lock = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            result = settings_screen.handle_events(event, detection_results, lock)
            if result == "title":
                print("Returning to title screen...")
                running = False
        
        # Update and render
        settings_screen.update()
        settings_screen.draw()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()
