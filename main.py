import sys

import pygame
import random

from assets import (
    AssetManager,
    WIDTH,
    HEIGHT,
    FPS,
    PIPE_SPAWN_DISTANCE,
    GROUND_HEIGHT,
    load_high_scores,
    save_high_scores,
)
from entities import Bird, Pipe, ParallaxLayer, Button

#STATES
MENU_STATE = "menu"
READY_STATE = "get_ready"
PLAYING_STATE = "playing"
GAME_OVER_STATE = "game_over"

CONTROL_MODE_KEYBOARD = "keyboard"
CONTROL_MODE_VISUAL = "visual"


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()

        self.assets = AssetManager().load_all()
        self.high_score = load_high_scores()

        self.state = MENU_STATE
        self.control_mode = None

        self.bird = None
        self.pipes = []
        self.score = 0
        self.gesture_controller = None
        self.layers = []

        self.create_mode_buttons()
        self.create_game_over_buttons()

    # The menu uses two large buttons so the player can choose keyboard or camera input before the round begins.
    def create_mode_buttons(self):
        ui_assets = self.assets.ui
        self.control_mode_buttons = [
            Button(
                ui_assets["btn_keyboard"],
                (WIDTH // 2, HEIGHT // 2 + 50),
                on_click=self.choose_control_mode,
                value=CONTROL_MODE_KEYBOARD,
            ),
            Button(
                ui_assets["btn_visual"],
                (WIDTH // 2, HEIGHT // 2 + 170),
                on_click=self.choose_control_mode,
                value=CONTROL_MODE_VISUAL,
            ),
        ]

    def create_game_over_buttons(self):
        ui_assets = self.assets.ui
        self.result_buttons = [
            Button(
                ui_assets["btn_restart"],
                (WIDTH // 2 - 150, HEIGHT // 2 + 160),
                on_click=self.restart_round,
            ),
            Button(
                ui_assets["btn_menu"],
                (WIDTH // 2 + 150, HEIGHT // 2 + 160),
                on_click=self.return_to_menu,
            ),
        ]

    def choose_control_mode(self, mode_name):
        if mode_name == CONTROL_MODE_VISUAL and self.gesture_controller is None:
            if not self.start_visual_controls():
                return 
        self.control_mode = mode_name
        self.begin_round_if_ready()

    def start_visual_controls(self):
        """Lazily starts the webcam and hand-landmarker for gesture mode."""
        try:
            from gesture_input import GestureController

            self.gesture_controller = GestureController(debug=True)
            return True
        except Exception as exc:
            print(f"[Visual mode unavailable] {exc}")
            return False

    def begin_round_if_ready(self):
        if self.control_mode:
            self.prepare_round()

    def restart_round(self, _value=None):
        self.prepare_round()

    def return_to_menu(self, _value=None):
        self.control_mode = None
        self.state = MENU_STATE
        self.stop_visual_controls()

    def stop_visual_controls(self):
        if self.gesture_controller:
            self.gesture_controller.release()
            self.gesture_controller = None

    def prepare_round(self):
        self.build_background_layers()
        bird_frames = self.assets.bird_frames
        self.bird = Bird(bird_frames, start_x=180, start_y=HEIGHT // 2)
        self.pipes = []
        self.score = 0
        self.state = READY_STATE

    def build_background_layers(self):
        self.layers = [
            ParallaxLayer(self.assets.sky, y=0, speed=0),
            ParallaxLayer(self.assets.clouds, y=60, speed=1),
            ParallaxLayer(self.assets.ground, y=HEIGHT - GROUND_HEIGHT, speed=4),
        ]

    def launch_round(self):
        self.state = PLAYING_STATE
        self.pipes.append(Pipe(self.assets.pipe))

    def finish_round(self):
        self.state = GAME_OVER_STATE
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_scores(self.high_score)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop_visual_controls()
                pygame.quit()
                sys.exit()

            if self.state == MENU_STATE:
                for button in self.control_mode_buttons:
                    button.handle_event(event)

            elif self.state == READY_STATE:
                if self.control_mode == CONTROL_MODE_KEYBOARD:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.launch_round()

            elif self.state == PLAYING_STATE:
                if self.control_mode == CONTROL_MODE_KEYBOARD:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.bird.jump()

            elif self.state == GAME_OVER_STATE:
                for button in self.result_buttons:
                    button.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.prepare_round()

    def update(self):
        if self.state == READY_STATE:
            self.bird.animate_idle()
            for layer in self.layers:
                layer.update()

            if self.control_mode == CONTROL_MODE_VISUAL and self.gesture_controller:
                self.gesture_controller.poll()
                if self.gesture_controller.consume_start_signal():
                    self.launch_round()

        elif self.state == PLAYING_STATE:
            self.bird.update()
            for layer in self.layers:
                layer.update()

            if self.control_mode == CONTROL_MODE_VISUAL and self.gesture_controller:
                self.gesture_controller.poll()
                if self.gesture_controller.consume_jump_signal():
                    self.bird.jump()

            for pipe in self.pipes:
                pipe.update()
            self.pipes = [pipe for pipe in self.pipes if not pipe.has_left_screen()]

            if self.pipes:
                latest_pipe = self.pipes[-1]
                num = random.randint(1,6)*20
                if latest_pipe.top_rect.x <= WIDTH + num - PIPE_SPAWN_DISTANCE:
                    self.pipes.append(Pipe(self.assets.pipe))

            for pipe in self.pipes:
                if self.bird.rect.colliderect(pipe.top_rect) or self.bird.rect.colliderect(pipe.bottom_rect):
                    self.finish_round()
                if not pipe.scored and pipe.top_rect.centerx < self.bird.x:
                    pipe.scored = True
                    self.score += 1

            if self.bird.rect.top <= 0 or self.bird.rect.bottom >= HEIGHT - GROUND_HEIGHT:
                self.finish_round()

        elif self.state == GAME_OVER_STATE:
            if self.control_mode == CONTROL_MODE_VISUAL and self.gesture_controller:
                self.gesture_controller.poll()
                if self.gesture_controller.consume_thumbs_up_signal():
                    self.restart_round()
                elif self.gesture_controller.consume_fist_signal():
                    self.return_to_menu()

    def draw(self):
        screen = self.screen
        ui_assets = self.assets.ui
        screen.fill((0, 0, 0))

        if self.state == MENU_STATE:
            self.draw_main_menu()
        else:
            for layer in self.layers:
                layer.draw(screen)

            if self.state == READY_STATE:
                self.bird.draw_ready_pose(screen)
                banner = ui_assets["get_ready_banner"]
                screen.blit(banner, banner.get_rect(center=(WIDTH // 2, HEIGHT // 3)))
                prompt_text = "Press SPACE to Play" if self.control_mode == CONTROL_MODE_KEYBOARD else "Show OPEN PALM to Play"
                prompt_font = self.assets.font(18)
                prompt_surface = prompt_font.render(prompt_text, True, (255, 255, 255))
                screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 120)))
                if self.control_mode == CONTROL_MODE_VISUAL and self.gesture_controller:
                    debug_font = self.assets.font(14)
                    debug_text = debug_font.render(
                        f"Detected: {self.gesture_controller.current_gesture}",
                        True,
                        (255, 255, 0),
                    )
                    screen.blit(debug_text, (20, HEIGHT - 30))

            elif self.state == PLAYING_STATE:
                for pipe in self.pipes:
                    pipe.draw(screen)
                self.bird.draw(screen)
                self.draw_score_overlay()

            elif self.state == GAME_OVER_STATE:
                for pipe in self.pipes:
                    pipe.draw(screen)
                self.bird.draw(screen)
                self.draw_result_panel()
                for button in self.result_buttons:
                    button.draw(screen)
                if self.control_mode == CONTROL_MODE_VISUAL:
                    self.draw_visual_gesture_hints()

        pygame.display.update()

    def draw_main_menu(self):
        screen = self.screen
        ui_assets = self.assets.ui
        logo = ui_assets["title_logo"]
        menu_background = pygame.transform.scale(
            pygame.image.load("assets/neutral/ui/menu_background.png").convert(),
            (WIDTH, HEIGHT),
        )
        screen.blit(menu_background, (0, 0))
        screen.blit(logo, logo.get_rect(center=(WIDTH // 2, 180)))

        for button, mode_name in zip(self.control_mode_buttons, [CONTROL_MODE_KEYBOARD, CONTROL_MODE_VISUAL]):
            button.draw(screen)
            if self.control_mode == mode_name:
                pygame.draw.rect(screen, (255, 255, 0), button.rect.inflate(10, 10), 4)

        hint_font = self.assets.font(16)
        hint = hint_font.render("Choose a control mode to begin", True, (0, 0, 0))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
        score_font = self.assets.font(24)
        score = score_font.render(f"High Score: {self.high_score}", True, (0, 0, 0))
        screen.blit(score, score.get_rect(center=(WIDTH // 2, HEIGHT - 100)))

    def draw_score_overlay(self):
        font = self.assets.font(28)
        text = font.render(str(self.score), True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=(WIDTH // 2, 60)))

    def draw_result_panel(self):
        ui_assets = self.assets.ui
        panel = ui_assets["score_panel"]
        rect = panel.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        self.screen.blit(panel, rect)

        font = self.assets.font(22)
        score_text = font.render(str(self.score), True, (60, 40, 20))
        best_text = font.render(str(self.high_score), True, (60, 40, 20))

        self.screen.blit(score_text, (rect.centerx + 60, rect.centery - 60))
        self.screen.blit(best_text, (rect.centerx + 60, rect.centery + 33))

    def draw_visual_gesture_hints(self):
        font = self.assets.font(14)
        restart_label = font.render("THUMBS-UP", True, (255, 255, 255))
        menu_label = font.render("FIST", True, (255, 255, 255))

        restart_button = self.result_buttons[0]
        menu_button = self.result_buttons[1]

        restart_rect = restart_label.get_rect(center=(restart_button.rect.centerx, restart_button.rect.bottom + 24))
        menu_rect = menu_label.get_rect(center=(menu_button.rect.centerx, menu_button.rect.bottom + 24))

        self.screen.blit(restart_label, restart_rect)
        self.screen.blit(menu_label, menu_rect)

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()


if __name__ == "__main__":
    Game().run()
