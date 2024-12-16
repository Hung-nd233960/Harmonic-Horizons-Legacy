import pygame, time

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT = (0, 255, 0)
BOX_COLOR = (250, 202, 236)
SELECTED_BOX_COLOR = (240, 201, 255)

class ImageSettingsScreen:
    def __init__(self, sound_manager, settings_manager, screen, background):
        self.settings_manager = settings_manager
        self.font = pygame.font.SysFont("Arial", 40)
        self.title_font = pygame.font.SysFont("Arial", 80)
        self.background = background
        self.sound_manager = sound_manager
        self.screen = screen
        self.selected_index = 0
        self.right_hand_up_flag = False  # Second debounce layer for right hand up
        self.right_hand_down_flag = False  # Second debounce layer for right hand down
        self.left_hand_up_flag = False  # Second debounce layer for left hand up
        self.left_hand_down_flag = False  # Second debounce layer for left hand down
        self.settings_keys = [
            "Resolution", 
            "FPS", 
            "Full Screen", 
            "VSync",
            "Back"
        ]
        self.last_frame_time = 0
        self.screen_width, self.screen_height = screen.get_size()
        self.last_update_time = time.time()
        self.start_time = time.time()
    def draw_rounded_rect(self, surface, color, rect, radius=30):
        pygame.draw.rect(surface, color, rect, border_radius=radius)

    def draw(self):
        self.screen.fill(WHITE)
        self.background.draw(self.screen, 0)
        # Draw title
        title_text = "Image Settings"
        title_surface = self.title_font.render(title_text, True, BLACK)
        title_width = title_surface.get_width()
        title_height = title_surface.get_height()
        
        title_rect_width = title_width + 40
        title_rect_height = title_height + 20
        title_rect_x = (self.screen_width - title_rect_width) // 2
        title_rect_y = self.screen_height // 12
        
        self.draw_rounded_rect(self.screen, BOX_COLOR, (title_rect_x, title_rect_y, title_rect_width, title_rect_height))
        
        title_text_x = title_rect_x + (title_rect_width - title_width) // 2
        title_text_y = title_rect_y + (title_rect_height - title_height) // 2
        self.screen.blit(title_surface, (title_text_x, title_text_y))

        # Draw settings options
        y_pos = self.screen_height // 4
        box_height = self.screen_height // 14
        box_width = self.screen_width // 2
        
        for i, setting in enumerate(self.settings_keys):
            # Get setting value based on the setting key
            if setting == "Resolution":
                setting_text = f"{setting}: {self.settings_manager.screen_width}x{self.settings_manager.screen_height}"
            elif setting == "FPS":
                setting_text = f"{setting}: {self.settings_manager.fps}"
            elif setting == "Full Screen":
                setting_text = f"{setting}: {'On' if self.settings_manager.full_screen else 'Off'}"
            elif setting == "VSync":
                setting_text = f"{setting}: {'On' if self.settings_manager.vsync else 'Off'}"
            else:
                setting_text = setting
            
            text_surface = self.font.render(setting_text, True, BLACK)
            text_width = text_surface.get_width()
            text_height = text_surface.get_height()
            
            x_pos = self.screen_width // 2 - box_width // 2
            y_pos_offset = y_pos + (box_height - text_height) // 2
            
            box_color = SELECTED_BOX_COLOR if i == self.selected_index else BOX_COLOR
            self.draw_rounded_rect(self.screen, box_color, (x_pos, y_pos, box_width, box_height))
            
            self.screen.blit(text_surface, (x_pos + (box_width - text_width) // 2, y_pos_offset))
            
            y_pos += box_height + 30

    def update(self):
        current_time = time.time() - self.start_time
        dt = current_time - self.last_frame_time
        self.background.update(dt)
        self.last_frame_time = current_time

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
                self.selected_index = (self.selected_index - 1) % len(self.settings_keys)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.settings_keys)
            elif event.key == pygame.K_SPACE:
                setting = self.settings_keys[self.selected_index]
                
                if setting == "Resolution":
                    current_index = self.settings_manager.resolutions.index(f"{self.settings_manager.screen_width}x{self.settings_manager.screen_height}")
                    new_index = (current_index + 1) % len(self.settings_manager.resolutions)
                    res = self.settings_manager.resolutions[new_index].split('x')
                    self.settings_manager.screen_width = int(res[0])
                    self.settings_manager.screen_height = int(res[1])
                
                elif setting == "FPS":
                    current_index = self.settings_manager.fps_options.index(self.settings_manager.fps)
                    new_index = (current_index + 1) % len(self.settings_manager.fps_options)
                    self.settings_manager.fps = self.settings_manager.fps_options[new_index]
                
                elif setting == "Full Screen":
                    self.settings_manager.full_screen = not self.settings_manager.full_screen
                
                elif setting == "VSync":
                    self.settings_manager.vsync = not self.settings_manager.vsync
                
                elif setting == "Back":
                    # Save the current settings
                    return "settings"
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
                    if setting == "Resolution":
                        current_index = self.settings_manager.resolutions.index(f"{self.settings_manager.screen_width}x{self.settings_manager.screen_height}")
                        new_index = (current_index + 1) % len(self.settings_manager.resolutions)
                        res = self.settings_manager.resolutions[new_index].split('x')
                        self.settings_manager.screen_width = int(res[0])
                        self.settings_manager.screen_height = int(res[1])
                    
                    elif setting == "FPS":
                        current_index = self.settings_manager.fps_options.index(self.settings_manager.fps)
                        new_index = (current_index + 1) % len(self.settings_manager.fps_options)
                        self.settings_manager.fps = self.settings_manager.fps_options[new_index]
                    
                    elif setting == "Full Screen":
                        self.settings_manager.full_screen = not self.settings_manager.full_screen
                    
                    elif setting == "VSync":
                        self.settings_manager.vsync = not self.settings_manager.vsync
                    
                    elif setting == "Back":
                        # Save the current settings
                        return "settings"
                self.last_update_time = current_time
