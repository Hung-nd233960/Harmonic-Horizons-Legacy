import pygame
import time, sys, os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from resources.UIElements import Button, Background
from Settings.settings import SettingsManager
from Settings.SoundManager import SoundManager
# Constants

BUTTON_WIDTH = 350
BUTTON_HEIGHT = 85
BUTTON_MARGIN = 25
BORDER_RADIUS = 80  # Radius for rounded corners

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class PauseScreen:
    def __init__(self, setting, screen):
        self.screen = screen
        self.setting = setting
          # Larger font for the title
        self.title_text = "why stop dreaming?"  # Game title
        # Button setup
        self.sound_manager = SoundManager()
        self.sound_manager.set_music_volume(self.setting.music_volume) 
        self.sound_manager.set_sfx_volume(self.setting.sfx_volume)
        self.loading_assets()
        self.set_fonts()
        self.last_frame_time = 0
        start_x = self.setting.screen_width // 2 - BUTTON_WIDTH // 2 
        start_y = self.setting.screen_height // 2 - (3 * BUTTON_HEIGHT + 2 * BUTTON_MARGIN) // 2 + 100
        self.right_hand_up_flag = False  # Second debounce layer for right hand up
        self.right_hand_down_flag = False  # Second debounce layer for right hand down
        self.left_hand_up_flag = False  # Second debounce layer for left hand up
        self.left_hand_down_flag = False  # Second debounce layer for left hand down
        self.buttons = [
            Button(start_x, start_y, BUTTON_WIDTH, BUTTON_HEIGHT, "continue ", BORDER_RADIUS),
            Button(start_x, start_y + BUTTON_HEIGHT + BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT, "play again", BORDER_RADIUS),
            Button(start_x, start_y + 2*(BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT, "other level", BORDER_RADIUS),
            Button(start_x, start_y + 3*(BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT, "return to title", BORDER_RADIUS)
        ]
        self.background_dark = Background(self.setting.screen_width, self.setting.screen_height, "night")
        self.last_update_time = time.time()
        self.start_time = time.time()
        self.selected_index = 0
        self.update_hover_states()

    def loading_assets(self):

        script_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(script_dir, "..", "assets")  # Path to the assets directory
        tracks_dir = os.path.join(assets_dir, "tracks")  # Path to the assets directory
        fonts_dir = os.path.join(assets_dir, "fonts")
        self.bold_font_path = os.path.join(fonts_dir, "DynaPuff-Bold.ttf")
        self.regular_font_path = os.path.join(fonts_dir, "DynaPuff-Regular.ttf")

    def set_fonts(self):
        self.font = pygame.font.Font(self.regular_font_path, 42)
        self.title_font = pygame.font.Font(self.bold_font_path, 100)

    def apply_settings(self):
        pass
    def update_hover_states(self):
        """Update which button is hovered based on the selected index."""
        for i, button in enumerate(self.buttons):
            button.is_hovered = (i == self.selected_index)
    def on_enter(self):
        pass
    def handle_events(self, event, detection_results, lock):
        current_time = time.time()
        def disengage():
            detection_results['clapped'] = False
            detection_results["right_hand_up"] = False
            detection_results["left_hand_up"] = False
            detection_results["right_hand_down"] = False
            detection_results["left_hand_down"] = False
            detection_results["cross_arm"] = False
        """Handle input events."""

        if current_time - self.last_update_time >= 1:
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
                with lock:
                    disengage()
                if self.selected_index == 0:
                    return "resume"
                elif self.selected_index == 1:
                    print("Restarting...")  # Placeholder for starting the game
                    return 'restart'
                elif self.selected_index == 2:
                    return "level_chooser"
                elif self.selected_index == 3:
                    return "title"
                
            elif detection_results["cross_arm"]:
                with lock:
                    disengage() 
                return "resume"
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
                    return "resume"
                elif self.selected_index == 1:
                    print("Restarting...")  # Placeholder for starting the game
                    return 'restart'
                elif self.selected_index == 2:
                    return "level_chooser"
                elif self.selected_index == 3:
                    return "title"
            elif event.key == pygame.K_ESCAPE:
                    return "resume"
            
                

    def on_out(self):
        pass
    
    def update(self):
        current_time = time.time() - self.start_time
        dt = current_time - self.last_frame_time
        for button in self.buttons:
            button.update(dt)
        self.background_dark.update(dt)
        self.last_frame_time = current_time

    def draw(self):
        """Draw the title screen."""
        self.screen.fill(WHITE)
        self.background_dark.draw(self.screen, 0)
        title_surface = self.title_font.render(self.title_text, True, (238, 186, 255))
        title_rect = title_surface.get_rect(center=(self.setting.screen_width // 2, self.setting.screen_height // 2 - 300))
        self.screen.blit(title_surface, title_rect)
        for button in self.buttons:
            button.draw(self.screen, self.font)


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

    # Initialize the title screen
    end_screen = PauseScreen(setting, screen)

    clock = pygame.time.Clock()
    running = True
    lock = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            end_screen.handle_events(event, detection_result, lock)

        end_screen.update()
        end_screen.draw()
        pygame.display.flip()
        clock.tick(setting.fps)

    pygame.quit()
