import pygame, random, math, os, sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)


class Cloud(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, guideline_y, orientation='right'):
        super().__init__()
        from resources.UIElements import create_rounded_cloud_surface
        # Create the obstacle surface with transparency
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)  # Ensure transparency
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Create the rounded cloud surface
        rounded_cloud = create_rounded_cloud_surface(pygame.Rect(0, 0, width, height), (63, 54, 70))

        # Blit the rounded cloud surface onto the obstacle image with transparency
        self.image.blit(rounded_cloud, (0, 0))

        self.orientation = orientation

    def move(self, speed, dt):
        direction = -1 if self.orientation == 'right' else 1
        self.rect.x += round(direction * speed * dt)

class Wave(pygame.sprite.Sprite):
    def __init__(self, amplitude, frequency, speed, offset, y_offset):
        super().__init__()
        self.amplitude = amplitude
        self.frequency = frequency
        self.speed = speed
        self.offset = offset
        self.y_offset = y_offset

    def get_points(self, time_elapsed, width):
        points = []
        for x in range(width):
            angle = self.frequency * x - time_elapsed * self.speed + self.offset
            y = int(self.y_offset + self.amplitude * math.sin(angle))
            points.append((x, y))
        return points


class Separator(pygame.sprite.Sprite):
    def __init__(self, x_pos, waves, thickness=20):
        """
        Creates a dynamic vertical line linking the topmost and bottommost waves with variable thickness.
        Args:
            x_pos (int): The x-coordinate for the vertical line.
            waves (list): List of Wave objects.
            thickness (int): The thickness of the separator line.
        """
        super().__init__()
        self.x_pos = x_pos
        self.waves = waves
        self.thickness = thickness  # Store the thickness

    def draw(self, screen, time_elapsed):
        # Calculate the topmost and bottommost points
        top_y = float('inf')  # Initialize as very high
        bottom_y = float('-inf')  # Initialize as very low

        for wave in self.waves:
            # Compute the y-position of the wave at x = self.x_pos
            angle = wave.frequency * self.x_pos - time_elapsed * wave.speed + wave.offset
            y = int(wave.y_offset + wave.amplitude * math.sin(angle))

            # Update top and bottom bounds
            top_y = min(top_y, y)
            bottom_y = max(bottom_y, y)

        # Draw the vertical line with the specified thickness
        pygame.draw.line(screen, (0, 0, 0, 150), (self.x_pos, top_y), (self.x_pos, bottom_y), self.thickness)



class BoundedImage(pygame.sprite.Sprite):
    def __init__(self, image_path, linked_wave, offset_x=70, offset_y=-210):
        """
        A class to display an image that moves according to the wave's motion.
        Args:
            image_path (str): Path to the image to display.
            linked_wave (Wave): The wave to link to for vertical movement.
            offset_x (int): Horizontal offset of the image from the wave's x position.
            offset_y (int): Vertical offset of the image from the wave's y position.
        """
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()  # Load image
        self.linked_wave = linked_wave
        self.offset_x = offset_x
        self.offset_y = offset_y

    def draw(self, screen, time_elapsed):
        # Follow the vertical motion of the linked wave
        wave_y = self.linked_wave.amplitude * math.sin(
            -time_elapsed * self.linked_wave.speed + self.linked_wave.offset
        )
        y_pos = int(self.linked_wave.y_offset + wave_y)
        screen.blit(self.image, (self.offset_x, y_pos + self.offset_y))  # Adjusted position


class MusicStaff:
    def __init__(self, width, height, wave_params, clef_image, separator_positions):
        self.width = width
        self.height = height
        self.waves = pygame.sprite.Group()
        self.separators = pygame.sprite.Group()
        self.bounded_images = pygame.sprite.Group()
        self.time_elapsed = 0

        self._initialize_waves(wave_params)
        self._initialize_separators(separator_positions)
        self._initialize_bounded_images(clef_image)

    def _initialize_waves(self, wave_params):
        for params in wave_params:
            self.waves.add(Wave(**params))

    def _initialize_separators(self, separator_positions):
        # Create separators, each linked to all waves
        for pos in separator_positions:
            self.separators.add(Separator(pos, list(self.waves), ))

    def _initialize_bounded_images(self, clef_image):
        # Create BoundedImage for the clef, linked to a middle wave
        self.bounded_images.add(BoundedImage(clef_image, list(self.waves)[2]))
    
    def update(self, dt):
        self.time_elapsed += dt

    def draw(self, screen):
        # Draw the waves
        for wave in self.waves:
            points = wave.get_points(self.time_elapsed, self.width)
            pygame.draw.lines(screen, (0, 0, 0, 150), False, points, 5)

        # Draw separators and BoundedImages (e.g., clef)
        for separator in self.separators:
            separator.draw(screen, self.time_elapsed)

        for bounded_image in self.bounded_images:
            bounded_image.draw(screen, self.time_elapsed)

def generate_bird_positions(num_birds, game_width, game_height):
    positions = []
    while len(positions) < num_birds:
        # Decide the group size using probabilities
        group_type = random.choices(
            ['single', 'pair', 'small_flock', 'large_flock'],
            weights=[20, 20, 30, 40],  # Probabilities
            k=1
        )[0]
        
        if group_type == 'single':
            group_size = 1
        elif group_type == 'pair':
            group_size = 2
        elif group_type == 'small_flock':
            group_size = random.randint(3, 5)
        elif group_type == 'large_flock':
            group_size = random.randint(6, 9)
        
        # Generate a random center for the group
        center_x = random.uniform(0, game_width)
        center_y = random.uniform(0, game_height)
        speed = random.randint(120,150)
        # Place birds in a cluster around the center
        for _ in range(group_size):
            angle = random.uniform(0, 2 * math.pi)  # Random angle
            radius = random.uniform(60, 120)  # Distance from the center
            bird_x = center_x + radius * math.cos(angle)
            bird_y = center_y + radius * math.sin(angle)
            
            # Ensure birds stay within bounds
            bird_x = max(0, min(game_width, bird_x))
            bird_y = max(0, min(game_height, bird_y))
            
            positions.append((bird_x, bird_y, speed))
            
            # Stop adding birds if we reach the total number
            if len(positions) >= num_birds:
                break
    
    return positions


def calculate_alpha(distance_to_reset, max_distance, easing=1):
        """
        Calculate the alpha value based on distance to reset using different easing functions.

        Parameters:
            distance_to_reset (float): Distance from the particle to the reset boundary.
            max_distance (float): Maximum possible distance for the particle.
            easing (str): The easing function to use. Options: "linear", "quadratic", "exponential".

        Returns:
            int: Calculated alpha value (0 to 255).
        """
        progress = distance_to_reset / max_distance  # Normalize distance to a 0-1 range

        alpha = 255

        return max(0, min(255, int(alpha)))  # Ensure alpha is in the valid range


class Particles(pygame.sprite.Sprite):
    def __init__(self, x, y, move_direction, speed = 400, radius=1, left_wall=0, right_wall=800, shape="circle"):
        super().__init__()
        self.shape = shape
        size = radius * 2 if shape != "pixel" else 1  # Pixel size is always 1x1
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)  # Surface with transparency
        self.image.fill((0, 0, 0, 0))  # Transparent fill

        # Generate random rainbow color
        self.color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )
        
        # Draw the specified shape
        if shape == "circle":
            pygame.draw.circle(self.image, self.color, (radius, radius), radius)
        elif shape == "square":
            pygame.draw.rect(self.image, self.color, (0, 0, size, size))
        elif shape == "pixel":
            self.image.fill(self.color)  # A single pixel is just a filled Surface

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)  # Position the particle
        self.speed = 400  # Pixels per second
        self.move_direction = move_direction
        self.left_wall = left_wall
        self.right_wall = right_wall

        # Random diffusion parameters
        self.diffuse_range = 5  # Maximum pixel offset for diffusion
        self.diffuse_probability = 0.3  # Probability of diffusing at each frame

    def update(self, dt):
        # Main movement along the x-axis
        self.rect.x += self.move_direction * round(self.speed * dt)
        
        # Diffusing motion
        if random.random() < self.diffuse_probability:  # Add randomness to simulate diffusion
            dx = 0
            dx = random.randint(0, self.diffuse_range)
            dy = random.randint(-self.diffuse_range, self.diffuse_range)
            self.rect.x += dx
            self.rect.y += dy

        # Reset when reaching walls
        if self.rect.x < self.left_wall:
            self.rect.x = self.right_wall
        elif self.rect.x > self.right_wall:
            self.rect.x = self.left_wall

        # Keep particles within vertical screen bounds
        self.rect.y = max(0, min(self.rect.y, pygame.display.get_surface().get_height()))


class Trailing(pygame.sprite.Group):
    def __init__(self, height, width, speed = 400, left_wall=0, right_wall=800, num_particles=50, move_direction=1, shape="circle"):
        super().__init__()
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.height = height
        self.width = width
        self.left_wall = left_wall
        self.right_wall = right_wall
        self.num_particles = num_particles
        self.move_direction = move_direction
        self.shape = shape
        self.speed = speed
        self.particles = self._create_particles()
        
    def _create_particles(self):
        particles = []
        for _ in range(self.num_particles):
            x = random.randint(self.left_wall, self.right_wall)
            y = random.randint(0, self.height)
            radius = random.randint(4, 7)  # Random radius
            particle = Particles(x, y, self.move_direction, self.speed, radius, self.left_wall, self.right_wall, shape=self.shape)
            particles.append(particle)
            self.add(particle)
        return particles

    def update(self, dt, alpha_easing=0.5):
        for particle in self.sprites():
            # Calculate distance to reset wall
            if self.move_direction > 0:  # Moving right
                distance_to_reset = self.right_wall - particle.rect.x
            else:  # Moving left
                distance_to_reset = particle.rect.x - self.left_wall

            max_distance = self.width

            # Use the alpha calculation function
            alpha = calculate_alpha(distance_to_reset, max_distance, easing=alpha_easing)
            particle.image.set_alpha(alpha)

            particle.update(dt)

    def draw(self, screen, x, y):
        self.surface.fill((0, 0, 0, 0))  # Clear the surface with transparency
        super().draw(self.surface)
        screen.blit(self.surface, (x, y))  # Draw the trailing surface on the main screen

class Raindrop(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, length):
        super().__init__()
        self.speed = speed
        self.length = length
        self.rain_color = (135, 206, 250)
        
        # Create the image surface
        self.image = pygame.Surface((2, length), pygame.SRCALPHA)  # Transparent surface
        pygame.draw.line(self.image, self.rain_color, (0, 0), (0, self.length), 2)
        
        # Set up rect for position tracking
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self, screen_height, dt):
        """Update the position of the raindrop."""
        self.rect.y += self.speed * dt  # Update the position using the rect
        if self.rect.y > screen_height:  # Reset if out of bounds
            self.rect.y = -self.length  # Reset above the screen

class Snow(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, length):
        super().__init__()
        self.speed = speed
        self.length = length
        self.snow_color = (255,255,255)
        
        # Create the image surface
        self.image = pygame.Surface((length, length), pygame.SRCALPHA)  # Transparent surface
        pygame.draw.line(self.image, self.snow_color, (self.length//2, 0), (self.length//2, self.length), 1)
        pygame.draw.line(self.image, self.snow_color, (0, self.length//2), (self.length, self.length//2), 1)
        
        # Set up rect for position tracking
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self, screen_height, dt):
        """Update the position of the raindrop."""
        self.rect.y += round(self.speed * dt)  # Update the position using the rect
        if self.rect.y > screen_height:  # Reset if out of bounds
            self.rect.y = -self.length  # Reset above the screen

class Stars(pygame.sprite.Sprite):
    def __init__(self, x, y, move_direction, radius=1):
        super().__init__()
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)  # Surface with transparency
        self.image.fill((0, 0, 0, 0))  # Transparent fill
        pygame.draw.circle(self.image, (255, 255, 255), (radius, radius), radius)  # Draw a white circle (star)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)  # Position the star at the specified coordinates
        self.speed = random.randint(1,3)
        self.move_direction = move_direction
        
    def update(self, screen_width, dt):
        self.rect.x += self.move_direction * math.ceil(self.speed * dt)
        
        # Keep stars within bounds (reset to the other side)
        if self.rect.x < 0:
            self.rect.x = screen_width  # Reset to the right side
        elif self.rect.x > screen_width:
            self.rect.x = 0  # Reset to the left side