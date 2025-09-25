import pygame
from settings import *

class Player:
    def __init__(self):
        # Player dimensions
        self.width = 120
        self.height = 30
        
        # Initial position (centered horizontally, near bottom of screen)
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 80
        
        # Create player rectangle for collision detection
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Movement speed
        self.speed = 8
        
        # Visual effects
        self.trail = []
        self.max_trail = 5
        self.active_animation = 0
        self.animation_speed = 0.2
        
    def update(self, keys):
        # Store previous position for trail effect
        prev_pos = self.rect.copy()
        
        # Handle horizontal movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
            
        # Keep player within screen bounds
        if self.x < 0:
            self.x = 0
        elif self.x > WIDTH - self.width:
            self.x = WIDTH - self.width
            
        # Update rectangle position
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Update animation counter
        self.active_animation += self.animation_speed
        if self.active_animation >= 4:
            self.active_animation = 0
            
        # Add to trail if we moved
        if prev_pos.x != self.rect.x:
            self.trail.append(prev_pos.copy())
            # Keep trail at max length
            if len(self.trail) > self.max_trail:
                self.trail.pop(0)
        
    def draw(self, screen, player_img=None):
        # Draw trail with decreasing opacity
        for i, trail_rect in enumerate(self.trail):
            alpha = int(128 * ((i + 1) / len(self.trail)))
            trail_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            trail_surf.fill((*BLUE[:3], alpha))
            screen.blit(trail_surf, trail_rect)
        
        # Draw player using image if available
        if player_img:
            screen.blit(player_img, (self.rect.x - 15, self.rect.y - 15))
        else:
            # Draw a code catcher (basket-like receptacle)
            # Main body with gradient
            gradient_rect = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            for y in range(self.height):
                alpha = 255 - int(150 * (y / self.height))
                color = (*BLUE[:3], alpha)
                pygame.draw.line(gradient_rect, color, (0, y), (self.width, y))
            screen.blit(gradient_rect, self.rect)
            
            # Draw border
            pygame.draw.rect(screen, BLUE, self.rect, 2, border_radius=5)
            
            # Add some visual flair - an animated "reception" indicator
            indicators = [
                # Circle patterns when receiving code
                [(self.width//4, 5), (self.width//2, 5), (3*self.width//4, 5)],
                [(self.width//4, 8), (self.width//2, 8), (3*self.width//4, 8)],
                [(self.width//4, 11), (self.width//2, 11), (3*self.width//4, 11)],
                [(self.width//4, 14), (self.width//2, 14), (3*self.width//4, 14)]
            ]
            
            active_index = int(self.active_animation)
            for dot_pos in indicators[active_index]:
                dot_x = self.rect.x + dot_pos[0]
                dot_y = self.rect.y + dot_pos[1]
                pygame.draw.circle(screen, LIGHT_BLUE, (dot_x, dot_y), 3)
                
            # Add text to indicate function
            font = pygame.font.Font(GAME_FONT_MONO, FONT_TINY)
            text = font.render("def catch():", True, WHITE)
            screen.blit(text, (self.rect.x + 10, self.rect.y + 8))