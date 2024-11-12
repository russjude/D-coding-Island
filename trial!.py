import pygame
from pygame.locals import *
from pygame import mixer
import os
import time
import sys
import random
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Game with Minigames')

# Load images and sounds
try:
    bg_image = pygame.image.load('background.png').convert()
    bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    player_image = pygame.image.load('player.png').convert_alpha()
    player_image = pygame.transform.scale(player_image, (30, 30))
    goal_image = pygame.image.load('goal.png').convert_alpha()
    goal_image = pygame.transform.scale(goal_image, (40, 40))
    
    jump_sound = pygame.mixer.Sound('jump.wav')
    collect_sound = pygame.mixer.Sound('collect.wav')
    win_sound = pygame.mixer.Sound('win.wav')
except:
    print("Warning: Some assets failed to load. Using default shapes.")
    bg_image = None
    player_image = None
    goal_image = None
    jump_sound = None
    collect_sound = None
    win_sound = None

class MinigameManager:
    def __init__(self):
        self.current_level = 0
        self.minigame_required = False
        self.transition_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.transition_overlay.fill(BLACK)
        self.transition_alpha = 0
        self.transitioning = False
        self.transition_speed = 5
        
    def load_minigame(self, level):
        """Load and run a minigame module when needed"""
        try:
            # Fade out current game
            self.fade_transition(out=True)
            
            # Store current display settings
            current_display = pygame.display.get_surface().copy()
            
            # Map levels to their corresponding minigame modules
            minigame_modules = {
                1: 'mini_game1',
                2: 'mini_game2',
                3: 'mini_game3',
                4: 'mini_game4',
                5: 'mini_game5'
            }
            
            if level not in minigame_modules:
                return True
                
            # Import and run minigame
            try:
                minigame = __import__(minigame_modules[level])
                
                # Fade in minigame
                self.fade_transition(out=False)
                
                result = minigame.main()
                
                # Fade out minigame
                self.fade_transition(out=True)
                
            except ImportError as e:
                print(f"Could not load minigame {level}: {e}")
                return False
            except Exception as e:
                print(f"Error running minigame {level}: {e}")
                return False
            
            # Reset display
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption('Game with Minigames')
            
            # Fade back to main game
            self.fade_transition(out=False)
            
            if not result:
                self.show_retry_message()
                return self.load_minigame(level)
                
            return result
            
        except Exception as e:
            print(f"Error in load_minigame: {e}")
            return False
    
    def fade_transition(self, out=True):
        """Handle fade transitions"""
        if out:
            alpha = 0
            while alpha < 255:
                self.transition_overlay.set_alpha(alpha)
                screen.blit(self.transition_overlay, (0, 0))
                pygame.display.flip()
                alpha += self.transition_speed
                pygame.time.wait(5)
        else:
            alpha = 255
            while alpha > 0:
                self.transition_overlay.set_alpha(alpha)
                screen.blit(self.transition_overlay, (0, 0))
                pygame.display.flip()
                alpha -= self.transition_speed
                pygame.time.wait(5)
            
    def show_retry_message(self):
        """Show message when minigame needs to be retried"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 36)
        text1 = font.render("You must complete the minigame to proceed!", True, WHITE)
        text2 = font.render("Press any key to try again...", True, WHITE)
        
        text1_rect = text1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
        text2_rect = text2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        
        screen.blit(text1, text1_rect)
        screen.blit(text2, text2_rect)
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False
            pygame.time.wait(100)
    
    def check_and_run_minigame(self, level):
        """Check if minigame should be run and handle it"""
        if level in [1, 2, 3, 4, 5] and self.minigame_required:
            result = self.load_minigame(level)
            self.minigame_required = False
            return result
        return True

class LevelManager:
    def __init__(self):
        self.current_level = 0
        self.max_level = 5
        self.level_completed = False
        self.level_data = {
            0: {
                'platforms': [(0, SCREEN_HEIGHT-40, SCREEN_WIDTH, 40)],
                'collectibles': [(100, SCREEN_HEIGHT-80), (300, SCREEN_HEIGHT-80), (500, SCREEN_HEIGHT-80)],
                'enemies': [(200, SCREEN_HEIGHT-60, 100), (400, SCREEN_HEIGHT-60, 100)],
                'goal': (SCREEN_WIDTH-60, SCREEN_HEIGHT-80)
            },
            # Add more level data here for levels 1-5
        }
        self.collectibles_required = {
            0: 3,
            1: 4,
            2: 5,
            3: 6,
            4: 7,
            5: 8
        }
    
    def load_level(self, level):
        """Load level data"""
        if level in self.level_data:
            return self.level_data[level]
        return None
    
    def next_level(self):
        """Progress to next level if available"""
        if self.current_level < self.max_level:
            self.current_level += 1
            self.level_completed = False
            return True
        return False
        
    def reset_level(self):
        """Reset current level"""
        self.level_completed = False
        return True

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = player_image if player_image else pygame.Surface((30, 30))
        if not player_image:
            self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump_power = -15
        self.gravity = 0.8
        self.jumping = False
        self.health = 100
        self.collectibles = 0
        self.invulnerable = False
        self.invulnerable_timer = 0
        
    def update(self, platforms):
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -self.speed
        if keys[pygame.K_RIGHT]:
            self.vel_x = self.speed
        
        # Jumping
        if keys[pygame.K_SPACE] and not self.jumping:
            self.vel_y = self.jump_power
            self.jumping = True
            if jump_sound:
                jump_sound.play()
        
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 10:
            self.vel_y = 10
            
        # Update position with collision checks
        self.rect.x += self.vel_x
        self.handle_collision(platforms, 'horizontal')
        
        self.rect.y += self.vel_y
        self.handle_collision(platforms, 'vertical')
        
        # Handle invulnerability
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
        
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0
            self.jumping = False
    
    def handle_collision(self, platforms, direction):
        """Handle collisions with platforms"""
        for platform in platforms:
            if self.rect.colliderect(platform):
                if direction == 'horizontal':
                    if self.vel_x > 0:
                        self.rect.right = platform.left
                    elif self.vel_x < 0:
                        self.rect.left = platform.right
                else:
                    if self.vel_y > 0:
                        self.rect.bottom = platform.top
                        self.vel_y = 0
                        self.jumping = False
                    elif self.vel_y < 0:
                        self.rect.top = platform.bottom
                        self.vel_y = 0
    
    def take_damage(self, amount):
        """Handle player taking damage"""
        if not self.invulnerable:
            self.health -= amount
            self.invulnerable = True
            self.invulnerable_timer = 60  # 1 second at 60 FPS
            return True
        return False

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_distance):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.start_x = x
        self.patrol_distance = patrol_distance
        self.speed = 2
        self.direction = 1
    
    def update(self):
        self.rect.x += self.speed * self.direction
        
        if abs(self.rect.x - self.start_x) > self.patrol_distance:
            self.direction *= -1

class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.bob_offset = 0
        self.bob_speed = 0.1
        self.original_y = y
    
    def update(self):
        # Simple floating animation
        self.bob_offset += self.bob_speed
        self.rect.y = self.original_y + math.sin(self.bob_offset) * 5

class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "playing"  # "playing", "paused", "game_over", "victory"
        self.level_manager = LevelManager()
        self.minigame_manager = MinigameManager()
        
        # Initialize sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()
        
        self.player = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT-100)
        self.all_sprites.add(self.player)
        
        self.load_current_level()
        
        # UI elements
        self.font = pygame.font.Font(None, 36)
        
    def load_current_level(self):
        """Load the current level data"""
        level_data = self.level_manager.load_level(self.level_manager.current_level)
        if level_data:
            # Clear existing sprites
            self.platforms.empty()
            self.enemies.empty()
            self.collectibles.empty()
            
            # Create platforms
            for plat in level_data['platforms']:
                platform = pygame.sprite.Sprite()
                platform.image = pygame.Surface((plat[2], plat[3]))
                platform.image.fill(GREEN)
                platform.rect = platform.image.get_rect()
                platform.rect.x = plat[0]
                platform.rect.y = plat[1]
                self.platforms.add(platform)
            
            # Create enemies
            for enemy in level_data['enemies']:
                new_enemy = Enemy(enemy[0], enemy[1], enemy[2])
                self.enemies.add(new_enemy)
                self.all_sprites.add(new_enemy)
            
            # Create collectibles
            for collect in level_data['collectibles']:
                new_collectible = Collectible(collect[0], collect[1])
                self.collectibles.add(new_collectible)
                self.all_sprites.add(new_collectible)
            
            # Set goal
            self.goal = pygame.Rect(*level_data['goal'], 40, 40)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_state == "playing":
                            self.game_state = "paused"
                        else:
                            self.game_state = "playing"
            
            if self.game_state == "playing":
                self.update()
                self.draw()
            elif self.game_state == "paused":
                self.draw_pause_menu()
            elif self.game_state == "game_over":
                self.draw_game_over()
            elif self.game_state == "victory":
                self.draw_victory_screen()
            
            pygame.display.flip()
        
        pygame.quit()
    
    def update(self):
        """Update game state"""
        # Don't update if transitioning between states
        if self.minigame_manager.transitioning:
            return
            
        # Update all sprites
        self.all_sprites.update(self.platforms)
        self.enemies.update()
        self.collectibles.update()
        
        # Check collisions with collectibles
        hits = pygame.sprite.spritecollide(self.player, self.collectibles, True)
        for hit in hits:
            self.player.collectibles += 1
            if collect_sound:
                collect_sound.play()
        
        # Check collisions with enemies
        if not self.player.invulnerable:
            hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
            if hits:
                if self.player.take_damage(20):  # 20 damage per hit
                    if self.player.health <= 0:
                        self.game_state = "game_over"
        
        # Check collision with goal
        if self.player.collectibles >= self.level_manager.collectibles_required[self.level_manager.current_level]:
            if self.player.rect.colliderect(self.goal):
                self.level_manager.level_completed = True
                self.minigame_manager.minigame_required = True
                
                # Try to run minigame
                if self.minigame_manager.check_and_run_minigame(self.level_manager.current_level):
                    if win_sound:
                        win_sound.play()
                    
                    # Progress to next level or complete game
                    if self.level_manager.current_level == self.level_manager.max_level:
                        self.game_state = "victory"
                    else:
                        self.level_manager.next_level()
                        self.load_current_level()
                        self.player.collectibles = 0
                        self.player.health = 100
                        self.player.rect.x = SCREEN_WIDTH // 2
                        self.player.rect.y = SCREEN_HEIGHT - 100

    def draw(self):
        """Draw game state"""
        # Draw background
        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill(BLACK)
        
        # Draw all sprites
        self.platforms.draw(screen)
        self.enemies.draw(screen)
        self.collectibles.draw(screen)
        
        # Draw player
        if self.player.invulnerable:
            if pygame.time.get_ticks() % 2:  # Flashing effect
                screen.blit(self.player.image, self.player.rect)
        else:
            screen.blit(self.player.image, self.player.rect)
        
        # Draw goal
        if goal_image:
            screen.blit(goal_image, self.goal)
        else:
            pygame.draw.rect(screen, GREEN, self.goal)
        
        # Draw HUD
        self.draw_hud()
    
    def draw_hud(self):
        """Draw heads-up display"""
        # Health bar
        health_width = 200
        health_height = 20
        health_x = 20
        health_y = 20
        
        pygame.draw.rect(screen, RED, (health_x, health_y, health_width, health_height))
        pygame.draw.rect(screen, GREEN, 
                        (health_x, health_y, 
                         health_width * (self.player.health/100), health_height))
        
        # Collectibles counter
        collectibles_text = f"Collectibles: {self.player.collectibles}/{self.level_manager.collectibles_required[self.level_manager.current_level]}"
        text_surface = self.font.render(collectibles_text, True, WHITE)
        screen.blit(text_surface, (20, 50))
        
        # Level indicator
        level_text = f"Level: {self.level_manager.current_level}"
        text_surface = self.font.render(level_text, True, WHITE)
        screen.blit(text_surface, (SCREEN_WIDTH - 150, 20))

    def draw_pause_menu(self):
        """Draw pause menu"""
        # Darken the screen
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # Draw pause text
        text = self.font.render("PAUSED", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(text, text_rect)
        
        # Draw instructions
        text = self.font.render("Press ESC to resume", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        screen.blit(text, text_rect)

    def draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        text = self.font.render("GAME OVER", True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(text, text_rect)
        
        text = self.font.render("Press R to restart level", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        screen.blit(text, text_rect)
        
        text = self.font.render("Press Q to quit", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
        screen.blit(text, text_rect)
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            self.level_manager.reset_level()
            self.load_current_level()
            self.player.health = 100
            self.player.collectibles = 0
            self.game_state = "playing"
        elif keys[pygame.K_q]:
            self.running = False

    def draw_victory_screen(self):
        """Draw victory screen"""
        screen.fill(BLACK)
        
        text = self.font.render("CONGRATULATIONS!", True, YELLOW)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(text, text_rect)
        
        text = self.font.render("You have completed all levels!", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(text, text_rect)
        
        text = self.font.render("Press Q to quit", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        screen.blit(text, text_rect)
        
        if pygame.key.get_pressed()[pygame.K_q]:
            self.running = False

def main():
    """Main function to start the game"""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()