import pygame, sys
from multiprocessing import Manager, Process, Lock
from UI.TitleScreen import TitleScreen
from UI.LevelChooser import LevelChooserScreen
from UI.EndScreen import EndScreen
from UI.PauseScreen import PauseScreen
from DetectionSystems.hand_detection import run_hand_detection
from DetectionSystems.sound_detection import detect_clap_from_microphone
from Settings.SceneManager import SceneManager
from Settings.settings import SettingsManager
from Settings.SettingsScreen import SettingsScreen

def game_init(settings_object, detection_results, lock):
    # con = pygame.image.load("logo.png")
    # pygame.display.set_icon(icon)
    screen = pygame.display.set_mode(
        (settings_object.screen_width, settings_object.screen_height),
        pygame.FULLSCREEN if settings_object.full_screen else 0, 
        0, 
        0, 
        settings_object.vsync
    )
    pygame.display.set_caption("Harmonic Horizons")
    clock = pygame.time.Clock()
    scene_manager = SceneManager(settings_object, screen, clock)
    scene_manager.add_scene("title", TitleScreen(settings_object, screen))
    scene_manager.add_scene("settings", SettingsScreen(settings_object, screen))
    scene_manager.add_scene("level_chooser", LevelChooserScreen(settings_object, screen))
    scene_manager.add_scene("pause", PauseScreen(settings_object, screen))
    scene_manager.add_scene("game_over", EndScreen(settings_object, screen))
    # Set the initial scene
    scene_manager.change_scene("title")
    running = True
    while running:
        if settings_object.detection:  # Fixed here
            CUSTOM_EVENT = pygame.event.custom_type()
            pygame.event.post(pygame.event.Event(CUSTOM_EVENT))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                detection_results["ended"] = True
                running = False
            scene_manager.handle_events(event, detection_results, lock)
        scene_manager.update()
        scene_manager.draw()
        pygame.display.flip()
        clock.tick(settings_object.fps)  # Fixed here
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    pygame.init()
    setting = SettingsManager()
    if setting.detection:
        with Manager() as manager:
            # Create a shared dictionary correctly
            shared_dict = manager.dict({
                "detection_of_sensors": False,
                "right_hand_up": False,
                "left_hand_up": False,
                "right_hand_down": False,
                "left_hand_down": False,
                "clapped": False,
                "cross_arm": False,
                "ended": False
            })
            lock = Lock()
            # Start multiple processes that modify the shared dictionary
            processes = []
            game_process = Process(target=game_init, args=(setting, shared_dict, lock))
            hand_detection_process = Process(target=run_hand_detection, args=(shared_dict,lock))
            sound_detection_process = Process(target=detect_clap_from_microphone, args=(shared_dict,lock))

            processes.append(game_process)
            processes.append(hand_detection_process)
            processes.append(sound_detection_process)

            game_process.start()
            sound_detection_process.start()
            hand_detection_process.start()

            # Wait for all processes to complete
            for p in processes:
                p.join()
    else:
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
        game_init(setting, detection_result, None)