import pygame

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}  # For sound effects
        self.music_volume = 1.0
        self.sfx_volume = 1.0

    def load_sound(self, name, filepath):
        """Load a sound effect."""
        self.sounds[name] = pygame.mixer.Sound(filepath)

    def play_sound(self, name, volume=None):
        """Play a sound effect with optional custom volume."""
        if name in self.sounds:
            sound = self.sounds[name]
            # Use either the provided volume or the global SFX volume
            sound.set_volume(volume if volume is not None else self.sfx_volume)
            sound.play()

    def pause_music(self):
        pygame.mixer.music.pause()

    def stop_sound(self, name):
        """Stop a specific sound effect."""
        if name in self.sounds:
            self.sounds[name].stop()

    def load_music(self, filepath):
        """Load background music."""
        pygame.mixer.music.load(filepath)

    def play_music(self, loops=-1):
        """Play music (default loops infinitely)."""
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(loops)

    def stop_music(self):
        """Stop the music."""
        pygame.mixer.music.stop()

    def set_music_volume(self, volume):
        """Set the music volume (0.0 to 1.0)."""
        self.music_volume = volume
        pygame.mixer.music.set_volume(self.music_volume)

    def set_sfx_volume(self, volume):
        """Set the volume for all sound effects (0.0 to 1.0)."""
        self.sfx_volume = volume
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)

    def stop_all_sounds(self):
        """Stop all sounds and music."""
        pygame.mixer.stop()
