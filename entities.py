
import random

import pygame

from assets import WIDTH, HEIGHT, GRAVITY, JUMP_STRENGTH, PIPE_SPEED, PIPE_GAP


class Bird:
    def __init__(self, frames, start_x=180, start_y=None):
        """frames: list of 3 pygame Surfaces for the flap animation."""
        self.frames = frames
        self.x = start_x
        self.y = start_y if start_y is not None else HEIGHT // 2
        self.velocity = 0
        self.frame_index = 0
        self.animation_counter = 0

        self.image = self.frames[0]
        self.rotated_image = self.image
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def animate_idle(self):
        """A gentle bob and wing-flap for the get-ready screen."""
        self.animation_counter += 1
        if self.animation_counter >= 8:
            self.animation_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

        self.animation_counter += 1
        if self.animation_counter >= 5:
            self.animation_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.image = self.frames[self.frame_index]

        angle = -self.velocity * 3
        angle = max(-25, min(90, angle))
        self.rotated_image = pygame.transform.rotate(self.image, angle)
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))

    def draw(self, surface):
        surface.blit(self.rotated_image, self.rect)

    def draw_ready_pose(self, surface):
        surface.blit(self.image, self.rect)


class Pipe:
    def __init__(self, pipe_image):
        self.gap_y = random.randint(220, HEIGHT - 220)

        self.top_image = pygame.transform.flip(pipe_image, False, True)
        self.bottom_image = pipe_image

        self.top_rect = self.top_image.get_rect(
            midbottom=(WIDTH + 100, self.gap_y - PIPE_GAP // 2)
        )
        self.bottom_rect = self.bottom_image.get_rect(
            midtop=(WIDTH + 100, self.gap_y + PIPE_GAP // 2)
        )
        self.scored = False

    def update(self):
        self.top_rect.x -= PIPE_SPEED
        self.bottom_rect.x -= PIPE_SPEED

    def draw(self, surface):
        surface.blit(self.top_image, self.top_rect)
        surface.blit(self.bottom_image, self.bottom_rect)

    def has_left_screen(self):
        return self.top_rect.right < 0


class ParallaxLayer:
    def __init__(self, image, y, speed=0):
        """A simple scrolling layer for the sky, clouds, and ground."""
        self.image = image
        self.width = image.get_width()
        self.y = y
        self.speed = speed
        self.x1 = 0
        self.x2 = self.width

    def update(self):
        if self.speed == 0:
            return
        self.x1 -= self.speed
        self.x2 -= self.speed
        if self.x1 <= -self.width:
            self.x1 = self.x2 + self.width
        if self.x2 <= -self.width:
            self.x2 = self.x1 + self.width

    def draw(self, surface):
        if self.speed == 0:
            surface.blit(self.image, (0, self.y))
        else:
            surface.blit(self.image, (self.x1, self.y))
            surface.blit(self.image, (self.x2, self.y))


class Button:
    def __init__(self, image, center, on_click=None, value=None):
        self.image = image
        self.rect = self.image.get_rect(center=center)
        self.on_click = on_click
        self.value = value

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_clicked(event.pos):
                if self.on_click:
                    self.on_click(self.value)
                return True
        return False
