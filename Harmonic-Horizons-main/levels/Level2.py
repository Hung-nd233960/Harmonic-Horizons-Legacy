import pygame
import os, sys
import time, random

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from resources.UIElements import create_smooth_rainbow_gradient, create_horizontal_gradient_surface, Background
from Settings.settings import SettingsManager
from Settings.SoundManager import SoundManager
from resources.tools import load_frames_from_spritesheet, BackgroundArtifacts, update_score, EffectManager
from resources.environment import Trailing
setting_object = SettingsManager()

class Raindrop(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, length, rain_image):
        super().__init__()
        self.speed = speed
        self.image = rain_image
        self.length = length
        # Set up rect for position tracking
        self.rect = self.image.get_rect(topleft = (x, y))

    def update(self, screen_height, dt):
        """Update the position of the raindrop."""
        self.rect.y += round(self.speed * dt)  # Update the position using the rect
        if self.rect.y > screen_height:  # Reset if out of bounds
            self.rect.y = -3*self.length # Reset above the screen

class level2Background(Background):
    def __init__(self, screen_width, screen_height, image_path):
        super().__init__(screen_width, screen_height, "custom", None, (25, 50, 100), (10, 20, 60))

        # Pre-allocate a surface for rendering
        self.background_surface = pygame.Surface((self.width, self.height))
        self.rain_color = (197,226,247)
        # Load frames from the spritesheet (parallax layers)
        self.assets, self.frame_width, self.frame_height = load_frames_from_spritesheet(image_path, 6, 1)
        self.base_speed = 350

        self.lightning_texture = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        self.lightning_texture.blit(create_horizontal_gradient_surface(self.lightning_texture.get_rect(), (132, 132, 138),(32, 32, 33)))
        self.effects = EffectManager(self.background_surface, self.lightning_texture)
        # Define speeds and offsets
        self.layer_configs = {
            "big_clouds_1": {"asset": self.assets[1], "speed": 0.5, "y_offset": -350},
            "small_cloud_3": {"asset": self.assets[2], "speed": 0.3, "y_offset": -300},
            "small_cloud_1": {"asset": self.assets[2], "speed": 0.6, "y_offset": -200},
            "small_cloud_2": {"asset": self.assets[2], "speed": 0.8, "y_offset": 0},
            "medium_trees": {"asset": self.assets[3], "speed": 1.0, "y_offset": 200},
            "far_trees": {"asset": self.assets[4], "speed": 0.3, "y_offset": 250},
            #"close_trees": {"asset": self.assets[5], "speed": 1.5, "y_offset": 300},
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

        # Pre-render rainflake images
        self.rain_images = self._create_rain_images()

        # Re-create rain with optimized rain
        self.rain_group = pygame.sprite.Group()
        self.create_rain(300)

    def _create_rain_images(self):
        """Generate and cache rainflake images."""
        rain_images = {}
        for length in [15, 20, 25, 30]:
            surface = pygame.Surface((4, length), pygame.SRCALPHA)
            pygame.draw.line(surface, self.rain_color, (0, 0), (0, length), 4)
            rain_images[length] = surface
        return rain_images

    def create_rain(self, num_drops=500):
        for _ in range(num_drops):
            x = random.randint(0, self.width)
            y = random.randint(-self.height, self.height)
            speed = random.uniform(1500, 1650)
            length = random.choice([15, 20, 25, 30])
            raindrop = Raindrop(x, y, speed, length, self.rain_images[length])
            self.rain_group.add(raindrop)

    def update(self, dt):
        self.rain_group.update(self.height, dt)
        self.layers_group.update(dt)
        if self.effects.is_dimming_active:
            self.effects.apply_dimming(dt)
        if self.effects.is_lightning_active:
            self.effects.apply_lightning(dt)

    def draw(self, surface, y_pos):
        self.background_surface.blit(self.image, (0, 0))
        for artifact in self.layers_group:
            artifact.draw(self.background_surface)

        self.rain_group.draw(self.background_surface)
        surface.blit(self.background_surface, (0, y_pos))
        
class Note:
    def __init__(self, time_start, time_end, type, placement):
        self.time_start = time_start
        self.time_end = time_end
        self.duration = time_end - time_start
        self.type = type
        self.placement = placement
        self.checked = False
        self.active = False
        self.spawned = False

class Guideline(pygame.sprite.Sprite):
    border_radius = 30
    def __init__(self, x, guideline_y, width, height, note):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)  # Create a surface for the image
        self.rect = self.image.get_rect()  # Get the rectangle that defines the surface size and position
        self.total_correct_frames = 0
        self.fill_surface = create_horizontal_gradient_surface(self.rect, (204, 191, 121), (255, 239, 151), Guideline.border_radius)  # Create the gradient surface
        self.rainbow_surface = create_smooth_rainbow_gradient(self.rect, Guideline.border_radius)
        self.align_surface = create_horizontal_gradient_surface(self.rect, (250, 216, 157), (250, 150, 122), Guideline.border_radius)
        self.note = note
        self.unalign()
        self.correct_frames = 0
        # Adjust the rect's y position based on the center y of the guideline
        self.rect.x = x
        self.rect.centery = guideline_y  # Now center of the guideline, not top-left
        self.aligned = False
        self.score_timer = 0
    def update(self, x=None):
        # If x is provided, update the x position of the guideline
        if x is not None:
            self.rect.x = x

    def move(self, speed, dt):
        """Move the guideline left or right depending on speed."""
        self.rect.x -= round(speed * dt)

    def align(self):
        self.image.blit(self.align_surface, (0, 0))
        self.aligned = True
        self.image.set_alpha(200)

    def unalign(self):
        self.image.blit(self.fill_surface, (0, 0))
        self.aligned = False
        self.image.set_alpha(50)
    def collided(self):
        self.image.set_alpha(225)
        self.image.blit(self.rainbow_surface, (0, 0))
    @property
    def guideline_y(self):
        return self.rect.centery  # Return the center y (not the top-left y)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, speed, note, basic_image_path, hit_image_path):
        super().__init__()
        self.note = note
        self.speed = speed
        self.is_hit = False
        self.basic_frames, self.frame_width, self.frame_height = load_frames_from_spritesheet(basic_image_path, 32, 1)
        self.hit_frames, self.frame_width, self.frame_height = load_frames_from_spritesheet(hit_image_path, 32, 1)
        # Create a surface for the image
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.unhit()  # Initially unhit

    def move(self, speed, dt):
        """Move the obstacle left or right depending on speed."""
        self.rect.x -= round(speed * dt)

    def update(self, current_frame):
        self.image = self.current_frames[current_frame]
        
    def unhit(self):
        """Set the obstacle to its unhit state (red circle)."""
        self.is_hit = False
        self.image.fill((0, 0, 0, 0))  # Clear the surface
        self.current_frames = self.basic_frames

    def hit(self):
        """Set the obstacle to its hit state (yellow circle)."""
        self.is_hit = True
        self.image.fill((0, 0, 0, 0))  # Clear the surface
        self.current_frames = self.hit_frames
        #pygame.draw.circle(self.image, (255, 255, 0), (self.rect.width // 2, self.rect.height // 2), self.rect.width // 2)

class ObstacleGroup(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)
        self.frame_delay_static = 50 / 1000
        self.frame_delay_collision = 1 / 2000
        self.accumulated_time = 0
        self.frame_delay = self.frame_delay_static
        self.current_frame = 0
    
    def update(self, dt):
        self.accumulated_time += dt
        if self.accumulated_time >= self.frame_delay:
            self.current_frame = (self.current_frame + 1) % 32
            self.accumulated_time = 0
        super().update(self.current_frame)

class ship(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image_path, spring_direction='down', orientation='right', min_y=0, max_y=0):
        super().__init__()

        self.current_frame = 0
        self.frame_delay_static = 60 / 1000
        self.frame_delay_collision = 20 / 2000
        self.frame_delay = self.frame_delay_static
        self.basic_frames, self.frame_width, self.frame_height = load_frames_from_spritesheet(image_path, 18, 1)
        self.gray_frames = [pygame.transform.grayscale(frame) for frame in self.basic_frames]
        self.image = self.gray_frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.collided = False
        self.accumulated_time = 0

        self.trailing = {"static" :Trailing(
            height=round(height//3), 
            width=round(self.rect.centerx - width/4),
            speed = 100,
            left_wall=0,
            right_wall=round(self.rect.centerx - width/4), 
            num_particles=40, 
            move_direction=-1,  # Move left to match ship
            shape="circle"
        ), "collision":Trailing(
            height=round(height//2), 
            width=round(self.rect.centerx - width/4),
            speed = 800,
            left_wall=0, 
            right_wall=round(self.rect.centerx - width/4), 
            num_particles=100, 
            move_direction=-1,  # Move left to match ship
            shape="square")}
        self.current_trailing = self.trailing["static"]
        
        # Movement parameters
        self.y = y
        self.speed_up = 3000
        self.speed_down = 3000
        self.spring_direction = spring_direction
        self.orientation = orientation
        self.min_y = min_y
        self.max_y = max_y

        self.activated = False
        # Overshoot parameters
        self.overshoot_amount = 5
        self.return_speed = 2000
        self.overshoot_timer = 0
        self.overshoot_duration = 0.05
        self.is_moving_up = False
        self.is_moving_down = False
        self.in_overshoot = False
        self.initial_press = True
        
    def update(self, dt):
        if self.collided:
            self.current_trailing = self.trailing["collision"]
            self.frame_delay = self.frame_delay_collision
        else:
            self.current_trailing = self.trailing["static"]
            self.frame_delay = self.frame_delay_static
        """
        Update the animation frame based on accumulated delta time.
        The frame shifts once the accumulated time exceeds the threshold (frame_delay).
        """
        self.accumulated_time += dt  # Accumulate the delta time

        # If accumulated time exceeds the threshold, shift to the next frame
        if self.accumulated_time >= self.frame_delay:
            self.current_frame = (self.current_frame + 1) % len(self.basic_frames)
            if self.collided:
                self.image = self.basic_frames[self.current_frame]
            else:
                self.image = self.gray_frames[self.current_frame]
            self.accumulated_time = 0  # Reset accumulated time after switching frame
        self.current_trailing.update(dt)


    def move(self, dt, up_pressed, down_pressed, activated):
        # Check for new button presses
        self.up_pressed = up_pressed
        self.down_pressed = down_pressed
        self.activated = activated
        
        # Determine movement state
        if up_pressed and not self.is_moving_up:
            self.is_moving_up = True
            self.is_moving_down = False
            self.in_overshoot = True
            self.overshoot_timer = 0
            self.initial_press = True

        elif down_pressed and not self.is_moving_down:
            self.is_moving_down = True
            self.is_moving_up = False
            self.in_overshoot = True
            self.overshoot_timer = 0
            self.initial_press = True
        
        # Reset states when buttons are released
        if not up_pressed:
            self.is_moving_up = False
        if not down_pressed:
            self.is_moving_down = False

        # Unified upward movement logic
        movement_speed = self.speed_up
        
        if self.is_moving_up:
            if self.in_overshoot:
                if self.initial_press:
                    # Initial overshoot movement
                    target = self.min_y - self.overshoot_amount
                    self.y = max(target, self.y - movement_speed * dt)
                    if self.y <= target:
                        self.initial_press = False
                        self.overshoot_timer = 0
                else:
                    # Return from overshoot
                    self.overshoot_timer += dt
                    if self.overshoot_timer >= self.overshoot_duration:
                        self.y = min(self.min_y, self.y + self.return_speed * dt)
                        if self.y >= self.min_y:
                            self.in_overshoot = False
            else:
                # Stay at boundary
                self.y = self.min_y
                
        elif self.is_moving_down:
            if self.in_overshoot:
                if self.initial_press:
                    # Initial overshoot movement
                    target = self.max_y + self.overshoot_amount
                    self.y = min(target, self.y + self.speed_down * dt)
                    if self.y >= target:
                        self.initial_press = False
                        self.overshoot_timer = 0
                else:
                    # Return from overshoot
                    self.overshoot_timer += dt
                    if self.overshoot_timer >= self.overshoot_duration:
                        self.y = max(self.max_y, self.y - self.return_speed * dt)
                        if self.y <= self.max_y:
                            self.in_overshoot = False
            else:
                # Stay at boundary
                self.y = self.max_y
        else:
            # Return to rest position when no keys are pressed
            if self.spring_direction == 'down':
                rest_y = setting_object.screen_height/2
            if self.y < rest_y:
                self.y = min(rest_y, self.y + self.speed_down * dt)
            elif self.y > rest_y:
                self.y = max(rest_y, self.y - self.speed_up * dt)

        # Update sprite position
        self.rect.y = round(self.y - self.rect.height // 2)

def beat_processing(filename):
    """
    Reads a beat map file and organizes the data into Note objects.

    This function reads each line from a file, processes the data into Note objects,
    and calculates the maximum possible score based on note durations. 

    Parameters:
        filename (str): Path to the beat map file.

    Returns:
        tuple: 
            - notes (list): A list of Note objects created from the beat map.
            - max_score (int): The maximum score achievable for the beat map.
    
    Notes:
        - Each line in the file must be formatted as:
          <time_start> <time_end> <placement>
        - Type codes:
        'S' = Single 'L' = Long 
        - Placement codes:
          'U' = Up, 'D' = Down, 'M' = Middle, 

    Raises:
        ValueError: If the file contains invalid lines or unknown placement codes.
    """
    notes = []
    max_score = 0

    # Open the beat map file
    with open(filename, "r") as file:
        for line in file:
            # Parse and validate the line
            parts = line.strip().split()
            if len(parts) != 4:
                raise ValueError(f"Invalid note format: {line.strip()}. Expected 4 parts.")

            # Extract and validate timing information
            try:
                time_start = float(parts[0])
                time_end = float(parts[1])
            except ValueError:
                raise ValueError(f"Invalid timing values in line: {line.strip()}")

            # Ensure the timing is valid
            if time_end <= time_start:
                raise ValueError(f"Invalid time range in line: {line.strip()}")
            
            type_code = parts[2].upper()
            if type_code == "S":
                type = 'single'
            elif type_code == "L":
                type = 'long'
            else:
                raise ValueError(f"Unknown type code: '{parts[2]}' in line: {line.strip()}")

            # Assign a placement based on the code
            placement_code = parts[3].upper()
            if placement_code == "U":
                placement = 'up'
            elif placement_code == "D":
                placement = 'down'
            elif placement_code == "M":
                placement = 'middle'
            else:
                raise ValueError(f"Unknown placement code: '{parts[3]}' in line: {line.strip()}")

            # Calculate the score contribution for this note
            duration = time_end - time_start
            if type == "single":
                max_score += 10  # Fixed score for single notes
            else:
                max_score += max(1, int(duration // 0.1))  # Increment for duration-based scoring

            # Create and append the Note object
            notes.append(Note(time_start, time_end, type, placement))

    # Return the list of notes and the maximum score
    return notes, max_score

class Gameplaylevel2:
    def __init__(self, setting, screen, clock):
        self.screen = screen
        self.setting = setting
        self.clock = clock
        self.sound_manager = SoundManager()
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.PURPLE = (128, 0, 128)
        self.PINK = (255, 192, 203)

        # Sprite Groups
        self.all_sprites = pygame.sprite.Group()
        self.obstacles_group = ObstacleGroup()
        self.guidelines_group = pygame.sprite.Group()

        # Gameplay parameters
        self.grace_period = self.setting.grace_period
        self.activate_cooldown = 100 / 1000
        self.sound_manager.set_music_volume(self.setting.music_volume) 
        self.sound_manager.set_sfx_volume(self.setting.sfx_volume)

        self.obstacle_speed = 900
        self.guideline_speed = 450
        self.ship_screen_width, self.ship_screen_height = 120, 120
        self.score_line_length = 600
        self.score_line_width = 14
        if not self.setting.detection:
            self.detection_result = {
                "detection_of_sensors": False,
                "right_hand_up": False,
                "left_hand_up": False,
                "right_hand_down": False,
                "left_hand_down": False,
                "clapped": False,
                "cross_arm": False,
                "ended": False
            }
        
        self.loading_assets()
        self.set_fonts()
        
        self.reset_states()
        self.reset_score()

        # Create ships
        self.ship = ship(self.setting.screen_width/8, self.setting.screen_height/2, self.ship_screen_width, self.ship_screen_height, self.ship_path,
                         spring_direction='down', orientation='left',
                         min_y=self.setting.screen_height/2 - self.setting.screen_height/4, max_y=self.setting.screen_height/2 + self.setting.screen_height/4)
        
        self.all_sprites.add(self.ship)

    def loading_assets(self):
        """ Load game assets like beat map and music """

        script_dir = os.path.dirname(os.path.abspath(__file__))  # Current script directory
        assets_dir = os.path.join(script_dir, "..", "assets")  # Path to the assets directory
        tracks_dir = os.path.join(assets_dir, "tracks")
        fonts_dir = os.path.join(assets_dir, "fonts")
        # Update file paths
        self.beat_map_file_path = os.path.join(tracks_dir, "level2Beat.txt")
        self.music_file_path = os.path.join(tracks_dir, "level2Track.wav")
        self.ship_path = os.path.join(assets_dir, "balloon.png")
        self.background_path = os.path.join(assets_dir, "theme.png")
        self.sfx_path = os.path.join(assets_dir, "HitSoundEffect.wav")
        self.rain_path = os.path.join(assets_dir, "rain_sound.mp3")
        self.thunder_path = os.path.join(assets_dir, "thunder.wav")
        # Load sound
        self.streak_font_path = os.path.join(fonts_dir, "DynaPuff-Bold.ttf")
        self.unstreak_font_path = os.path.join(fonts_dir, "DynaPuff-Regular.ttf")

        self.obstacle_path = os.path.join(assets_dir, "purple note.png")
        self.hit_obstacle_path = os.path.join(assets_dir, "blue note.png")

        self.sound_manager.load_sound("hit_sound", self.sfx_path)
        self.sound_manager.load_sound("rain_sound", self.rain_path)

        #self.sound_manager.load_sound("thunder_sound")
    def set_fonts(self):
        """ Initialize game fonts """
        self.hit_state_font = pygame.font.Font(self.unstreak_font_path, 45)
        self.streak_state_font = pygame.font.Font(self.streak_font_path, 45)

    def reset_states(self):
        """ Reset game state variables """
        self.background = level2Background(self.setting.screen_width, self.setting.screen_height, self.background_path)
        self.start_time = time.time()
        self.collided = False
        self.hit = False
        self.missed = False
        self.new_text = ""
        self.last_text_time = 0
        self.last_frame_time = 0
        self.music_play_time = 0
        self.total_pause_time = 0
        self.pause = False
        self.end_game = False
    
    def reset_score(self):
        """ Initialize and reset scoring system """
        self.beats_list, self.max_score = beat_processing(self.beat_map_file_path)
        self.score = 0
        self.perfect = 0
        self.misses = 0
        self.single_score = 10
        self.long_score = 1
        self.streak = 0
        self.first_star_mark = int(self.max_score*3/10)
        self.second_star_mark = int(self.max_score*6/10)
        self.third_star_mark = int(self.max_score*9/10)
        self.first_star_check = False
        self.second_star_check = False
        self.third_star_check = False

    def on_enter(self):
        """ Prepare the game when entering the level """
        self.screen.fill("black")
        self.obstacles_group.empty()
        self.guidelines_group.empty()
        self.reset_states()
        self.reset_score()
        self.sound_manager.load_music(self.music_file_path)
        self.sound_manager.play_music(0)
        
    def on_pause(self):
        self.pause_timestamp = time.time() 
        self.sound_manager.pause_music()

    def on_resume(self):
        self.pause = False
        self.on_resume_timestamp = time.time()
        pygame.mixer.music.unpause()
        self.total_pause_time += self.on_resume_timestamp - self.pause_timestamp

    def spawn_obstacle(self, current_time):
        """ Spawn obstacles or guidelines based on beat map timing """
        for note in self.beats_list:
            if not note.spawned:
                type = note.type
                placement = note.placement
            # Calculate spawn time based on note type
                if type == "single":
                    spawn_time = note.time_start - ((self.setting.screen_width - self.setting.screen_width / 8 - self.ship_screen_width) / self.obstacle_speed)
                else:
                    spawn_time = note.time_start - ((self.setting.screen_width - self.setting.screen_width / 8 - self.ship_screen_width) / self.guideline_speed)

                # Spawn obstacle or guideline if conditions are met
                if current_time >= spawn_time:
                    y = self.setting.screen_height / 2  # Default to middle

                    if placement == 'up':
                        y = self.setting.screen_height / 2 - self.setting.screen_height / 4
                    elif placement == 'down':
                        y = self.setting.screen_height / 2 + self.setting.screen_height / 4
                    if note.type == "single":
                        # Create and add a single obstacle
                        placement = note.placement 
                        obstacle = Obstacle(
                            x=self.setting.screen_width, 
                            y=y, 
                            width=40, 
                            height=40, 
                            speed=self.obstacle_speed, 
                            note=note,
                            basic_image_path = self.obstacle_path,
                            hit_image_path = self.hit_obstacle_path,
                        )
                        self.obstacles_group.add(obstacle)
                        self.all_sprites.add(obstacle)
                    else:
                        # Create and add a guideline
                        guideline_width = int(self.guideline_speed * note.duration)
                        guideline_height = 20
                        
                        guideline = Guideline(
                            x=self.setting.screen_width,
                            guideline_y=y,
                            width=guideline_width,
                            height=guideline_height,
                            note=note
                        )
                        self.guidelines_group.add(guideline)
                        self.all_sprites.add(guideline)
                    
                    # Mark the note as spawned
                    note.spawned = True

    def update_score(self, current_time, dt):
        """ Update game score based on note timings, player actions, and streak tracking """
        
        # Handle obstacles
        for obstacle in list(self.obstacles_group):
            # Check if the player can still hit the obstacle within the grace period
            if obstacle.note.time_start - self.setting.grace_period*0.5 <= current_time <= obstacle.note.time_end + self.setting.grace_period*0.5 and not obstacle.is_hit:
                obstacle_is_correct_position = False
                if obstacle.note.placement == 'up' and self.ship.up_pressed:
                    obstacle_is_correct_position = True
                elif obstacle.note.placement == 'down' and self.ship.down_pressed:
                    obstacle_is_correct_position = True
                elif obstacle.note.placement == 'middle' and not (self.ship.down_pressed or self.ship.up_pressed):
                    obstacle_is_correct_position = True    
                if obstacle_is_correct_position and self.ship.activated:
                    self.score += self.single_score
                    obstacle.hit()
                    self.streak += 1  # Increment streak
                    self.perfect += 1
                    obstacle.note.checked = True
            # If the obstacle's time has passed and it hasn't been hit, count it as a miss
            elif current_time > obstacle.note.time_end + self.setting.grace_period*0.5 and not obstacle.is_hit:
                self.misses += 1
                self.reset_streak()  # Reset streak on miss
                obstacle.note.checked = True

        # Handle guidelines
        for guideline in list(self.guidelines_group):
            if guideline.note.time_start - self.setting.grace_period <= current_time <= guideline.note.time_end + self.setting.grace_period:
                # Determine if the player is in the correct position
                is_correct_position = False
                if guideline.note.placement == 'up' and self.ship.up_pressed:
                    is_correct_position = True
                elif guideline.note.placement == 'down' and self.ship.down_pressed:
                    is_correct_position = True
                elif guideline.note.placement == 'middle' and not (self.ship.down_pressed or self.ship.up_pressed):
                    is_correct_position = True

                # Update active state and scoring
                if is_correct_position:
                    self.ship.collided = True
                    guideline.note.active = True
                    guideline.correct_frames += dt
                    guideline.total_correct_frames += dt
                    if guideline.correct_frames >= 0.1:
                        self.score += self.long_score
                        guideline.correct_frames = 0
                          # Increment streak
                else:
                    self.ship.collided = False
                    guideline.note.active = False
                    guideline.correct_frames = 0

            if guideline.note.time_start + self.setting.grace_period <= current_time <= guideline.note.time_end - self.setting.grace_period:
                if not is_correct_position:
                    self.reset_streak()
            
            # At the end of the guideline duration, determine if it was perfect or missed
            if current_time > guideline.note.time_end and not guideline.note.checked:
                total_duration = guideline.note.time_end - guideline.note.time_start
                if guideline.total_correct_frames >= total_duration - self.grace_period*2:
                    self.perfect += 1
                    self.streak += 1

                if guideline.total_correct_frames == 0:
                    self.misses += 1
                    self.reset_streak()
          # Reset streak on miss
                guideline.note.checked = True

        # Update star checks
        if self.score >= self.first_star_mark:
            self.first_star_check = True
        if self.score >= self.second_star_mark:
            self.second_star_check = True
        if self.score >= self.third_star_mark:
            self.third_star_check = True

    def reset_streak(self):
        """ Reset the streak counter """
        if self.streak > 0:
            print(f"Streak Ended. Final Streak: {self.streak}")
        self.streak = 0
               
    def update_ships(self, dt):
        """ Handle ship movements based on key inputs """
        keys = pygame.key.get_pressed()
        self.ship.move(
            dt,
            up_pressed=keys[pygame.K_UP] or (self.detection_result["left_hand_up"] and self.detection_result["right_hand_up"]),
            down_pressed=keys[pygame.K_DOWN] or (self.detection_result["left_hand_down"] and self.detection_result["right_hand_down"]),
            activated=keys[pygame.K_SPACE] or self.detection_result["clapped"]
        )
        if self.ship.activated:
            pass
            #self.sound_manager.play_sound("hit_sound")
        self.ship.update(dt)

    def update_obstacles(self, dt):
        """ Move obstacles and remove those no longer on screen """

        for guideline in list(self.guidelines_group):
            guideline.move(self.guideline_speed, dt)
            # Remove guidelines off screen
            if guideline.rect.right < 0:
                self.all_sprites.remove(guideline)
                self.guidelines_group.remove(guideline)
        
        for obstacle in list(self.obstacles_group):
            obstacle.move(self.obstacle_speed, dt)
            # Remove obstacles off screen
            if obstacle.rect.right < 0 and obstacle.note.checked:
                self.all_sprites.remove(obstacle)
                self.obstacles_group.remove(obstacle)
        self.guidelines_group.update()
        self.obstacles_group.update(dt)

    def check_guideline_alignment(self, current_time):
        """ Check if ships are touching obstacle guidelines """
        ship = self.ship
        ship_center = ship.rect.centery
        for guideline in self.guidelines_group:    
            # Check if ship is aligned with guideline
            
            guideline_center = guideline.rect.centery
            
            # Define a tolerance range for alignment
            tolerance = 5
            placement_to_key = {
            "up": self.ship.up_pressed,
            "down": self.ship.down_pressed,
            "middle": not (self.ship.up_pressed or self.ship.down_pressed)}

            if guideline.note.placement in placement_to_key and placement_to_key[guideline.note.placement]:
                if guideline.note.time_start <= current_time <= guideline.note.time_end:
                    guideline.collided()
                else:
            # Do something if condition is true
                    guideline.align()
            else:
                guideline.unalign()

    def draw(self):
        """ Render game screen and elements """
        self.screen.fill(self.WHITE)
        self.background.draw(self.screen, 0)
        

        # Draw score line
        score_width = int(self.score_line_length * (self.score / self.max_score))
        pygame.draw.rect(self.screen, (214, 171, 245), (self.setting.screen_width/2 - self.score_line_length/2, 35, self.score_line_length, self.score_line_width), 0, 50)
        if  self.streak > 5:
            streak_color = (245, 66, 102)
            streak_text_surface = self.streak_state_font.render(f"X {self.streak}", True, streak_color)
        else:
            streak_color = (90, 45, 116)
            streak_text_surface = self.hit_state_font.render(f"x {self.streak}", True, streak_color)
        pygame.draw.rect(self.screen, streak_color, (self.setting.screen_width/2 - self.score_line_length/2, 35, score_width, self.score_line_width), 0, 50)
        self.screen.blit(streak_text_surface, (self.setting.screen_width/2 - self.score_line_length/2 - self.setting.screen_width/16, 13))
        # Draw star markers
        star_positions = [
            (self.first_star_mark, self.first_star_check),
            (self.second_star_mark, self.second_star_check),
            (self.third_star_mark, self.third_star_check)
        ]
        
        for mark, checked in star_positions:
            x_pos = self.setting.screen_width/2 - self.score_line_length/2 + int(self.score_line_length * (mark / self.max_score))
            color = (152, 56, 181) if checked else (255, 165, 0)
            pygame.draw.circle(self.screen, color, (x_pos, self.score_line_width/2 + 35), 10)

        # Draw sprites in specific groups with custom rendering if needed
        for sprite in self.guidelines_group:
            self.screen.blit(sprite.image, sprite.rect)
        
        for sprite in self.obstacles_group:
            self.screen.blit(sprite.image, sprite.rect)

        
        trailing_x = 0
        trailing_y = self.ship.rect.y + (self.ship.rect.height - self.ship.current_trailing.surface.get_height()) // 2
        self.ship.current_trailing.draw(self.screen, trailing_x, trailing_y)

        for sprite in self.all_sprites:
            if sprite not in self.guidelines_group and sprite not in self.obstacles_group:
                self.screen.blit(sprite.image, sprite.rect)

    def environment_update(self, dt):
        self.background.update(dt)

    def update(self):
        """ Main update function for each frame """
        
        current_time = time.time() - self.start_time - self.total_pause_time
        dt = current_time - self.last_frame_time
        self.spawn_obstacle(current_time)
        self.update_score(current_time, dt)
        self.environment_update(dt)
        self.update_obstacles(dt)
        self.update_ships(dt)
        self.check_guideline_alignment(current_time)
        # Update all sprites
        
        self.last_frame_time = current_time
       
    def handle_events(self, event, detection_results, lock):
        """ Handle game events and state transitions """
        self.event = event
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.pause = True
        else:
            if detection_results["cross_arm"]:
                self.pause = True
        
        self.detection_result = detection_results
        # Check for game over condition
        if self.beats_list[-1].spawned and time.time() - self.start_time -self.total_pause_time > self.beats_list[-1].time_end > 2:
            self.end_game = True
        if self.end_game:
            update_score("level_2", self.score, self.misses, self.perfect, self.first_star_check, self.second_star_check, self.third_star_check)
            return "game_over"
        if self.pause:
            self.on_pause()
            return "pause"

    def on_out(self):
        """ Cleanup method when leaving the level """
        pygame.mixer.music.stop()

if __name__ == "__main__":
    import sys
    pygame.init()
    setting = SettingsManager()
    screen = pygame.display.set_mode((setting.screen_width, setting.screen_height), vsync= 0)
    pygame.display.set_caption("ship Game")
    clock = pygame.time.Clock()
    # Initialize Gameplay
    game = Gameplaylevel2(setting, screen, clock)

    running = True
    game.on_enter()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.event = event
        game.update()
        game.draw()
        print(game.ship.activated)
        pygame.display.flip()
        clock.tick(120)
    pygame.quit()
    sys.exit()
