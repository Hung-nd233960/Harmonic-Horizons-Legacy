import sounddevice as sd
import numpy as np
import time, os, sys
from multiprocessing import Lock

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from Settings.settings import SettingsManager

def detect_clap_from_microphone(detection_results, lock, sample_rate=48000, duration=0.1, channels=1, clap_time=0.2):
    """
    Listens to microphone input and detects claps based on the given threshold with a debounce.
    
    Args:
        threshold (int): Volume threshold for detecting a clap.
        sample_rate (int): The sample rate of the microphone input.
        duration (float): Duration (in seconds) for each check.
        channels (int): Number of channels for the microphone input (1 for mono).
        clap_time (float): Time (in seconds) to wait after a detected clap before detecting again.
    """
    setting = SettingsManager()
    threshold = setting.sound_detection_sensitivity
    # Variable to store the last time a clap was detected
    last_clap_time = 0

    def print_available_devices():
        """Prints the list of available sound devices."""
        print("Available sound devices:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            print(f"Device {i}: {device['name']} (Input channels: {device['max_input_channels']}, Output channels: {device['max_output_channels']})")

    # Function to detect a clap
    def detect_clap(indata, frames, time_info, status):
        nonlocal last_clap_time

        # Calculate the volume (RMS) of the audio data
        volume_norm = np.linalg.norm(indata) * 10
        
        # Check if the volume exceeds the threshold and if the debounce time has passed
        if volume_norm > threshold and (time.time() - last_clap_time) > clap_time:
            last_clap_time = time.time()  # Update the last clap time
            print("Clap detected! Volume:", volume_norm)
            with lock:
                detection_results["clapped"] = True
                detection_results["detection_of_sensors"] = True
        elif volume_norm < threshold and detection_results["clapped"] and (time.time() - last_clap_time) > clap_time:
            with lock:
                detection_results["clapped"] = False
                detection_results["detection_of_sensors"] = True
        
    print_available_devices()
    # Start audio input stream
    with sd.InputStream(device=6, callback=detect_clap, channels=channels, samplerate=sample_rate):
        print("Listening for claps...")
        try:
            while not detection_results["ended"]:
                time.sleep(duration)  # Continuously check for sound
        except KeyboardInterrupt:
            print("Stopped listening.")

# Example usage
if __name__ == "__main__":
    detection_results = {
        "right_hand_up": False,
        "left_hand_up": False,
        "right_hand_down": False,
        "left_hand_down": False,
        "clapped": False,
        "cross_arm": False,
        "ended": False }
    
    lock = None
    detect_clap_from_microphone(detection_results, lock)
