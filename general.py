import pygame
import os
import math

def load_image_convert_alpha(filename):
    """Load an image with the given filename from the images directory"""
    return pygame.image.load(os.path.join('images', filename)).convert_alpha()

def load_sound(filename):
    """Load a sound with the given filename from the sounds directory"""
    return pygame.mixer.Sound(os.path.join('sounds', filename))

def draw_centered(surface1, surface2, position):
    """Draw surface1 onto surface2 with center at position"""
    rect = surface1.get_rect()
    rect = rect.move(position[0]-rect.width//2, position[1]-rect.height//2)
    surface2.blit(surface1, rect)

def rotate_center(image, angle):
        """rotate the given image around its center & return an image & rect, works in degrees not radians"""
        rotate_image = pygame.transform.rotate(image, angle)
        return rotate_image

def distance(p, q): # p and q are XY coordinates in the form of arrays/lists
    """Helper function to calculate distance between 2 points"""
    return math.sqrt((p[0]-q[0])**2 + (p[1]-q[1])**2)

def vector_magnitude(x, y):
    return math.sqrt(x**2 + y**2)
