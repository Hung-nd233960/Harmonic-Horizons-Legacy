import pygame, time

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT = (0, 255, 0)
BOX_COLOR = (250, 202, 236)
SELECTED_BOX_COLOR = (240, 201, 255)

class AssessibilitySettingsScreen:
    def __init__(self, sound_manager, settings_manager, screen, background):
        self.settings_manager = settings_manager
        self.font = pygame.font.SysFont("Arial", 40)
        self.title_font = pygame.font.SysFont("Arial", 80)
        self.sound_manager = sound_manager
        self.screen = screen
        self.selected_index = 0
        self.background = background
        self.right_hand_up_flag = False  # Second debounce layer for right hand up
        self.right_hand_down_flag = False  # Second debounce layer for right hand down
        self.left_hand_up_flag = False  # Second debounce layer for left hand up
        self.left_hand_down_flag = False  # Second debounce layer for left hand down
        # Define accessibility settings based on SettingsManager
        self.assessibility_settings = [
            "Grace Period", 
            "Detection", 
            "Motion Detection Sensitivity", 
            "Sound Detection Sensitivity", 
            "Back"
        ]
        self.last_frame_time = 0 
        self.screen_width = settings_manager.screen_width
        self.screen_height = settings_manager.screen_height
        self.last_update_time = time.time()
        self.start_time = time.time()

    # Function to draw rounded rectangles
    def draw_rounded_rect(self, surface, color, rect, radius=30):
        pygame.draw.rect(surface, color, rect, border_radius=radius)

    # Draw the settings screen
    def draw(self):
        self.screen.fill(WHITE)  # Set the background color to white
        self.background.draw(self.screen, 0)
        # Draw the title (Centered in a rectangle)
        title_text = "Accessibility Settings"
        title_surface = self.title_font.render(title_text, True, BLACK)
        title_width = title_surface.get_width()
        title_height = title_surface.get_height()
        
        # Center the title rectangle
        title_rect_width = title_width + 40  # Extra padding around the title
        title_rect_height = title_height + 20  # Extra padding around the title
        title_rect_x = (self.screen_width - title_rect_width) // 2  # Center horizontally
        title_rect_y = self.screen_height // 12  # Move title closer to the top
        
        # Draw the title background rectangle
        self.draw_rounded_rect(self.screen, BOX_COLOR, (title_rect_x, title_rect_y, title_rect_width, title_rect_height))
        
        # Draw the title text centered within the rectangle
        title_text_x = title_rect_x + (title_rect_width - title_width) // 2
        title_text_y = title_rect_y + (title_rect_height - title_height) // 2
        self.screen.blit(title_surface, (title_text_x, title_text_y))  # Center text in title box

        # Draw the settings options
        y_pos = self.screen_height // 4  # Move the settings options up a bit, closer to the title
        box_height = self.screen_height // 14  # Adjust height to make them larger
        box_width = self.screen_width // 2  # Box width adjusted for larger resolution
        
        for i, setting in enumerate(self.assessibility_settings):
            # Get setting value based on the setting key
            if setting == "Grace Period":
                setting_text = f"{setting}: {self.settings_manager.grace_period}s"
            elif setting == "Detection":
                setting_text = f"{setting}: {'On' if self.settings_manager.detection else 'Off'}"
            elif setting == "Motion Detection Sensitivity":
                setting_text = f"{setting}: {self.settings_manager.motion_detection_sensitivity}"
            elif setting == "Sound Detection Sensitivity":
                setting_text = f"{setting}: {self.settings_manager.sound_detection_sensitivity}"
            else:
                setting_text = setting
            
            text_surface = self.font.render(setting_text, True, BLACK)
            text_width = text_surface.get_width()
            text_height = text_surface.get_height()
            
            # Calculate position for the text and the box
            x_pos = self.screen_width // 2 - box_width // 2
            y_pos_offset = y_pos + (box_height - text_height) // 2  # Vertically center the text inside the box
            
            # Draw the box with rounded corners
            box_color = SELECTED_BOX_COLOR if i == self.selected_index else BOX_COLOR
            self.draw_rounded_rect(self.screen, box_color, (x_pos, y_pos, box_width, box_height))
            
            # Draw the text inside the box
            self.screen.blit(text_surface, (x_pos + (box_width - text_width) // 2, y_pos_offset))
            
            y_pos += box_height + 30  # Adjusted space between boxes for more room

    def update(self):
        current_time = time.time() - self.start_time
        dt = current_time - self.last_frame_time
        self.background.update(dt)
        self.last_frame_time = current_time  # No constant updates needed for this screen (no animation, etc.)

    def handle_event(self, event, detection_results, lock):
        current_time = time.time()
        def disengage():
                detection_results['clapped'] = False
                detection_results["right_hand_up"] = False
                detection_results["left_hand_up"] = False
                detection_results["right_hand_down"] = False
                detection_results["left_hand_down"] = False
                detection_results["cross_arm"] = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.assessibility_settings)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.assessibility_settings)
            elif event.key == pygame.K_SPACE:
                setting = self.assessibility_settings[self.selected_index]
                
                # Handle settings change
                if setting == "Grace Period":
                    current_index = self.settings_manager.grace_period_options.index(self.settings_manager.grace_period)
                    new_index = (current_index + 1) % len(self.settings_manager.grace_period_options)
                    self.settings_manager.grace_period = self.settings_manager.grace_period_options[new_index]
                
                elif setting == "Detection":
                    self.settings_manager.detection = not self.settings_manager.detection
                
                elif setting == "Motion Detection Sensitivity":
                    current_index = self.settings_manager.motion_sensitivity_options.index(self.settings_manager.motion_detection_sensitivity)
                    new_index = (current_index + 1) % len(self.settings_manager.motion_sensitivity_options)
                    self.settings_manager.motion_detection_sensitivity = self.settings_manager.motion_sensitivity_options[new_index]
                
                elif setting == "Sound Detection Sensitivity":
                    current_index = self.settings_manager.sound_sensitivity_options.index(self.settings_manager.sound_detection_sensitivity)
                    new_index = (current_index + 1) % len(self.settings_manager.sound_sensitivity_options)
                    self.settings_manager.sound_detection_sensitivity = self.settings_manager.sound_sensitivity_options[new_index]
                
                elif setting == "Back":
                    # Save the current settings
                    return "settings"
        else:
            if current_time - self.last_frame_time >= 1:
                    
                if detection_results["right_hand_up"]:
                    if not self.right_hand_up_flag:
                        self.right_hand_up_flag = True
                        self.selected_index = (self.selected_index - 1) % len(self.assessibility_settings)
                        self.right_hand_up_flag = False
                if detection_results["left_hand_up"]:
                    if not self.left_hand_up_flag:
                        self.left_hand_up_flag = True
                        self.selected_index = (self.selected_index - 1) % len(self.assessibility_settings)
                    else:
                        self.left_hand_up_flag = False
                if detection_results["left_hand_down"]:
                    if not self.left_hand_down_flag:
                        self.left_hand_down_flag = True
                        self.selected_index = (self.selected_index + 1) % len(self.assessibility_settings)
                    else:
                        self.left_hand_down_flag = False
                if detection_results["right_hand_down"]:
                    if not self.right_hand_down_flag:
                        self.right_hand_down_flag = True
                        self.selected_index = (self.selected_index + 1) % len(self.assessibility_settings)
                    else:
                        self.right_hand_down_flag = False
                        
                if detection_results["clapped"]:
                    setting = self.assessibility_settings[self.selected_index]
                # Handle settings change
                    if setting == "Grace Period":
                        current_index = self.settings_manager.grace_period_options.index(self.settings_manager.grace_period)
                        new_index = (current_index + 1) % len(self.settings_manager.grace_period_options)
                        self.settings_manager.grace_period = self.settings_manager.grace_period_options[new_index]
                    
                    elif setting == "Detection":
                        self.settings_manager.detection = not self.settings_manager.detection
                    
                    elif setting == "Motion Detection Sensitivity":
                        current_index = self.settings_manager.motion_sensitivity_options.index(self.settings_manager.motion_detection_sensitivity)
                        new_index = (current_index + 1) % len(self.settings_manager.motion_sensitivity_options)
                        self.settings_manager.motion_detection_sensitivity = self.settings_manager.motion_sensitivity_options[new_index]
                    
                    elif setting == "Sound Detection Sensitivity":
                        current_index = self.settings_manager.sound_sensitivity_options.index(self.settings_manager.sound_detection_sensitivity)
                        new_index = (current_index + 1) % len(self.settings_manager.sound_sensitivity_options)
                        self.settings_manager.sound_detection_sensitivity = self.settings_manager.sound_sensitivity_options[new_index]
                    
                    elif setting == "Back":
                        # Save the current settings
                        return "settings"
                self.last_update_time = current_time

"""
# Main loop
if __name__ == "__main__":
    # Initialize Pygame
    pygame.init()
    
    # Initialize SettingsManager
    settings_manager = SettingsManager()
    
    # Set up the screen based on current settings
    screen = pygame.display.set_mode(
        (settings_manager.screen_width, settings_manager.screen_height), 
        pygame.FULLSCREEN if settings_manager.full_screen else 0
    )
    pygame.display.set_caption("Accessibility Settings")

    # Initialize the accessibility settings screen
    accessibility_screen = AssessibilitySettingsScreen(screen, settings_manager)
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            result = accessibility_screen.handle_event(event)
            if result == "settings":
                break

        accessibility_screen.update()
        accessibility_screen.draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()
"""