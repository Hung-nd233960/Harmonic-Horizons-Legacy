import pygame
import colorsys
import math
import random, datetime, json
from Settings.settings import SettingsManager
from resources.environment import Raindrop, Snow, Stars
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Gradient colors
NORMAL_TOP = (255, 180, 250)
NORMAL_BOTTOM = (250, 60, 235)
HOVER_TOP = (250, 90, 223)
HOVER_BOTTOM = (200, 90, 250)

hover_border_color = (62, 66, 189)
hover_text_color = 'white'
unhover_text_color = (62, 66, 189)
normal_border_color = (0,0,0,0)
# Initialize Pygame

# Screen dimensions

BLUE = (135, 206, 250)
def create_rounded_cloud_surface(rect, corner_radius=30, cloud_color = (255, 255, 255)):
    # Create an empty surface to draw the cloud on with transparency
    cloud_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    # Define the number of points (random count between 8 and 14)
    if rect.width > 1500:
        points_count = random.randint(20, 30)
    elif rect.width > 1000:
        points_count = random.randint(10, 24)
    elif rect.width > 500:
        points_count = random.randint(7, 15)
    else:
        points_count = random.randint(3, 7)
    step_x = rect.width / (points_count - 1)  # Step size to divide width into points
    
    # Loop over the points (excluding the first and last)
    x = -2 * step_x
    for i in range(0, points_count + 2):
        # Calculate the x position for this point
        x += step_x
        
        # Randomize the width of the ellipse between 0.3 and 0.5 of the Rect's width
        ellipse_width = round(random.randint(25, 40) * step_x / 10)
        
        # The height of the ellipse is 2 * the height of the Rect
        ellipse_height = round(random.randint(20, 45) * rect.height / 10)
        
        # Draw the ellipse on the cloud surface (ensuring no black outline)
        pygame.draw.ellipse(cloud_surface, cloud_color, (x, 0, ellipse_width, ellipse_height))
    
    # Create a new surface to hold the rounded rectangle and the cloud
    rounded_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    
    # Create a mask for the rounded corners
    mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))  # Transparent surface for mask
    
    # Draw the rounded rectangle on the mask
    pygame.draw.rect(mask, (255, 255, 255), (0, 0, rect.width, rect.height), border_radius=corner_radius)
    
    # Use the mask to clip the cloud surface onto the rounded surface
    rounded_surface.blit(cloud_surface, (0, 0))
    rounded_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    
    return rounded_surface


class LightningFlash:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.flash_alpha = 0
        self.flash_speed = 5  # How fast the flash fades
        self.flash_intensities = [255, 200, 150, 100, 50]
        
    def trigger_flash(self):
        """Manually triggers a lightning flash"""
        self.flash_alpha = random.choice(self.flash_intensities)
    
    def update(self):
        """Update the flash effect to fade out"""
        if self.flash_alpha > 0:
            self.flash_alpha -= self.flash_speed
    
    def draw(self, screen):
        """Draw the lightning flash on the screen"""
        if self.flash_alpha > 0:
            flash_surface = pygame.Surface((self.screen_width, self.screen_height))
            flash_surface.fill((255, 255, 255))  # White flash
            flash_surface.set_alpha(self.flash_alpha)
            screen.blit(flash_surface, (0, 0))

class ScreenDimming:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.dim_alpha = 0
        self.dim_direction = 1  # 1 to dim, -1 to brighten
        self.dim_speed = 3  # Speed of dimming/brightening

    def update(self):
        """Update the dimming effect"""
        self.dim_alpha += self.dim_speed * self.dim_direction
        if self.dim_alpha >= 200:  # Max darkness
            self.dim_direction = -1  # Reverse to brighten
        elif self.dim_alpha <= 0:  # Fully transparent
            self.dim_direction = 1  # Reverse to dim again

    def draw(self, screen):
        """Draw the dimming effect on the screen"""
        dim_surface = pygame.Surface((self.screen_width, self.screen_height))
        dim_surface.fill((0, 0, 0))  # Black dim
        dim_surface.set_alpha(self.dim_alpha)
        screen.blit(dim_surface, (0, 0))



def create_moon_surfaces(radius, crater_count, blocking_factor, blocking_offset):
    """
    Create full moon and half moon surfaces.

    :param radius: Radius of the moon.
    :param crater_count: Number of random black pixels to simulate craters.
    :param blocking_offset: Offset of the transparent circle for half moon.
    :return: Dictionary with "full moon" and "half moon" surfaces.
    """
    surface_size = radius * 2
    white = (255, 255, 255)
    black = (0, 0, 0)
    transparent = (0, 0, 0, 0)

    # Create full moon surface
    full_moon_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
    full_moon_surface.fill(transparent)
    pygame.draw.circle(full_moon_surface, white, (radius, radius), radius)

    # Add random black pixels to simulate craters
    for _ in range(crater_count):
        rand_x = random.randint(0, surface_size - 1)
        rand_y = random.randint(0, surface_size - 1)
        if (rand_x - radius) ** 2 + (rand_y - radius) ** 2 <= radius ** 2:
            full_moon_surface.set_at((rand_x, rand_y), black)

    # Create half moon surface
    half_moon_surface = full_moon_surface.copy()
    mask_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
    mask_surface.fill(transparent)

    blocking_radius = radius * blocking_factor/10
    pygame.draw.circle(mask_surface, black, 
                       (int(radius + blocking_offset), radius), 
                       int(blocking_radius))
    half_moon_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    return {
        "full moon": full_moon_surface,
        "half moon": half_moon_surface
    }

def create_horizontal_gradient_surface(rect, top_color, bottom_color, border_radius = 0 ):
    """
    Create a high-quality vertical gradient surface with rounded corners.
    
    Args:
        rect (pygame.Rect): The dimensions of the surface (width, height).
        top_color (tuple): The RGB color at the top of the gradient.
        bottom_color (tuple): The RGB color at the bottom of the gradient.
        border_radius (int): The border radius for rounded corners.

    Returns:
        pygame.Surface: A surface with the gradient and rounded corners applied.
    """
    # Scale up for subpixel blending
    upscale_factor = 4  # Draw at 4x resolution for smoother gradient
    gradient_height = rect.height * upscale_factor
    gradient_surface = pygame.Surface((rect.width, gradient_height), pygame.SRCALPHA)

    for i in range(gradient_height):
        # Calculate normalized position (0.0 to 1.0)
        factor = i / gradient_height

        # Gamma correction for perceptual smoothing
        corrected_factor = math.pow(factor, 2.2)  # Gamma = 2.2 for perceptual linearity

        # Interpolate colors with gamma correction
        current_color = (
            int(top_color[0] + (bottom_color[0] - top_color[0]) * corrected_factor),
            int(top_color[1] + (bottom_color[1] - top_color[1]) * corrected_factor),
            int(top_color[2] + (bottom_color[2] - top_color[2]) * corrected_factor),
            255  # Alpha channel
        )

        # Draw a single line for the current gradient step
        pygame.draw.line(gradient_surface, current_color, (0, i), (rect.width, i))

    # Downscale to original size for smoother appearance
    gradient_surface = pygame.transform.smoothscale(gradient_surface, (rect.width, rect.height))

    # Create a rounded mask
    mask_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(mask_surface, (255, 255, 255, 255), 
                     (0, 0, rect.width, rect.height), 
                     border_radius=border_radius)

    # Apply the rounded mask to the gradient surface
    gradient_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    return gradient_surface


def create_smooth_rainbow_gradient(rect, border_radius = 0):
    """
    Create a smooth rainbow gradient with rounded corners.

    Args:
        rect (pygame.Rect): The dimensions of the surface (width, height).
        border_radius (int): The border radius for rounded corners.

    Returns:
        pygame.Surface: A surface with the rainbow gradient and rounded corners applied.
    """
    gradient_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

    for i in range(rect.height):
        # Calculate the normalized position (0.0 to 1.0)
        factor = 1 - (i / rect.height)

        # Generate the color in the rainbow (Hue: 0 to 1, Saturation: 1, Lightness: 0.5)
        hue = factor  # Hue cycles from 0 (red) to 1 (back to red via rainbow colors)
        r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)  # Full saturation and brightness
        current_color = (int(r * 255), int(g * 255), int(b * 255))

        # Draw the current line
        pygame.draw.line(gradient_surface, current_color, (0, i), (rect.width, i))

    # Create a rounded mask
    mask_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(mask_surface, (255, 255, 255, 255), 
                     (0, 0, rect.width, rect.height), 
                     border_radius=border_radius)

    # Apply the rounded mask to the gradient surface
    gradient_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    return gradient_surface

def create_vertical_gradient_surface(rect, top_color, bottom_color, border_radius=0):
    """
    Create a high-quality vertical gradient surface with rounded corners.
    
    Args:
        rect (pygame.Rect): The dimensions of the surface (width, height).
        top_color (tuple): The RGB color at the top of the gradient.
        bottom_color (tuple): The RGB color at the bottom of the gradient.
        border_radius (int): The border radius for rounded corners.

    Returns:
        pygame.Surface: A surface with the gradient and rounded corners applied.
    """
    # Create a surface for the gradient with transparency
    gradient_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

    # Loop through each pixel row to create the gradient
    for y in range(rect.height):
        # Interpolation factor for the gradient (normalized)
        factor = y / rect.height

        # Interpolate colors
        current_color = (
            int(top_color[0] + (bottom_color[0] - top_color[0]) * factor),
            int(top_color[1] + (bottom_color[1] - top_color[1]) * factor),
            int(top_color[2] + (bottom_color[2] - top_color[2]) * factor),
            255  # Full alpha channel
        )

        # Draw a horizontal line at the current row
        pygame.draw.line(gradient_surface, current_color, (0, y), (rect.width, y))

    # Create a mask for rounded corners if needed
    if border_radius > 0:
        # Create a surface to serve as a mask
        mask_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        # Draw a rounded rectangle on the mask
        pygame.draw.rect(
            mask_surface, (255, 255, 255, 255),
            (0, 0, rect.width, rect.height),
            border_radius=border_radius
        )
        # Apply the mask to the gradient surface
        gradient_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    return gradient_surface

class Button:
    def __init__(self, x, y, width, height, text, border_radius):
        self.base_rect = pygame.Rect(x, y, width, height)  # Original dimensions
        self.rect = self.base_rect.copy()  # Current pulsating dimensions
        self.text = text
        self.border_radius = border_radius
        self.is_hovered = False
        self.pulse_time = 0  # Time tracker for the pulse animation

        # Predefine gradient surfaces for normal and hover states
        self.normal_gradient_surface = create_horizontal_gradient_surface(
            self.base_rect, NORMAL_TOP, NORMAL_BOTTOM, border_radius
        )
        self.hover_gradient_surface = create_horizontal_gradient_surface(
            self.base_rect, HOVER_TOP, HOVER_BOTTOM, border_radius
        )

    def update(self, delta_time):
        """
        Update the button's state, including hover detection and animations.

        Args:
            delta_time (float): Time elapsed since the last frame (in seconds).
        """
        
        if self.is_hovered:
            # Increment pulse time for animation
            self.pulse_time += delta_time
            # Calculate scaling factor for pulsation
            scale_factor = 1 + 0.05 * math.sin(self.pulse_time * 4)
            # Adjust the rect size based on the scale factor
            new_width = int(self.base_rect.width * scale_factor)
            new_height = int(self.base_rect.height * scale_factor)
            self.rect = pygame.Rect(
                self.base_rect.centerx - new_width // 2,
                self.base_rect.centery - new_height // 2,
                new_width,
                new_height
            )
        else:
            # Reset to base size and reset pulse time
            self.rect = self.base_rect.copy()
            self.pulse_time = 0

    def draw(self, screen, font):
        """
        Draw the button on the screen.

        Args:
            screen (pygame.Surface): The surface to draw on.
            font (pygame.font.Font): The font used to render the button text.
        """
        # Choose the correct gradient surface
        if self.is_hovered:
            gradient_surface = pygame.transform.smoothscale(
                self.hover_gradient_surface, (self.rect.width, self.rect.height)
            )
            border_color = hover_border_color
            text_color = hover_text_color
        else:
            gradient_surface = pygame.transform.smoothscale(
                self.normal_gradient_surface, (self.rect.width, self.rect.height)
            )
            border_color = normal_border_color
            text_color = unhover_text_color

        # Draw the gradient surface
        screen.blit(gradient_surface, self.rect.topleft)

        # Draw the border
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=self.border_radius)

        # Draw the text
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class Background(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height, state_of_time, weather = None, bottom_gradient = None, top_gradient = None):
        super().__init__()
        self.width = screen_width
        self.height = screen_height  # Half the screen height
        self.image = pygame.Surface((self.width, self.height))
        self.state_of_time = state_of_time
        self.weather = weather
        if state_of_time == "custom":
            bottom_color = bottom_gradient
            top_color = top_gradient
        elif state_of_time == 'night':
            bottom_color = (89,0,152)
            top_color = (7,0,88)
            self.moon_surface = random.choice(list(create_moon_surfaces(random.randint(70, 90),random.randint(70, 90), 8, random.randint(30, 50)).values()))
        else:
            top_color = (220,240,250)
            bottom_color = (185,226,245)
        self.image.blit(create_horizontal_gradient_surface(self.image.get_rect(),top_color,bottom_color))
        # Create stars randomly in the background
        self.stars_group = pygame.sprite.Group()
        self.rain_group = pygame.sprite.Group()
        self.snow_group = pygame.sprite.Group()
        if state_of_time == 'night':
            self.direction = -1
            self.create_stars()
        if weather == "rain":
            self.create_raindrops(300)
        if weather == "snow":
            self.create_snow(300)

    def create_raindrops(self, num_drops = 200):
        """Generate a list of raindrops."""
        for _ in range(num_drops):
            x = random.randint(0, self.width)
            y = random.randint(-self.height, 0)
            speed = random.uniform(800, 825)  # Pixels per second
            length = random.randint(5, 15)   # Length of the raindrop
            raindrop = Raindrop(x, y, speed, length)
            self.rain_group.add(raindrop)

    def create_snow(self, num_drops = 500):
        """Generate a list of raindrops."""
        for _ in range(num_drops):
            x = random.randint(0, self.width)
            y = random.randint(-self.height, self.height)
            speed = random.uniform(200, 250)  # Pixels per second
            length = random.choice([2,4,6])   # Length of the raindrop
            snowdrop = Snow(x, y, speed, length)
            self.snow_group.add(snowdrop)
    
    def create_stars(self, num_stars=100):
        """Create random stars (circles) inside the background."""
        for _ in range(num_stars):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            star = Stars(x, y, self.direction)
            self.stars_group.add(star)
        
    def update(self, dt):
        """Update the stars if needed (e.g., for movement or animation)."""
        self.stars_group.update(self.width, dt)
        self.rain_group.update(self.height, dt)
        self.snow_group.update(self.height, dt)

    def draw(self, surface, y_pos):
        """Draw the background and the stars to the given surface."""
        background_surface = pygame.Surface((self.width, self.height))
        background_surface.blit(self.image)
        if self.state_of_time == 'night':
            background_surface.blit(self.moon_surface, (150,50))
        if self.weather == 'rain':
            self.rain_group.draw(background_surface)
        elif self.weather == 'snow':
            self.snow_group.draw(background_surface)
        elif self.weather == "star":
            self.stars_group.draw(background_surface)
            
        surface.blit(background_surface, (0, y_pos))
         

# Planet class definition

class LevelBlock:
    animation_speed = 1.2
    def __init__(self, text, x, y, default_width, default_height, selected_width, selected_height, offset, border_radius = 80):
        self.text = text
        self.x = x
        self.y = y
        self.default_x = x
        self.default_y = y
        self.width = default_width
        self.height = default_height
        self.default_width = default_width
        self.default_height = default_height
        self.target_width = default_width
        self.target_height = default_height
        self.offset_x = 0
        self.target_offset_x = 0
        self.animation_progress = 0
        self.animating = False  # True when animating
        self.selected = False
        self.selected_width = selected_width
        self.selected_height = selected_height
        self.offset = offset
        self.border_radius = border_radius
        
        # Precompute gradient surfaces
        self.base_rect = pygame.Rect(0, 0, self.width, self.height)
        self.normal_gradient_surface = create_horizontal_gradient_surface(
            self.base_rect, NORMAL_TOP, NORMAL_BOTTOM, border_radius
        )
        self.selected_gradient_surface = create_horizontal_gradient_surface(
            self.base_rect, HOVER_TOP, HOVER_BOTTOM, border_radius
        )

    def update(self, dt):
        """Update the animation based on target properties."""
        
        if self.animating:
            self.animation_progress += LevelBlock.animation_speed*dt
            if self.animation_progress >= 1:
                self.animation_progress = 1
                self.animating = False

            t = self.ease_in_out(self.animation_progress)
            # Interpolate width, height, and offset_x
            self.width = self.default_width + t * (self.target_width - self.default_width)
            self.height = self.default_height + t * (self.target_height - self.default_height)
            self.offset_x = t * self.target_offset_x
            
            # Update the base rect for gradient surface
            self.base_rect = pygame.Rect(0, 0, self.width, self.height)

    def select(self):
        """Select the block and animate it."""
        self.selected = True
        self.target_width = self.selected_width
        self.target_height = self.selected_height
        self.target_offset_x = self.offset
        self.animation_progress = 0
        self.animating = True

    def unselect(self):
        """Unselect the block and animate it back to normal."""
        self.selected = False
        self.target_width = self.default_width
        self.target_height = self.default_height
        self.target_offset_x = 0
        self.animation_progress = 0
        self.animating = True

    def draw(self, screen, font):
        """Draw the block with different gradients based on selection state."""
        # Calculate the current rect
        rect = pygame.Rect(self.x + self.offset_x, self.y, self.width, self.height)
        
        # Choose the appropriate gradient surface
        current_gradient_surface = (self.selected_gradient_surface if self.selected 
                                    else self.normal_gradient_surface)
        if self.selected:
            current_gradient_surface = self.selected_gradient_surface
            border_color = hover_border_color
            text_color = hover_text_color
        else:
            current_gradient_surface = self.normal_gradient_surface
            border_color = normal_border_color
            text_color = unhover_text_color
        # Scale the gradient surface to match the current rect size
        scaled_gradient = pygame.transform.scale(current_gradient_surface, (int(self.width), int(self.height)))
        
        # Blit the scaled gradient surface
        screen.blit(scaled_gradient, rect)
        
        # Draw the level number
        text = font.render(self.text, True, text_color)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

    @staticmethod
    def ease_in_out(t):
        """Ease-in-out function for smooth transitions."""
        return t * t * (3 - 2 * t)


class Scoreboard:
    animation_speed = 1
    def __init__(self, width, height, font, stat_font):
        self.width = width
        self.height = height
        self.font = font
        self.stat_font = stat_font
        self.animating = False
        # Data for High Score and Latest Attempt

        # Create the scoreboard surface
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0))  # Transparent background

    def update(self, dt):
        if self.animating:
            self.animation_progress += Scoreboard.animation_speed*dt
            if self.animation_progress >= 1:
                self.animation_progress = 1
                self.animating = False
            t = self.ease_in_out(self.animation_progress)
            # Interpolate width, height, and offset_x
            self.width = self.default_width + t * (self.target_width - self.default_width)
            self.height = self.default_height + t * (self.target_height - self.default_height)
            self.offset_x = t * self.target_offset_x
            
    def draw_section(self, title, data, y_start, section_height):
        # Draw section title
        title_text = self.font.render(title, True, (191, 50, 156))
        title_rect = title_text.get_rect(center=(self.width // 2, y_start + 40))
        self.surface.blit(title_text, title_rect)

        # Draw stars
        star_y = y_start + round(section_height / 3.15)
        star_radius = 25
        star_gap = 30
        num_stars = 3
        total_star_width = (num_stars * 2 * star_radius) + ((num_stars - 1) * star_gap)
        start_x = (self.width - total_star_width) // 2

        for i in range(num_stars):
            pos = (start_x + (2*i+1)*star_radius + i*star_gap, star_y)
            color = (232, 70, 113) if i < data["stars"] else (200, 200, 200)
            pygame.draw.circle(self.surface, color, pos, star_radius)
            pygame.draw.circle(self.surface, 'purple', pos, star_radius, 2)

        # Draw stats
        stats = [("Perfect", 'purple', data["perfect"]), ("Missed", 'orange', data["misses"])]
        for i, (label, color, value) in enumerate(stats):
            stat_label = self.stat_font.render(label, True, color)
            stat_label_rect = stat_label.get_rect(center=(150, y_start + section_height // 2 + i * 40))
            self.surface.blit(stat_label, stat_label_rect)

            stat_value = self.stat_font.render(str(value), True, color)
            stat_value_rect = stat_value.get_rect(center=(self.width - 150, y_start + section_height // 2 + i * 40))
            self.surface.blit(stat_value, stat_value_rect)

        # Draw timestamp
        timestamp_text = self.stat_font.render(f"Date: {data['timestamp']}", True, (100, 100, 100))
        timestamp_rect = timestamp_text.get_rect(center=(self.width // 2, y_start + section_height - 40))
        self.surface.blit(timestamp_text, timestamp_rect)

    def draw(self):
        # Clear the surface
        self.surface.fill((252, 242, 247, 255))  # Light pink background
        pygame.draw.rect(self.surface, 'purple', (0, 0, self.width, self.height), 5, 50)  # Border with rounded edges

        # Draw dividing line
        mid_y = self.height // 2
        pygame.draw.line(self.surface, 'purple', (0, mid_y), (self.width, mid_y), 5)

        # Draw High Score section
        self.draw_section("High Score", self.high_score_data, 0, self.height // 2)

        # Draw Latest Attempt section
        self.draw_section("Latest Attempt", self.latest_attempt_data, self.height // 2, self.height // 2)

        mask_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(mask_surface, (255, 255, 255, 255), 
                     (0, 0, self.width, self.height), 
                     border_radius=50)

    # Apply the rounded mask to the gradient surface
        self.surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        return self.surface
    def ease_in_out(t):
        """Ease-in-out function for smooth transitions."""
        return t * t * (3 - 2 * t)

