import pygame, os, sys, time, json
from datetime import datetime
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from resources.UIElements import Background, LevelBlock, Scoreboard
# Constants
from Settings.settings import SettingsManager
from Settings.SoundManager import SoundManager




BUTTON_WIDTH = 350
BUTTON_HEIGHT = 85
BUTTON_MARGIN = 35
BORDER_RADIUS = 80  # Radius for rounded corners

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def process_scores_from_file(file_path):
    try:
        # Load the JSON data from the file
        with open(file_path, 'r') as file:
            scores = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file cannot be found or is not a valid JSON, do nothing and return None
        return None
    
    # Initialize output dictionary
    result = {}
    
    # Loop through each level in the JSON (excluding 'latest_level')
    for level, data in scores.items():
        if level == "latest_level":
            continue
        
        try:
            # Process high score and latest attempt times
            high_score_time = datetime.strptime(data["High Score"]["time"], "%Y-%m-%d %H:%M:%S").date()
            latest_attempt_time = datetime.strptime(data["Latest Attempt"]["time"], "%Y-%m-%d %H:%M:%S").date()
            
            # Add data to result
            result[level] = {
                "High Score": {
                    "date": str(high_score_time),
                    **data["High Score"]
                },
                "Latest Attempt": {
                    "date": str(latest_attempt_time),
                    **data["Latest Attempt"]
                }
            }
            # Remove hours and minutes from the nested dicts
            result[level]["High Score"].pop("time", None)
            result[level]["Latest Attempt"].pop("time", None)
        except (KeyError, ValueError):
            # Skip processing if required keys or time formatting is incorrect
            continue
    
    return result

class LevelChooserScreen:
    def __init__(self, setting, screen):
        self.screen = screen
        self.setting = setting 
        self.title_text = "What level do you want?"  # Game title

        self.sound_manager = SoundManager()
        self.sound_manager.set_music_volume(self.setting.music_volume) 
        self.sound_manager.set_sfx_volume(self.setting.sfx_volume)
        self.loading_assets()
        self.set_fonts()
        # Adjust button alignment
        start_x = 2 * BUTTON_MARGIN  # Buttons aligned to the left with some margin
        start_y = self.setting.screen_height // 2 - (3.5 * BUTTON_HEIGHT + 2 * BUTTON_MARGIN) // 2
        
        self.right_hand_up_flag = False  # Second debounce layer for right hand up
        self.right_hand_down_flag = False  # Second debounce layer for right hand down
        self.left_hand_up_flag = False  # Second debounce layer for left hand up
        self.left_hand_down_flag = False  # Second debounce layer for left hand down
        self.start_time = time.time()
        self.last_frame_time = 0
        self.level_scores = process_scores_from_file("level_score.json")
        # Buttons with updated start_x
        self.buttons = [
            LevelBlock("Level 1", start_x, start_y, BUTTON_WIDTH, BUTTON_HEIGHT, round(BUTTON_WIDTH), round(BUTTON_HEIGHT * 1.2), BUTTON_WIDTH * 2.2, BORDER_RADIUS),
            LevelBlock("Level 2", start_x, start_y + BUTTON_HEIGHT + BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT, round(BUTTON_WIDTH), round(BUTTON_HEIGHT * 1.2), BUTTON_WIDTH * 2.2, BORDER_RADIUS),
            LevelBlock("Level 3", start_x, start_y + 2 * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT, round(BUTTON_WIDTH), round(BUTTON_HEIGHT * 1.2), BUTTON_WIDTH * 2.2, BORDER_RADIUS),
            LevelBlock("Level 4", start_x, start_y + 3 * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT, round(BUTTON_WIDTH), round(BUTTON_HEIGHT * 1.2), BUTTON_WIDTH * 2.2, BORDER_RADIUS),
            LevelBlock("Back to Title", start_x, start_y + 4.5 * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT, round(BUTTON_WIDTH * 1.1), round(BUTTON_HEIGHT * 1), BUTTON_WIDTH * 2.05, BORDER_RADIUS),
        ]

        self.background_dark = Background(self.setting.screen_width, self.setting.screen_height, "night")
        self.last_update_time = time.time()
        self.selected_index = 0
        
        # Pre-create scoreboards
        self.scoreboards = self.create_all_scoreboards()
        self.current_scoreboard = None

    def on_enter(self):
        pass
    def loading_assets(self):

        script_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(script_dir, "..", "assets")  # Path to the assets directory
        tracks_dir = os.path.join(assets_dir, "tracks")  # Path to the assets directory
        fonts_dir = os.path.join(assets_dir, "fonts")
        self.bold_font_path = os.path.join(fonts_dir, "DynaPuff-Bold.ttf")
        self.regular_font_path = os.path.join(fonts_dir, "DynaPuff-Regular.ttf")

    def set_fonts(self):
        self.font = pygame.font.Font(self.regular_font_path, 42)
        self.stat_font = pygame.font.Font(self.regular_font_path, 32)
        self.title_font = pygame.font.Font(self.bold_font_path, 90)  # Larger font for the title

    def create_scoreboard(self, level_name):
        """Create a scoreboard for a single level."""
        if level_name in self.level_scores:
            level_data = self.level_scores[level_name]
            high_score = level_data["High Score"]
            latest_attempt = level_data["Latest Attempt"]
        else:
            # Default data for non-existent levels
            high_score = {"is_first_star": False, "is_second_star": False, "is_third_star": False, "perfect": 0, "missed": 0, "date": "No Data"}
            latest_attempt = {"is_first_star": False, "is_second_star": False, "is_third_star": False, "perfect": 0, "missed": 0, "date": "No Data"}

        scoreboard = Scoreboard(
            width=self.setting.screen_width // 4.5,
            height=self.setting.screen_height // 1.7,
            font=self.font,
            stat_font=self.stat_font
        )
        scoreboard.high_score_data = {
            "stars": high_score["is_first_star"] + high_score["is_second_star"] + high_score["is_third_star"],
            "perfect": high_score["perfect"],
            "misses": high_score["missed"],
            "timestamp": high_score["date"]
        }
        scoreboard.latest_attempt_data = {
            "stars": latest_attempt["is_first_star"] + latest_attempt["is_second_star"] + latest_attempt["is_third_star"],
            "perfect": latest_attempt["perfect"],
            "misses": latest_attempt["missed"],
            "timestamp": latest_attempt["date"]
        }
        return scoreboard

    def create_all_scoreboards(self):
        """Create a scoreboard for each level."""
        level_names = ["level_1", "level_2", "level_3", "level_4", "level_5"]  # Corresponding to button names
        scoreboards = []

        for level_name in level_names:
            scoreboard = self.create_scoreboard(level_name)
            scoreboards.append(scoreboard)
        
        return scoreboards

    def update_hover_states(self):
        """Update which button is hovered based on the selected index."""
        for i, button in enumerate(self.buttons):
            if i == self.selected_index:
                button.select()
                # Use the pre-created scoreboard for the hovered level (except for "Back to Title")
                if button.text != "Back to Title":
                    self.current_scoreboard = self.scoreboards[i]  # Fetch from the list
                else:
                    self.current_scoreboard = None
            else:
                button.unselect()
    
    def apply_settings(self):
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
                with lock:
                    disengage()
                if self.selected_index == 0:
                    print("Level 1")  # Placeholder for starting the game
                    return "level_1"
                elif self.selected_index == 1:
                    print("Level 2")
                    return "level_2"
                elif self.selected_index == 2:
                    print("Level 3")
                    return "level_3"
                elif self.selected_index == 3:
                    print("Level 4")
                elif self.selected_index == 4:
                    return "title"
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
                    print("Level 1")  # Placeholder for starting the game
                    return "level_1"
                elif self.selected_index == 1:
                    print("Level 2")
                    return "level_2"
                elif self.selected_index == 2:
                    print("Level 3")
                    return "level_3"
                elif self.selected_index == 3:
                    print("Level 4")
                elif self.selected_index == 4:
                    return "title"
            
                
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
        """Draw the level chooser screen."""
        self.screen.fill(WHITE)
        self.background_dark.draw(self.screen, 0)

        # Draw title
        title_surface = self.title_font.render(self.title_text, True, (238, 186, 255))
        title_rect = title_surface.get_rect(center=(self.setting.screen_width // 2, self.setting.screen_height // 6))
        self.screen.blit(title_surface, title_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen, self.font)

        # Draw the current scoreboard if applicable
        if self.current_scoreboard:
            scoreboard_surface = self.current_scoreboard.draw()
            scoreboard_rect = scoreboard_surface.get_rect(center=(self.setting.screen_width // 1.2, self.setting.screen_height // 1.7))
            self.screen.blit(scoreboard_surface, scoreboard_rect)

if __name__ == "__main__":
    # Initialize Pygame
    detection_result = {
                "detection_of_sensors": False,
                "right_hand_up": False,
                "left_hand_up": False,
                "right_hand_down": False,
                "left_hand_down": False,
                "clapped": False,
                "cross_arm": False,
                "ended": False
            }
    pygame.init()
    setting = SettingsManager()
    screen = pygame.display.set_mode((setting.screen_width, setting.screen_height))
    pygame.display.set_caption("Title Screen")

    # Initialize the title screen
    level_screen = LevelChooserScreen(setting, screen)

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            level_screen.handle_events(event, detection_result, None)

        level_screen.update()
        level_screen.draw()
        pygame.display.flip()
        clock.tick(90)

    pygame.quit()
