import sys
import pygame
from settings import *
from game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Code Catcher")
    clock = pygame.time.Clock()
    
    game = Game(screen)
    
    running = True
    while running:
        running = game.handle_events()
        game.update()
        game.draw()
        clock.tick(FPS)  # Control the game frame rate
    
    pygame.quit()

if __name__ == "__main__":
    main()
