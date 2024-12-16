import pygame
from levels import Level1, Level2, Level3

class ScreenManager:
    def __init__(self, initial_screen):
        self.screen = initial_screen

    def update_screen(self, new_screen):
        self.screen = new_screen

class SceneManager:
    def __init__(self, settings_object, screen, clock):
        self.screen = screen
        self.scenes = {}
        self.current_scene = None
        self.next_scene = None
        self.transitioning = False
        self.transition_phase = "none"  # Can be "white_out", "transition", or "none"
        self.transition_progress = 0
        self.transition_speed = 0.02  # Speed of transition
        self.current_level = ""
        self.clock = clock
        self.settings_object = settings_object

    def add_scene(self, name, scene):
        """Add a new scene to the scene manager."""
        self.scenes[name] = scene
    def purge_scene(self, name):
        self.scenes.pop(name)
    def change_scene(self, name, state = "",transition_type="fade"):
        """Initiate a transition to the next scene."""
        if name in self.scenes and not self.transitioning:
            self.next_scene = name
            self.state_of_scene = state 
            self.transitioning = True
            self.transition_phase = "white_out"
            self.transition_type = transition_type
            self.transition_progress = 0
            
    def handle_events(self, event, detection_results, lock):
        # Define a dictionary for level classes
        level_classes = {
            "level_1": Level1.Gameplaylevel1,
            "level_2": Level2.Gameplaylevel2,
        }

        # Delegate event handling to the current scene
        if not self.transitioning and self.current_scene:
            next_scene = self.current_scene.handle_events(event, detection_results, lock)
            
            if next_scene in level_classes:
                # Update the current level and switch to the new level
                self.current_level = next_scene
                self.add_scene("game", level_classes[next_scene](self.settings_object, self.screen, self.clock))
                self.change_scene("game")
            
            elif next_scene == "resume":
                self.change_scene("game", "resume")
            
            elif next_scene == "restart":
                # Restart the current level
                self.purge_scene("game")
                if self.current_level in level_classes:
                    self.add_scene("game", level_classes[self.current_level](self.settings_object, self.screen, self.clock))
                    self.change_scene("game")
            
            elif next_scene == "title":
                if self.settings_object.changes_needed or self.settings_object.check_changes():
                    # Reset screen with new settings
                    new_screen = self.settings_object.apply_image_changes(self.screen)
                    
                    # Update screen for all scenes
                    for scene in self.scenes.values():
                        scene.screen = new_screen
                        scene.sound_manager.set_music_volume(self.settings_object.music_volume)
                        scene.sound_manager.set_sfx_volume(self.settings_object.sfx_volume)
                        scene.apply_settings()
                    
                    # Update SceneManager's screen and reset changes flag
                    self.screen = new_screen
                    self.settings_object.changes_needed = False
                
                self.change_scene(next_scene)
            
            elif next_scene == "game_over":
                self.change_scene(next_scene)
            elif next_scene:
                self.change_scene(next_scene)


    def update(self):
        """Update the current scene or handle transition effects."""
        if self.transitioning:
            self.transition_progress += self.transition_speed
            if self.transition_phase == "white_out" and self.transition_progress >= 1:
                # Move to the transition phase after white-out
                self.transition_phase = "transition"
                self.transition_progress = 0
            elif self.transition_phase == "transition" and self.transition_progress >= 1:
                # Transition complete, set the new scene
                self.current_scene = self.scenes[self.next_scene]
                if self.state_of_scene == "resume":
                    self.current_scene.on_resume()
                else:
                    self.current_scene.on_enter()
                self.state_of_scene = ""
                self.next_scene = None
                self.transitioning = False
                self.transition_phase = "none"
        else:
            if self.current_scene:
                self.current_scene.update()

    def draw(self):
        """Draw the current scene and apply transition effects."""
        if self.transitioning:
            if self.transition_phase == "white_out":
                self.white_out_transition()
            elif self.transition_phase == "transition":
                if self.transition_type == "fade":
                    self.fade_transition()
                elif self.transition_type == "slide_up":
                    self.slide_transition(direction="up")
                elif self.transition_type == "slide_down":
                    self.slide_transition(direction="down")
        else:
            if self.current_scene:
                self.current_scene.draw()

    def white_out_transition(self):
        """White out the screen."""
        eased_progress = self.ease_in_out(self.transition_progress)
        white_surface = pygame.Surface(self.screen.get_size())
        white_surface.fill((255, 255, 255))  # White-out color
        alpha = int(eased_progress * 255)
        white_surface.set_alpha(alpha)
        self.screen.blit(white_surface, (0, 0))

    def fade_transition(self):
        """Apply a fade transition effect."""
        eased_progress = self.ease_in_out(self.transition_progress)

        if self.current_scene:
            self.current_scene.draw()

        if self.next_scene:
            self.scenes[self.next_scene].draw()

        fade_surface = pygame.Surface(self.screen.get_size())
        fade_surface.fill((255, 255, 255))  # Transition color (white fade)
        alpha = int((1 - eased_progress) * 255)
        fade_surface.set_alpha(alpha)
        self.screen.blit(fade_surface, (0, 0))

    def slide_transition(self, direction):
        """Apply a slide transition effect."""
        eased_progress = self.ease_in_out(self.transition_progress)
        offset = int(eased_progress * self.screen.get_height())

        if direction == "up":
            # Current scene slides up
            if self.current_scene:
                self.screen.blit(self.screen, (0, -offset))
            # Next scene slides in from below
            if self.next_scene:
                self.scenes[self.next_scene].draw()
                self.screen.blit(self.screen, (0, self.screen.get_height() - offset))
        elif direction == "down":
            # Current scene slides down
            if self.current_scene:
                self.screen.blit(self.screen, (0, offset))
            # Next scene slides in from above
            if self.next_scene:
                self.scenes[self.next_scene].draw()
                self.screen.blit(self.screen, (0, -self.screen.get_height() + offset))

    @staticmethod
    def ease_in_out(t):
        """Easing function for smooth acceleration and deceleration."""
        return t * t * (3 - 2 * t)
    

    