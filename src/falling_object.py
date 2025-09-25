import pygame
import random
import math
from settings import *

class FallingObject:
    def __init__(self, level):
        self.width = random.randint(120, 220)
        self.height = 50
        self.rect = pygame.Rect(
            random.randint(0, WIDTH - self.width),
            -self.height,
            self.width,
            self.height
        )
        
        # Varied speed based on level
        base_speed = 2 + (level * 0.5)
        self.speed = random.uniform(base_speed, base_speed + 3)
        
        # Random horizontal movement
        self.has_horizontal_movement = random.random() < 0.3
        if self.has_horizontal_movement:
            self.h_speed = random.choice([-1, 1]) * random.uniform(0.5, 1.5)
            self.h_distance = 0
            self.max_h_distance = random.randint(30, 80)
        
        # Determine if this is correct code or a bug
        self.is_correct = random.choice([True, False])
        
        # Code snippets by level
        if level <= 2:
            self.correct_snippets = [
                "print('Hello')",
                "x = 5 + 3",
                "def func():",
                "for i in range(10):",
                "if x > 0:"
            ]
            self.bug_snippets = [
                "pront('Hello')",
                "x = 5 + ",
                "def func()",
                "for i in rage(10):",
                "if x > 0"
            ]
        elif level <= 4:
            self.correct_snippets = [
                "while True: break",
                "try: except ValueError:",
                "class MyClass(object):",
                "with open('file.txt') as f:",
                "import random"
            ]
            self.bug_snippets = [
                "while True, break",
                "try: except ValueError",
                "class MyClass(object)",
                "with open('file.txt') as f",
                "import randum"
            ]
        else:
            self.correct_snippets = [
                "lambda x: x * 2",
                "[x for x in range(10)]",
                "async def func(): await x",
                "assert condition, 'message'",
                "yield from generator()"
            ]
            self.bug_snippets = [
                "lambda x: x *",
                "[x for x in range 10]",
                "async def func(): wait x",
                "assert condition 'message'",
                "yield form generator()"
            ]
        
        # Select a random snippet
        if self.is_correct:
            self.text = random.choice(self.correct_snippets)
        else:
            self.text = random.choice(self.bug_snippets)
        
        # Visual properties
        self.font = pygame.font.Font(GAME_FONT_MONO, 16)
        self.wobble = 0
        self.wobble_speed = random.uniform(0.05, 0.15)
        self.wobble_amount = random.uniform(0.5, 1.5)
        self.angle = random.uniform(-5, 5)
        self.rotation_speed = random.uniform(-0.2, 0.2)
        
        # Animation properties
        self.shine_pos = 0
        self.shine_speed = random.uniform(0.01, 0.03)
        
        # Particles
        self.particles = []
        
    def update(self):
        # Update vertical position
        self.rect.y += self.speed
        
        # Update horizontal movement if applicable
        if self.has_horizontal_movement:
            self.h_distance += abs(self.h_speed)
            if self.h_distance >= self.max_h_distance:
                self.h_speed *= -1
                self.h_distance = 0
            self.rect.x += self.h_speed
            
            # Keep within screen bounds
            if self.rect.left < 0:
                self.rect.left = 0
                self.h_speed = abs(self.h_speed)
            elif self.rect.right > WIDTH:
                self.rect.right = WIDTH
                self.h_speed = -abs(self.h_speed)
        
        # Update wobble and rotation
        self.wobble += self.wobble_speed
        self.angle += self.rotation_speed
        
        # Update shine animation
        self.shine_pos += self.shine_speed
        if self.shine_pos > 1.5:
            self.shine_pos = -0.5
            
        # Update particles
        for particle in self.particles[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
                continue
                
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.1  # Gravity
            
        # Randomly emit trail particles
        if random.random() < 0.1:
            self.add_trail_particle()
    
    def add_trail_particle(self):
        color = LIGHT_GREEN if self.is_correct else LIGHT_RED
        self.particles.append({
            'x': self.rect.x + random.randint(0, self.width),
            'y': self.rect.y + self.height,
            'vx': random.uniform(-0.5, 0.5),
            'vy': random.uniform(0.5, 1.5),
            'radius': random.uniform(1, 3),
            'color': color,
            'life': random.randint(10, 30)
        })
            
    def draw(self, screen):
        # Draw particles first (behind the object)
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 30))
            particle_surf = pygame.Surface((particle['radius']*2, particle['radius']*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (*particle['color'][:3], alpha), 
                              (particle['radius'], particle['radius']), particle['radius'])
            screen.blit(particle_surf, (particle['x'] - particle['radius'], particle['y'] - particle['radius']))
        
        # Calculate wobble offset
        wobble_offset = math.sin(self.wobble) * self.wobble_amount
        
        # Create a surface for the object that can be rotated
        obj_surf = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
        
        # Calculate background and border colors with slight variance for visual interest
        bg_color = LIGHT_GREEN if self.is_correct else LIGHT_RED
        border_color = GREEN if self.is_correct else RED
        
        # Draw the main object on the surface
        obj_rect = pygame.Rect(10, 10, self.width, self.height)
        
        # Draw rounded rectangle with shadow
        shadow_rect = obj_rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(obj_surf, (*DARK_GRAY[:3], 100), shadow_rect, border_radius=8)
        
        # Draw main rectangle
        pygame.draw.rect(obj_surf, bg_color, obj_rect, border_radius=8)
        pygame.draw.rect(obj_surf, border_color, obj_rect, 2, border_radius=8)
        
        # Render text with shadow effect
        text_surface = self.font.render(self.text, True, DARK_GRAY)
        shadow_surface = self.font.render(self.text, True, (*DARK_GRAY[:3], 120))
        
        text_pos = (
            obj_rect.x + obj_rect.width//2 - text_surface.get_width()//2,
            obj_rect.y + obj_rect.height//2 - text_surface.get_height()//2
        )
        
        # Draw shadow first
        obj_surf.blit(shadow_surface, (text_pos[0]+1, text_pos[1]+1))
        # Then draw main text
        obj_surf.blit(text_surface, text_pos)
        
        # Add a shine effect
        if self.shine_pos > 0 and self.shine_pos < 1:
            shine_x = int(obj_rect.x + self.shine_pos * obj_rect.width)
            shine_height = obj_rect.height - 4
            shine_width = 20
            
            # Create gradient for shine
            for i in range(shine_width):
                alpha = int(255 * math.sin(i / shine_width * math.pi) * 0.5)
                color = (255, 255, 255, alpha)
                shine_rect = pygame.Rect(shine_x - shine_width//2 + i, obj_rect.y + 2, 1, shine_height)
                pygame.draw.rect(obj_surf, color, shine_rect)
        
        # Draw a small icon to help quickly identify
        icon_size = 12
        icon_rect = pygame.Rect(
            obj_rect.right - icon_size - 8, 
            obj_rect.top + 5, 
            icon_size, 
            icon_size
        )
        if self.is_correct:
            # Draw checkmark
            pygame.draw.circle(obj_surf, GREEN, icon_rect.center, icon_size//2)
            pygame.draw.line(obj_surf, WHITE, 
                            (icon_rect.centerx - 4, icon_rect.centery), 
                            (icon_rect.centerx - 1, icon_rect.centery + 3), 2)
            pygame.draw.line(obj_surf, WHITE, 
                            (icon_rect.centerx - 1, icon_rect.centery + 3), 
                            (icon_rect.centerx + 4, icon_rect.centery - 3), 2)
        else:
            # Draw bug
            pygame.draw.circle(obj_surf, RED, icon_rect.center, icon_size//2)
            pygame.draw.line(obj_surf, WHITE, 
                            (icon_rect.centerx - 3, icon_rect.centery - 3), 
                            (icon_rect.centerx + 3, icon_rect.centery + 3), 2)
            pygame.draw.line(obj_surf, WHITE, 
                            (icon_rect.centerx + 3, icon_rect.centery - 3), 
                            (icon_rect.centerx - 3, icon_rect.centery + 3), 2)
        
        # Rotate surface
        rotated_surf = pygame.transform.rotate(obj_surf, self.angle)
        rotated_rect = rotated_surf.get_rect(center=(self.rect.centerx + wobble_offset, self.rect.centery))
        
        # Draw to screen
        screen.blit(rotated_surf, rotated_rect.topleft)
