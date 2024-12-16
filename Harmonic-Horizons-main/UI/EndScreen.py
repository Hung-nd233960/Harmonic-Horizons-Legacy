import pygame
import time
import json
import os, sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from resources.UIElements import Button, Background
from Settings.settings import SettingsManager
from Settings.SoundManager import SoundManager
# Constants

BUTTON_WIDTH = 350
BUTTON_HEIGHT = 80
BUTTON_MARGIN = 25
BORDER_RADIUS = 30  # Radius for rounded corners

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)



def read_latest_level_data(filename="level_score.json"):
    try:
        # Open and read the JSON file
        with open(filename, "r") as file:
            data = json.load(file)

        # Check for the latest level
        latest_level = data.get("latest_level")
        if not latest_level:
            return None, "Error: No latest level found in the file."

        # Get the data for the latest level
        level_data = data.get(latest_level)
        if not level_data:
            return None, f"Error: No data found for level '{latest_level}'."

        # Extract and return relevant details
        latest_attempt = level_data.get("Latest Attempt", {})
        high_score = level_data.get("High Score", {})

        return {
            "latest_level": latest_level,
            "latest_attempt": {
                "is_first_star": latest_attempt.get("is_first_star", False),
                "is_second_star": latest_attempt.get("is_second_star", False),
                "is_third_star": latest_attempt.get("is_third_star", False),
                "score": latest_attempt.get("score", 0),
                "missed": latest_attempt.get("missed", 0),
                "perfect": latest_attempt.get("perfect", 0),
            },
            "high_score": {
                "score": high_score.get("score", 0)
            }
        }

    except FileNotFoundError:
        return None, "Error: File not found."
    except json.JSONDecodeError:
        return None, "Error: JSON file is corrupted."


class EndScreen:
    def __init__(self,setting, screen, is_first_star = False, is_second_star = False, is_third_star = False ):
        self.screen = screen
        self.setting = setting
        self.sound_manager = SoundManager()
        self.sound_manager.set_music_volume(self.setting.music_volume) 
        self.sound_manager.set_sfx_volume(self.setting.sfx_volume)

        
        self.title_text = "All Done!"  # Game title
        self.last_update_time = time.time()
        
        self.right_hand_down_flag = False
        self.left_hand_up_flag = False
        self.right_hand_up_flag = False
        self.left_hand_down_flag = False
        self.first_star_check = False
        self.second_star_check = False
        self.third_star_check = False
        self.perfect = 0
        self.misses = 0
        self.score_updated = False
        self.last_frame_time = 0
        self.start_time = time.time()
        self.last_update_time = time.time()
        self.loading_assets()
        self.set_fonts()
        # Button setup
        start_x = self.setting.screen_width // 2 - BUTTON_WIDTH // 2 
        start_y = self.setting.screen_height // 2 - (3 * BUTTON_HEIGHT + 2 * BUTTON_MARGIN) // 2 + 200

        self.buttons = [
            Button(start_x, start_y, BUTTON_WIDTH, BUTTON_HEIGHT, "sleep again", BORDER_RADIUS),
            Button(start_x, start_y + BUTTON_HEIGHT + BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT, "other dreams", BORDER_RADIUS),
            Button(start_x, start_y + 2*(BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT, "wake up", BORDER_RADIUS),
        ]
        self.background_dark = Background(self.setting.screen_width, self.setting.screen_height, "night")
        self.selected_index = 0
        self.update_hover_states()
    def apply_settings(self):
        pass
    def loading_assets(self):

        script_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(script_dir, "..", "assets")  # Path to the assets directory
        tracks_dir = os.path.join(assets_dir, "tracks")  # Path to the assets directory
        fonts_dir = os.path.join(assets_dir, "fonts")
        self.bold_font_path = os.path.join(fonts_dir, "DynaPuff-Bold.ttf")
        self.regular_font_path = os.path.join(fonts_dir, "DynaPuff-Regular.ttf")

    def set_fonts(self):

        self.font = pygame.font.Font(self.regular_font_path, 39)
        self.title_font = pygame.font.Font(self.bold_font_path, 100)  # Larger font for the title
        self.game_over_font = pygame.font.Font(self.regular_font_path, 48)
        self.game_over_state_font = pygame.font.Font(self.regular_font_path, 32)
        self.game_over_message_font = pygame.font.Font(self.regular_font_path, 33)
        
    def update_hover_states(self):
        """Update which button is hovered based on the selected index."""
        for i, button in enumerate(self.buttons):
            button.is_hovered = (i == self.selected_index)
    def on_enter(self):
        self.start_time = time.time()
        print("")
        result = read_latest_level_data()
        if result:
            self.latest_level = result["latest_level"]
            self.first_star_check = result["latest_attempt"]["is_first_star"]
            self.second_star_check = result["latest_attempt"]["is_second_star"]
            self.third_star_check = result["latest_attempt"]["is_third_star"]
            self.score = result["latest_attempt"]["score"]
            self.misses = result["latest_attempt"]["missed"]
            self.perfect = result["latest_attempt"]["perfect"]
            self.high_score = result["high_score"]["score"]
        else:
            # Handle error message
            print("Error")
            self.latest_level = None
            self.first_star_check = False
            self.second_star_check = False
            self.third_star_check = False
            self.latest_score = 0
            self.latest_missed = 0
            self.latest_perfect = 0
            self.high_score = 0
        self.score_updated = True
        
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
                disengage()
                if self.selected_index == 0:
                    print("Starting game...") # Placeholder for starting the game
                    return "restart"
                elif self.selected_index == 1:

                    return "level_chooser"  # Placeholder for settings
                elif self.selected_index == 2:
                    return "title"
                self.score_updated = False
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
                    print("Restarting...")  # Placeholder for starting the game
                    return 'restart'
                elif self.selected_index == 1:
                    return "level_chooser"
                elif self.selected_index == 2:
                    return "title"
                self.score_updated = False
    
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
        def draw_game_over(self):
    # Draw the main panel
            panel_x, panel_y, panel_width, panel_height = 710, 150, 500, 780
            pygame.draw.rect(self.screen, (252, 242, 247), (panel_x, panel_y, panel_width, panel_height), 0, 70)
            pygame.draw.rect(self.screen, 'purple', (panel_x, panel_y, panel_width, panel_height), 5, 70)

            # Render and center "All Done!" text
            game_over_text = self.game_over_font.render("All Done!", True, (191, 50, 156))
            game_over_rect = game_over_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 50))
            self.screen.blit(game_over_text, game_over_rect)

            # Draw stars centered horizontally
            # Draw stars centered horizontally
            star_y = panel_y + 125  # Adjusted to align vertically within the panel
            star_radius = 25
            star_gap = 50  # Gap between each star
            num_stars = 3
            total_star_width = (num_stars * 2 * star_radius) + ((num_stars - 1) * star_gap)

            # Calculate starting x-position for centering
            start_x = panel_x + (panel_width - total_star_width) // 2 + 15

            # Generate star positions dynamically
            star_positions = [
                (start_x + i * (2 * star_radius + star_gap), star_y) for i in range(num_stars)
            ]

            # Draw the stars
            star_checks = [self.first_star_check, self.second_star_check, self.third_star_check]
            for pos, checked in zip(star_positions, star_checks):
                if checked:
                    pygame.draw.circle(self.screen, (232, 70, 113), pos, star_radius)
                pygame.draw.circle(self.screen, 'purple', pos, star_radius, 1)


            # Draw statistics
            stats_texts = [("Perfect", 'purple', self.perfect), ("Missed", 'orange', self.misses)]
            for i, (label, color, value) in enumerate(stats_texts):
                # Render the labels
                stat_label = self.game_over_state_font.render(label, True, color)
                stat_label_rect = stat_label.get_rect(center=(panel_x + 150, 350 + i * 50))
                self.screen.blit(stat_label, stat_label_rect)

                # Render the values
                stat_value = self.game_over_state_font.render(str(value), True, color)
                stat_value_rect = stat_value.get_rect(center=(panel_x + panel_width - 150, 350 + i * 50))
                self.screen.blit(stat_value, stat_value_rect)

            # Render and center "Nice Try!" message
            nice_try_text = self.game_over_message_font.render("Nice Try!", True, (232, 70, 113))
            nice_try_rect = nice_try_text.get_rect(center=(panel_x + panel_width // 2, 460))
            self.screen.blit(nice_try_text, nice_try_rect)


        self.screen.fill(WHITE)
        self.background_dark.draw(self.screen, 0)
        if self.score_updated:
            draw_game_over(self)
            for button in self.buttons:
                button.draw(self.screen, self.font)
        


if __name__ == "__main__":
    # Initialize Pygame
    pygame.init()
    setting = SettingsManager()
    screen = pygame.display.set_mode((setting.screen_width, setting.screen_height))

    # Initialize the title screen
    end_screen = EndScreen(setting, screen)

    clock = pygame.time.Clock()
    running = True
    detection_results = {
                "detection_of_sensors": False,
                "right_hand_up": False,
                "left_hand_up": False,
                "right_hand_down": False,
                "left_hand_down": False,
                "clapped": False,
                "cross_arm": False,
                "ended": False
            }
    end_screen.on_enter()
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            end_screen.handle_events(event, detection_results, None)

        end_screen.update()
        end_screen.draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
