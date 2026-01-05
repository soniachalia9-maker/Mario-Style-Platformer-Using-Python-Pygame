import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -18
PLAYER_SPEED = 7

# Colors
SKY_BLUE = (135, 206, 235)
GROUND_GREEN = (86, 125, 70)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
BLUE = (0, 120, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Player:
    def __init__(self, x, y):
        self.width = 40
        self.height = 60
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = False
        self.direction = "right"
        self.jumping = False
        self.collected_coins = 0
        self.lives = 3
        self.invincible = 0
        self.color = RED
        
    def update(self, platforms, enemies, coins, powerups):
        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 20:  # Terminal velocity
            self.vel_y = 20
        
        # Horizontal movement
        self.rect.x += self.vel_x
        
        # Check horizontal collisions
        self.check_collisions(platforms, enemies, coins, powerups)
        
        # Vertical movement
        self.rect.y += self.vel_y
        self.on_ground = False
        
        # Check vertical collisions
        self.check_collisions(platforms, enemies, coins, powerups)
        
        # Screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
            self.vel_y = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.respawn()
            
        # Update invincibility timer
        if self.invincible > 0:
            self.invincible -= 1
            
    def check_collisions(self, platforms, enemies, coins, powerups):
        # Platform collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Vertical collision
                if self.vel_y > 0:  # Falling
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jumping = False
                elif self.vel_y < 0:  # Jumping
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
                # Horizontal collision
                elif self.vel_x > 0:  # Moving right
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:  # Moving left
                    self.rect.left = platform.rect.right
        
        # Enemy collisions
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect) and self.invincible == 0:
                # Player jumps on enemy
                if self.vel_y > 0 and self.rect.bottom <= enemy.rect.centery + 10:
                    enemy.hit()
                    self.vel_y = JUMP_STRENGTH / 1.5
                    self.jumping = True
                else:
                    self.take_damage()
                    
        # Coin collisions
        for coin in coins[:]:
            if self.rect.colliderect(coin.rect):
                coins.remove(coin)
                self.collected_coins += 1
                
        # Power-up collisions
        for powerup in powerups[:]:
            if self.rect.colliderect(powerup.rect):
                powerup.apply(self)
                powerups.remove(powerup)
                
    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.jumping = True
            
    def move_left(self):
        self.vel_x = -PLAYER_SPEED
        self.direction = "left"
        
    def move_right(self):
        self.vel_x = PLAYER_SPEED
        self.direction = "right"
        
    def stop(self):
        self.vel_x = 0
        
    def take_damage(self):
        if self.invincible == 0:
            self.lives -= 1
            self.invincible = 60  # 1 second of invincibility
            if self.lives <= 0:
                self.game_over = True
                
    def respawn(self):
        self.rect.x = 100
        self.rect.y = 100
        self.vel_x = 0
        self.vel_y = 0
        self.take_damage()
        
    def draw(self, screen):
        # Draw Mario-like character
        color = self.color if self.invincible % 10 < 5 else WHITE
        
        # Body
        pygame.draw.rect(screen, color, self.rect)
        
        # Face
        face_x = self.rect.centerx + (10 if self.direction == "right" else -10)
        pygame.draw.circle(screen, WHITE, (face_x, self.rect.centery - 5), 8)
        pygame.draw.circle(screen, BLACK, (face_x, self.rect.centery - 5), 3)
        
        # Hat (Mario-style)
        hat_rect = pygame.Rect(self.rect.left - 5, self.rect.top - 10, self.width + 10, 15)
        pygame.draw.rect(screen, color, hat_rect)
        pygame.draw.rect(screen, BLACK, hat_rect, 2)

class Platform:
    def __init__(self, x, y, width, height, color=BROWN):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        # Add texture
        pygame.draw.rect(screen, (100, 50, 20), self.rect, 2)

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 35, 35)
        self.vel_x = random.choice([-2, 2])
        self.color = BLUE
        
    def update(self, platforms):
        self.rect.x += self.vel_x
        
        # Change direction at edges
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                self.vel_x *= -1
                
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.vel_x *= -1
            
    def hit(self):
        # Enemy gets hit from above
        global score
        score += 100
        return True
        
    def draw(self, screen):
        # Goomba-like enemy
        pygame.draw.ellipse(screen, self.color, self.rect)
        
        # Eyes
        eye_x = self.rect.centerx + (-5 if self.vel_x > 0 else 5)
        pygame.draw.circle(screen, WHITE, (eye_x, self.rect.centery - 5), 6)
        pygame.draw.circle(screen, BLACK, (eye_x, self.rect.centery - 5), 3)

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.animation = 0
        
    def update(self):
        self.animation = (self.animation + 0.2) % 10
        
    def draw(self, screen):
        # Animated coin
        size = 10 + abs(5 - self.animation) * 2
        pygame.draw.circle(screen, YELLOW, self.rect.center, size)
        pygame.draw.circle(screen, (200, 200, 0), self.rect.center, size - 3)
        pygame.draw.circle(screen, YELLOW, self.rect.center, size - 6)

class PowerUp:
    def __init__(self, x, y, type="star"):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.type = type
        self.bounce = 0
        
    def update(self):
        self.bounce = (self.bounce + 0.1) % 6.28  # 2*pi
        
    def apply(self, player):
        if self.type == "star":
            player.invincible = 300  # 5 seconds of invincibility
            player.color = YELLOW
        elif self.type == "mushroom":
            player.lives += 1
            player.color = RED
            
    def draw(self, screen):
        # Bouncing effect
        y_offset = int(5 * abs(pygame.math.Vector2(0, 1).rotate(self.bounce * 90).y))
        
        if self.type == "star":
            # Draw star
            points = []
            center = (self.rect.centerx, self.rect.centery + y_offset)
            for i in range(5):
                angle = 72 * i - 90
                outer_x = center[0] + 15 * pygame.math.Vector2(1, 0).rotate(angle).x
                outer_y = center[1] + 15 * pygame.math.Vector2(1, 0).rotate(angle).y
                inner_x = center[0] + 7 * pygame.math.Vector2(1, 0).rotate(angle + 36).x
                inner_y = center[1] + 7 * pygame.math.Vector2(1, 0).rotate(angle + 36).y
                points.extend([(outer_x, outer_y), (inner_x, inner_y)])
            pygame.draw.polygon(screen, YELLOW, points)
            
        elif self.type == "mushroom":
            # Draw mushroom
            mushroom_rect = pygame.Rect(
                self.rect.left, 
                self.rect.top + y_offset, 
                self.rect.width, 
                self.rect.height
            )
            pygame.draw.ellipse(screen, RED, mushroom_rect)
            cap_rect = pygame.Rect(
                self.rect.left - 5,
                self.rect.top - 10 + y_offset,
                self.rect.width + 10,
                20
            )
            pygame.draw.ellipse(screen, RED, cap_rect)
            pygame.draw.ellipse(screen, WHITE, cap_rect, 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PyMario - Platformer Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.reset_game()
        
    def reset_game(self):
        global score
        score = 0
        
        # Create player
        self.player = Player(100, 100)
        
        # Create platforms
        self.platforms = [
            Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50, GROUND_GREEN),  # Ground
            Platform(200, 500, 200, 20),
            Platform(500, 400, 150, 20),
            Platform(300, 300, 200, 20),
            Platform(600, 250, 150, 20),
            Platform(100, 200, 100, 20),
            Platform(700, 550, 100, 20),
            Platform(400, 450, 100, 20),
            Platform(800, 350, 150, 20),
        ]
        
        # Create enemies
        self.enemies = [
            Enemy(300, 450),
            Enemy(600, 200),
            Enemy(800, 300),
        ]
        
        # Create coins
        self.coins = []
        for i in range(20):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 150)
            self.coins.append(Coin(x, y))
            
        # Create power-ups
        self.powerups = [
            PowerUp(400, 250, "star"),
            PowerUp(750, 500, "mushroom"),
        ]
        
        # Game state
        self.game_over = False
        self.level_complete = False
        self.level = 1
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                    
                if self.game_over or self.level_complete:
                    if event.key == pygame.K_r:
                        self.reset_game()
                else:
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                    elif event.key == pygame.K_UP:
                        self.player.jump()
                        
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    self.player.stop()
                    
    def update(self):
        if self.game_over or self.level_complete:
            return
            
        # Update player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move_left()
        if keys[pygame.K_RIGHT]:
            self.player.move_right()
            
        self.player.update(self.platforms, self.enemies, self.coins, self.powerups)
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.platforms)
            
        # Update coins
        for coin in self.coins:
            coin.update()
            
        # Update power-ups
        for powerup in self.powerups:
            powerup.update()
            
        # Check level completion
        if len(self.coins) == 0:
            self.level_complete = True
            
        # Check game over
        if self.player.lives <= 0:
            self.game_over = True
            
    def draw(self):
        # Draw sky
        self.screen.fill(SKY_BLUE)
        
        # Draw clouds
        for i in range(5):
            x = (pygame.time.get_ticks() // 50 + i * 200) % (SCREEN_WIDTH + 400) - 200
            y = 100 + i * 40
            pygame.draw.ellipse(self.screen, WHITE, (x, y, 100, 40))
            pygame.draw.ellipse(self.screen, WHITE, (x + 30, y - 20, 80, 40))
            pygame.draw.ellipse(self.screen, WHITE, (x + 60, y, 70, 40))
        
        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)
            
        # Draw coins
        for coin in self.coins:
            coin.draw(self.screen)
            
        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(self.screen)
            
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
            
        # Draw player
        self.player.draw(self.screen)
        
        # Draw HUD
        self.draw_hud()
        
        # Draw game over or level complete screen
        if self.game_over:
            self.draw_game_over()
        elif self.level_complete:
            self.draw_level_complete()
            
        pygame.display.flip()
        
    def draw_hud(self):
        # Score
        score_text = self.font.render(f"Score: {score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Coins
        coin_text = self.font.render(f"Coins: {self.player.collected_coins}", True, WHITE)
        self.screen.blit(coin_text, (10, 50))
        
        # Lives
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 90))
        
        # Level
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH - 150, 10))
        
        # Controls help
        controls = [
            "← → : Move",
            "SPACE/↑ : Jump",
            "ESC : Quit",
            "R : Restart"
        ]
        
        for i, text in enumerate(controls):
            control_text = self.small_font.render(text, True, WHITE)
            self.screen.blit(control_text, (SCREEN_WIDTH - 200, 50 + i * 25))
            
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Final Score: {score}", True, WHITE)
        restart_text = self.small_font.render("Press R to restart", True, WHITE)
        
        self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))
        self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
        
    def draw_level_complete(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 50, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        complete_text = self.font.render("LEVEL COMPLETE!", True, YELLOW)
        score_text = self.font.render(f"Score: {score}", True, WHITE)
        next_text = self.small_font.render("Press R for next level", True, WHITE)
        
        self.screen.blit(complete_text, (SCREEN_WIDTH//2 - complete_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))
        self.screen.blit(next_text, (SCREEN_WIDTH//2 - next_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
        
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()