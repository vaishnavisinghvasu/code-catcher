import pygame
from player import Player
from falling_object import FallingObject
from settings import *
import random
import os

pygame.init()
pygame.mixer.init()

# Load sound files
def load_sound(filename):
    try:
        sound_path = os.path.join('assets', filename)
        return pygame.mixer.Sound(sound_path)
    except:
        return None

# Load all sounds
game_start_sound = load_sound('game_start.mp3')
game_over_sound = load_sound('game_over.mp3')
correct_sound = load_sound('correct.wav')
bug_sound = load_sound('bug.wav')
levelup_sound = load_sound('levelup.wav')
button_hover_sound = load_sound('hover.wav')
button_click_sound = load_sound('click.wav')

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color, action=None, font_size=FONT_MEDIUM):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.text = text
        self.action = action
        self.font = pygame.font.Font(GAME_FONT, font_size)
        self.is_hovered = False
        self.clicked = False
        self.hover_effect = 0
        self.hover_direction = 1

    def draw(self, screen):
        # Calculate hover effect (pulsing glow)
        self.hover_effect += 0.05 * self.hover_direction
        if self.hover_effect > 1:
            self.hover_effect = 1
            self.hover_direction = -1
        elif self.hover_effect < 0:
            self.hover_effect = 0
            self.hover_direction = 1
            
        current_color = self.hover_color if self.is_hovered else self.color
        
        # Draw button with glow effect if hovered
        if self.is_hovered:
            glow_rect = self.rect.inflate(10 + 5 * self.hover_effect, 10 + 5 * self.hover_effect)
            glow_color = (*self.hover_color[:3], 100)
            pygame.draw.rect(screen, glow_color, glow_rect, border_radius=10)
            
        # Draw main button
        pygame.draw.rect(screen, current_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)
        
        # Draw text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def update(self, mouse_pos, mouse_clicked):
        # Check if mouse is over button
        prev_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Play hover sound if just started hovering
        if self.is_hovered and not prev_hovered and button_hover_sound:
            button_hover_sound.play()
        
        # Check for click
        if self.is_hovered and mouse_clicked and self.action and not self.clicked:
            if button_click_sound:
                button_click_sound.play()
            self.clicked = True
            return self.action
        
        # Reset clicked state
        if not mouse_clicked:
            self.clicked = False
            
        return None

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(GAME_FONT, FONT_MEDIUM)
        self.state = 'menu'
        self.game_over = False
        self.player = Player()
        self.objects = []
        self.spawn_timer = 0
        self.score = 0
        self.level = 1
        self.missed_correct = 0
        self.caught_bugs = 0
        self.flash_alpha = 0
        self.flash_color = (0, 0, 0)
        self.menu_buttons = []
        self.game_over_buttons = []
        self.setup_buttons()
        self.background = self.create_background()
        self.particles = []
        self.tutorial_shown = False
        self.pause = False
        self.load_assets()
        
    def load_assets(self):
        # Load images
        try:
            self.logo = pygame.image.load('assets/logo.png').convert_alpha()
            self.logo = pygame.transform.scale(self.logo, (400, 200))
        except:
            self.logo = None
            
        try:
            self.player_img = pygame.image.load('assets/catcher.png').convert_alpha()
            self.player_img = pygame.transform.scale(self.player_img, (100, 60))
        except:
            self.player_img = None
            
    def create_background(self):
        # Create a gradient background with code-like elements
        bg = pygame.Surface((WIDTH, HEIGHT))
        
        # Draw gradient
        for y in range(HEIGHT):
            color_value = int(200 - 150 * (y / HEIGHT))
            color = (color_value, color_value + 20, color_value + 40)
            pygame.draw.line(bg, color, (0, y), (WIDTH, y))
        
        # Add some code-like symbols in the background
        symbols = ['{ }', '[ ]', '( )', '< >', ';', '==', '+=', '->']
        symbol_font = pygame.font.Font(GAME_FONT_MONO, 14)
        
        for _ in range(50):
            symbol = random.choice(symbols)
            symbol_surf = symbol_font.render(symbol, True, (255, 255, 255, 30))
            x = random.randint(0, WIDTH - 30)
            y = random.randint(0, HEIGHT - 30)
            symbol_surf.set_alpha(20)  # Very subtle
            bg.blit(symbol_surf, (x, y))
            
        return bg
        
    def setup_buttons(self):
        # Menu buttons
        start_btn = Button(
            WIDTH//2 - 100, HEIGHT//2, 
            200, 50, 
            "START GAME", GREEN, LIGHT_GREEN, DARK_GRAY,
            action="start_game"
        )
        
        tutorial_btn = Button(
            WIDTH//2 - 100, HEIGHT//2 + 70, 
            200, 50, 
            "HOW TO PLAY", BLUE, LIGHT_BLUE, WHITE,
            action="tutorial"
        )
        
        quit_btn = Button(
            WIDTH//2 - 100, HEIGHT//2 + 140, 
            200, 50, 
            "QUIT", LIGHT_RED, RED, WHITE,
            action="quit"
        )
        
        self.menu_buttons = [start_btn, tutorial_btn, quit_btn]
        
        # Game over buttons
        play_again_btn = Button(
            WIDTH//2 - 120, HEIGHT//2 + 50, 
            240, 50, 
            "PLAY AGAIN", GREEN, LIGHT_GREEN, DARK_GRAY,
            action="play_again"
        )
        
        menu_btn = Button(
            WIDTH//2 - 120, HEIGHT//2 + 120, 
            240, 50, 
            "BACK TO MENU", BLUE, LIGHT_BLUE, WHITE,
            action="menu"
        )
        
        self.game_over_buttons = [play_again_btn, menu_btn]
        
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_clicked = True
                    
            if event.type == pygame.KEYDOWN:
                if self.state == 'game':
                    if event.key == pygame.K_ESCAPE:
                        self.pause = not self.pause
                elif self.state == 'tutorial':
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        self.state = 'menu'
        
        # Handle buttons based on current state
        if self.state == 'menu':
            for button in self.menu_buttons:
                action = button.update(mouse_pos, mouse_clicked)
                if action == "start_game":
                    self.state = 'game'
                    self.start_game()
                elif action == "tutorial":
                    self.state = 'tutorial'
                elif action == "quit":
                    return False
                    
        elif self.state == 'game_over':
            for button in self.game_over_buttons:
                action = button.update(mouse_pos, mouse_clicked)
                if action == "play_again":
                    self.state = 'game'
                    self.reset_game()
                    self.start_game()
                elif action == "menu":
                    self.state = 'menu'
                    
        return True
        
    def start_game(self):
        if game_start_sound:
            game_start_sound.play()
        self.score = 0
        self.level = 1
        self.missed_correct = 0
        self.caught_bugs = 0
        self.game_over = False
        self.pause = False
        
    def reset_game(self):
        self.player = Player()
        self.objects = []
        self.particles = []
        self.spawn_timer = 0
        
    def update(self):
        if self.state == 'game' and not self.pause:
            self.game_update()
        
        # Update particles regardless of state
        self.update_particles()
        
        # Handle flash effect fade
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - 15)
            
    def update_particles(self):
        # Update and remove dead particles
        for particle in self.particles[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
                continue
                
            # Move particle
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Apply gravity or other effects
            particle['vy'] += 0.1  # Gravity
            
    def create_particle_effect(self, x, y, color, count=20, is_correct=True):
        for _ in range(count):
            speed = random.uniform(1, 3) if is_correct else random.uniform(0.5, 2)
            angle = random.uniform(0, 6.28)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': speed * math.cos(angle),
                'vy': speed * math.sin(angle) - 2,  # Initial upward velocity
                'radius': random.randint(2, 6),
                'color': color,
                'life': random.randint(20, 40)
            })
            
    def game_update(self):
        if self.game_over:
            self.state = 'game_over'
            if game_over_sound:
                game_over_sound.play()
            return
            
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        
        # Spawn new objects
        spawn_rate = max(20, 60 - self.level * 5)
        self.spawn_timer += 1
        if self.spawn_timer > spawn_rate:
            self.objects.append(FallingObject(self.level))
            self.spawn_timer = 0
            
        # Update objects and check collisions
        for obj in self.objects[:]:
            obj.update()
            
            if obj.rect.colliderect(self.player.rect):
                # Visual and audio feedback
                self.flash_color = (0, 255, 0) if obj.is_correct else (255, 0, 0)
                self.flash_alpha = 100
                
                # Create particle effect at collision point
                particle_color = GREEN if obj.is_correct else RED
                self.create_particle_effect(
                    obj.rect.centerx, 
                    obj.rect.centery, 
                    particle_color,
                    count=30,
                    is_correct=obj.is_correct
                )
                
                if obj.is_correct:
                    self.score += 1
                    if correct_sound:
                        correct_sound.play()
                else:
                    self.caught_bugs += 1
                    if bug_sound:
                        bug_sound.play()
                        
                self.objects.remove(obj)
                
            elif obj.rect.top > HEIGHT:
                if obj.is_correct:
                    self.missed_correct += 1
                    # Small negative feedback
                    self.create_particle_effect(
                        obj.rect.centerx, 
                        HEIGHT - 10,
                        LIGHT_RED,
                        count=10,
                        is_correct=False
                    )
                self.objects.remove(obj)
                
        # Level progression
        if self.score >= self.level * 10:
            self.level += 1
            if levelup_sound:
                levelup_sound.play()
                
            # Level up particle celebration
            for _ in range(5):
                self.create_particle_effect(
                    random.randint(0, WIDTH),
                    random.randint(HEIGHT//2, HEIGHT),
                    (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)),
                    count=20,
                    is_correct=True
                )
                
        # Game over conditions
        if self.missed_correct >= 5 or self.caught_bugs >= 5:
            self.game_over = True
            
    def draw(self):
        # Background
        self.screen.blit(self.background, (0, 0))
        
        # Draw particles
        self.draw_particles()
        
        # Flash effect if active
        if self.flash_alpha > 0:
            flash_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash_surface.fill((*self.flash_color[:3], self.flash_alpha))
            self.screen.blit(flash_surface, (0, 0))
        
        # State-specific drawing
        if self.state == 'menu':
            self.draw_menu()
        elif self.state == 'game':
            self.draw_game()
            if self.pause:
                self.draw_pause()
        elif self.state == 'game_over':
            self.draw_game_over()
        elif self.state == 'tutorial':
            self.draw_tutorial()
            
        pygame.display.flip()
        
    def draw_particles(self):
        for particle in self.particles:
            # Calculate alpha based on remaining life
            alpha = int(255 * (particle['life'] / 40))
            radius = particle['radius'] * (particle['life'] / 40)  # Shrink as life decreases
            
            # Create surface for this particle
            particle_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            
            # Draw the particle with alpha
            pygame.draw.circle(
                particle_surface, 
                (*particle['color'][:3], alpha), 
                (radius, radius), 
                int(radius)
            )
            
            # Blit to screen
            self.screen.blit(
                particle_surface, 
                (particle['x'] - radius, particle['y'] - radius)
            )
            
    def draw_menu(self):
        # Draw logo or title
        if self.logo:
            logo_rect = self.logo.get_rect(centerx=WIDTH//2, y=50)
            self.screen.blit(self.logo, logo_rect)
        else:
            # Fallback to text if logo isn't available
            title_font = pygame.font.Font(GAME_FONT_BOLD, FONT_XL)
            subtitle_font = pygame.font.Font(GAME_FONT, FONT_MEDIUM)
            
            # Draw glowing title effect
            glows = [(4, 4, 20), (3, 3, 40), (2, 2, 60), (1, 1, 80)]
            title_text = "CODE CATCHER"
            
            for offset_x, offset_y, alpha in glows:
                glow_surf = title_font.render(title_text, True, (*BLUE[:3], alpha))
                self.screen.blit(glow_surf, (WIDTH//2 - glow_surf.get_width()//2 + offset_x, HEIGHT//4 + offset_y))
                self.screen.blit(glow_surf, (WIDTH//2 - glow_surf.get_width()//2 - offset_x, HEIGHT//4 - offset_y))
            
            # Main title
            title = title_font.render(title_text, True, BLUE)
            subtitle = subtitle_font.render("Catch correct code snippets, avoid bugs!", True, DARK_GRAY)
            
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
            self.screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//3))
        
        # Draw animated buttons
        for button in self.menu_buttons:
            button.draw(self.screen)
            
        # Draw version info
        version_font = pygame.font.Font(GAME_FONT, FONT_TINY)
        version_text = version_font.render("v1.0", True, GRAY)
        self.screen.blit(version_text, (WIDTH - version_text.get_width() - 10, HEIGHT - version_text.get_height() - 10))
        
    def draw_game(self):
        # Draw header panel with gradient
        header_rect = pygame.Rect(0, 0, WIDTH, 70)
        pygame.draw.rect(self.screen, HEADER_COLOR, header_rect)
        
        # Add subtle pattern to header
        for i in range(10):
            x = random.randint(0, WIDTH)
            y = random.randint(0, 60)
            pygame.draw.circle(self.screen, (*LIGHT_BLUE[:3], 30), (x, y), 5)
        
        pygame.draw.line(self.screen, BLUE, (0, 70), (WIDTH, 70), 2)
        
        # Stats display with icons
        icons = [
            "🏆", # Score
            "📈", # Level
            "❤️", # Lives
            "🐞"  # Bugs
        ]
        
        stats_font = pygame.font.Font(GAME_FONT_MONO, FONT_SMALL)
        stats = [
            f"{icons[0]} {self.score}",
            f"{icons[1]} {self.level}",
            f"{icons[2]} {5 - self.missed_correct}",
            f"{icons[3]} {self.caught_bugs}/5"
        ]
        
        for i, stat in enumerate(stats):
            text = stats_font.render(stat, True, DARK_GRAY)
            
            # Create a subtle background for each stat
            bg_rect = pygame.Rect(20 + i*170, 10, 150, 30)
            pygame.draw.rect(self.screen, (*WHITE[:3], 180), bg_rect, border_radius=5)
            
            self.screen.blit(text, (30 + i*170, 15))
        
        # Progress bar with animation
        progress_bg_rect = pygame.Rect(20, 50, WIDTH-40, 10)
        progress_width = int((WIDTH-40)*(self.score%10)/10)
        progress_rect = pygame.Rect(20, 50, progress_width, 10)
        
        # Draw progress bar background with gradient
        pygame.draw.rect(self.screen, (*WHITE[:3], 100), progress_bg_rect, border_radius=5)
        
        # Draw actual progress
        if progress_width > 0:
            # Create a gradient effect for the progress bar
            for x in range(progress_width):
                progress_color = gradient_color(GREEN, LIGHT_GREEN, x/progress_width)
                pygame.draw.line(self.screen, progress_color, (20 + x, 50), (20 + x, 59))
                
        # Border for progress bar
        pygame.draw.rect(self.screen, GREEN, progress_bg_rect, 2, border_radius=5)
        
        # Add level indicator on progress bar
        level_indicator = stats_font.render(f"Level {self.level}", True, DARK_GRAY)
        self.screen.blit(level_indicator, (WIDTH//2 - level_indicator.get_width()//2, 30))
        
        # Game objects
        self.player.draw(self.screen, self.player_img)
        for obj in self.objects:
            obj.draw(self.screen)
            
    def draw_pause(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_font = pygame.font.Font(GAME_FONT_BOLD, FONT_XL)
        instruction_font = pygame.font.Font(GAME_FONT, FONT_MEDIUM)
        
        pause_text = pause_font.render("PAUSED", True, WHITE)
        instruction = instruction_font.render("Press ESC to Resume", True, LIGHT_BLUE)
        
        self.screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 50))
        self.screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT//2 + 20))
        
    def draw_game_over(self):
        # Draw the game state in the background
        self.draw_game()
        
        # Semi-transparent overlay with gradient
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(HEIGHT):
            alpha = 180 + int(20 * math.sin(y/30))
            overlay.fill((0, 0, 30, alpha), (0, y, WIDTH, 1))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text with glow effect
        title_font = pygame.font.Font(GAME_FONT_BOLD, FONT_XL)
        text_font = pygame.font.Font(GAME_FONT, FONT_LARGE)
        
        # Draw glowing text effect
        glows = [(3, 3, 50), (2, 2, 100), (1, 1, 150)]
        for offset_x, offset_y, alpha in glows:
            glow_surf = title_font.render("GAME OVER", True, (*RED[:3], alpha))
            self.screen.blit(glow_surf, (WIDTH//2 - glow_surf.get_width()//2 + offset_x, HEIGHT//3 + offset_y))
            self.screen.blit(glow_surf, (WIDTH//2 - glow_surf.get_width()//2 - offset_x, HEIGHT//3 - offset_y))
        
        # Main text
        title = title_font.render("GAME OVER", True, RED)
        score = text_font.render(f"Final Score: {self.score}", True, WHITE)
        level = text_font.render(f"Level Reached: {self.level}", True, LIGHT_BLUE)
        
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        self.screen.blit(score, (WIDTH//2 - score.get_width()//2, HEIGHT//2 - 30))
        self.screen.blit(level, (WIDTH//2 - level.get_width()//2, HEIGHT//2 + 10))
        
        # Draw animated buttons
        for button in self.game_over_buttons:
            button.draw(self.screen)
        
    def draw_tutorial(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 40, 220))
        self.screen.blit(overlay, (0, 0))
        
        # Tutorial content
        title_font = pygame.font.Font(GAME_FONT_BOLD, FONT_LARGE)
        text_font = pygame.font.Font(GAME_FONT, FONT_MEDIUM)
        tip_font = pygame.font.Font(GAME_FONT_MONO, FONT_SMALL)
        
        title = title_font.render("HOW TO PLAY", True, WHITE)
        
        instructions = [
            "1. Use LEFT and RIGHT arrow keys to move your code catcher",
            "2. Catch correct code snippets (green) to score points",
            "3. Avoid catching buggy code (red)",
            "4. Missing 5 correct snippets or catching 5 bugs ends the game",
            "5. Level up after every 10 points",
            "6. Press ESC during gameplay to pause"
        ]
        
        examples = [
            ("print('Hello')", "CORRECT - Valid syntax"),
            ("pront('Hello')", "BUG - Invalid function name")
        ]
        
        # Draw title
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Draw instructions
        for i, instruction in enumerate(instructions):
            inst_text = text_font.render(instruction, True, LIGHT_BLUE)
            self.screen.blit(inst_text, (WIDTH//2 - inst_text.get_width()//2, 120 + i*40))
        
        # Draw example section title
        example_title = text_font.render("EXAMPLES:", True, WHITE)
        self.screen.blit(example_title, (WIDTH//2 - example_title.get_width()//2, 380))
        
        # Draw examples with colored backgrounds
        for i, (code, desc) in enumerate(examples):
            # Code snippet background
            bg_color = GREEN if "CORRECT" in desc else RED
            snippet_rect = pygame.Rect(WIDTH//2 - 200, 420 + i*70, 400, 30)
            pygame.draw.rect(self.screen, bg_color, snippet_rect, border_radius=5)
            
            # Code text
            code_text = tip_font.render(code, True, WHITE)
            self.screen.blit(code_text, (WIDTH//2 - code_text.get_width()//2, 425 + i*70))
            
            # Description
            desc_text = tip_font.render(desc, True, LIGHT_GRAY)
            self.screen.blit(desc_text, (WIDTH//2 - desc_text.get_width()//2, 455 + i*70))
        
        # Back instruction
        back_text = text_font.render("Press ESC or ENTER to return to menu", True, GREEN)
        self.screen.blit(back_text, (WIDTH//2 - back_text.get_width()//2, HEIGHT - 50))

# Helper function for color gradients
def gradient_color(color1, color2, ratio):
    result = []
    for i in range(3):
        result.append(int(color1[i] * (1-ratio) + color2[i] * ratio))
    return tuple(result)

# Import math for particle effects
import math
