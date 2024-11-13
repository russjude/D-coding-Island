import pygame
import cv2
import os
from queue import Queue
from threading import Thread
import time
import subprocess
import git

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set the screen dimensions
SCREEN_WIDTH = 1539
SCREEN_HEIGHT = 940

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Credits")

class VideoPlayer:
    def __init__(self, video_path, buffer_size=100, speed_multiplier=2):
        self.cap = cv2.VideoCapture(video_path)
        self.frame_buffer = Queue(maxsize=buffer_size)
        self.current_frame = None
        self.buffer_size = buffer_size
        self.running = True
        self.speed_multiplier = speed_multiplier
        
        original_fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.target_frame_time = (1.0 / original_fps) / self.speed_multiplier
        self.last_frame_time = time.time()
        
        self.load_thread = Thread(target=self._load_frames, daemon=True)
        self.load_thread.start()
    
    def _load_frames(self):
        while self.running:
            if self.frame_buffer.qsize() < self.buffer_size:
                ret, frame = self.cap.read()
                if not ret:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                # Rotate 270 degrees (Counterclockwise)
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = pygame.surfarray.make_surface(frame)
                frame = pygame.transform.scale(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
                
                self.frame_buffer.put(frame)
            else:
                time.sleep(0.001)
    
    def get_frame(self):
        current_time = time.time()
        elapsed = current_time - self.last_frame_time
        
        if elapsed >= self.target_frame_time and not self.frame_buffer.empty():
            self.current_frame = self.frame_buffer.get()
            self.last_frame_time = current_time
            
        return self.current_frame
    
    def cleanup(self):
        self.running = False
        self.load_thread.join(timeout=1.0)
        if self.cap is not None:
            self.cap.release()

def switch_branch(branch_name):
    try:
        repo = git.Repo(os.getcwd())
        current = repo.active_branch.name
        
        if current != branch_name:
            if repo.is_dirty():
                repo.git.stash('save', f'Auto-stash before switching to {branch_name}')
            
            repo.git.checkout(branch_name)
            print(f"Successfully switched from '{current}' to '{branch_name}'")
            return True
        return True
    except git.exc.GitCommandError as e:
        print(f"Git error: {str(e)}")
        return False
    except Exception as e:
        print(f"Error switching branches: {str(e)}")
        return False

class CreditsScreen:
    def __init__(self, video_path):
        self.video_player = VideoPlayer(video_path)
        self.font = pygame.font.Font(None, 50)
        self.text = self.font.render("Press SPACE to return to the main menu", True, (255, 255, 255))
        self.text_rect = self.text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100))
    
    def run(self):
        waiting = True
        while waiting:
            current_frame = self.video_player.get_frame()
            if current_frame:
                screen.blit(current_frame, (0, 0))
                screen.blit(self.text, self.text_rect)
                pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        print("Returning to main menu...")
                        if switch_branch("main"):
                            try:
                                # Clean up properly
                                self.video_player.cleanup()
                                pygame.mixer.quit()
                                pygame.quit()
                                
                                # Launch main menu and wait for it to complete
                                subprocess.run(["python", "main.py"], check=True)
                                return False
                            except FileNotFoundError:
                                print("Could not find main.py")
                            except subprocess.CalledProcessError as e:
                                print(f"Error running main.py: {e}")
                        else:
                            print("Failed to switch to main branch")
                    elif event.key == pygame.K_ESCAPE:
                        return False

        self.video_player.cleanup()
        return True

def main():
    try:
        # Set up and load credits video
        credits_video_path = "Graphics/CREDITS.mp4"
        credits_screen = CreditsScreen(credits_video_path)
        
        # Run the credits screen
        if not credits_screen.run():
            pygame.mixer.quit()
            pygame.quit()
            return

    except Exception as e:
        print(f"Error in credits screen: {e}")
    finally:
        pygame.mixer.quit()
        pygame.quit()

if __name__ == "__main__":
    main()