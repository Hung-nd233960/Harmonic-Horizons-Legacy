import pygame
import json
import os

class SettingsManager:
    def __init__(self, screen_width=1920, screen_height=1080, fps=120, full_screen=True,vsync = True, music_volume=0.5, sfx_volume=0.5, 
                 grace_period=0.3, detection=False, motion_detection_sensitivity=0.5, sound_detection_sensitivity=30):
        """
        Initializes the SettingsManager with default or provided values.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.fps = fps
        self.full_screen = full_screen
        self.vsync = vsync
        self.music_volume = music_volume
        self.sfx_volume = sfx_volume
        self.grace_period = grace_period
        self.detection = detection
        self.motion_detection_sensitivity = motion_detection_sensitivity
        self.sound_detection_sensitivity = sound_detection_sensitivity
        self.grace_period_options = [0.1, 0.2, 0.3, 0.4, 0.5, 0.8, 1.0]
        self.sound_sensitivity_options = [20, 30, 40, 50]
        self.motion_sensitivity_options = [0.2, 0.5, 0.7]
        self.resolutions = ["1920x1080", "1024x768", "800x600"]
        self.fps_options = [30, 60, 90, 120, 144]
        self.changes_needed = False
        # Load settings from JSON if available
        self.load_settings()

    def load_settings(self):
        """
        Loads settings from a settings.json file if it exists. If not, creates the file
        with default settings.
        """
        settings_file = "settings.json"
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                loaded_settings = json.load(f)
                for key, value in loaded_settings.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                print("Settings loaded from settings.json")
        else:
            self.save_settings()

    def save_settings(self):
        """
        Saves the settings to the settings.json file.
        """
        settings = self.get_settings_as_dict()
        with open("settings.json", 'w') as f:
            json.dump(settings, f, indent=4)
        print("settings saved to settings.json")

    def reset_settings(self):
        """
        Resets all settings to their default values and updates settings.json.
        """
        self.screen_width = 1920
        self.screen_height = 1080
        self.fps = 120
        self.full_screen = True
        self.vsync = False
        self.music_volume = 0.5
        self.sfx_volume = 0.5
        self.grace_period = 0.3
        self.detection = False
        self.motion_detection_sensitivity = 0.5
        self.sound_detection_sensitivity = 30
        self.save_settings()
        print("All settings have been reset to default values.")

    def update_settings(self, changes):
        """
        Updates the settings based on a dictionary of changes.
        """
        for key, value in changes.items():
            if hasattr(self, key):
                setattr(self, key, value)
                print(f"{key} updated to: {value}")
            else:
                print(f"Invalid setting: {key}")

    def apply_image_changes(self, screen):
        """
        Applies the changes to the Pygame environment.
        """
        screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN if self.full_screen else 0, 0,0, self.vsync)
        return screen

    def get_settings_as_dict(self):
        """
        Returns the current settings as a dictionary.
        """
        return {
            "screen_width": self.screen_width,
            "screen_height": self.screen_height,
            "fps": self.fps,
            "full_screen": self.full_screen,
            "vsync": self.vsync,
            "music_volume": self.music_volume,
            "sfx_volume": self.sfx_volume,
            "grace_period": self.grace_period,
            "detection": self.detection,
            "motion_detection_sensitivity": self.motion_detection_sensitivity,
            "sound_detection_sensitivity": self.sound_detection_sensitivity
        }

    def apply_settings_from_dict(self, settings_dict):
        """
        Applies settings from a dictionary, updating the settings and saving them.

        :param settings_dict: Dictionary of settings to apply.
        """
        for key, value in settings_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
                print(f"{key} set to: {value}")
            else:
                print(f"Invalid setting: {key}")
        self.save_settings()
    
    def check_changes(self):
        """
        Checks if the current settings differ from the ones saved in settings.json.
        Returns True if there are changes, False otherwise.
        """
        settings_file = "settings.json"
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                loaded_settings = json.load(f)
            
            current_settings = self.get_settings_as_dict()
            
            # Compare loaded settings with current settings
            for key, value in loaded_settings.items():
                if current_settings.get(key) != value:
                    print(f"Settings have changed: {key} was {value}, now {current_settings.get(key)}")
                    return True  # Return True if there's a mismatch
        return False  # Return False if no changes detected

