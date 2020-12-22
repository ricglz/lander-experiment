"""Game loop logic"""
import sys

import pygame
from numpy import array

from .event_handler import EventHandler
from .lander import Lander
from .controller import Controller
from .vector import Vector
from .game_logic import GameLogic
from .surface import Surface
from .main_menu import MainMenu
from .result_menu import ResultMenu
from .data_collection import DataCollection

class GameLoop:
    action = -1
    controller = Controller()
    fps = 60
    fps_clock = pygame.time.Clock()
    game_logic = GameLogic()
    game_started = False
    lander = None
    main_menu = None
    object_list = []
    result_menu = None
    screen = None
    sprites = None
    state = None
    surface = None
    total_games = 0
    won_games = 0

    def __init__(self, config_data, predictor):
        pygame.init()
        self.handler = EventHandler(self.controller, self)
        self.config_data = config_data
        config_data['SCREEN_WIDTH'] = int(config_data['SCREEN_WIDTH'])
        config_data['SCREEN_HEIGHT'] = int(config_data['SCREEN_HEIGHT'])
        config_data['DIM'] = config_data['SCREEN_WIDTH'], config_data['SCREEN_HEIGHT']
        self.screen = pygame.display.set_mode(config_data['DIM'])
        pygame.display.set_caption('Lander game')
        pygame.display.set_icon(pygame.image.load(config_data['LANDER_IMG_PATH']))
        self.main_menu = MainMenu(config_data['DIM'])
        self.result_menu = ResultMenu(config_data['DIM'])
        self.predictor = predictor

    def score_calculation(self):
        """Calculates the score of the game"""
        score = 1000.0 - (self.surface.centre_landing_pad[0] - self.lander.position.x)

        angle = self.lander.current_angle
        angle = 1 if angle == 0 else abs(angle - 360) if angle > 180 else angle
        score /= angle

        velocity = 500 - (self.lander.velocity.x + self.lander.velocity.y)
        score += velocity

        return score

    def on_quit(self):
        """Quits the game"""
        if self.total_games > 0:
            win_ratio = self.won_games / self.total_games
            print(f'NN win ratio: {win_ratio:.4%}, Games: {self.total_games}')
        pygame.quit()
        sys.exit()

    def in_a_menu(self, on_menus, game_modes):
        """Management of what to do, when the player is on a menu"""
        result_menu = self.result_menu
        main_menu = self.main_menu

        if on_menus[1] or on_menus[2]:
            score = self.score_calculation()
            result_menu.draw_result_objects(self.screen, on_menus[1], score)
        else:
            main_menu.draw_buttons(self.screen)

        # main_menu.draw_buttons(self.screen)
        for event in pygame.event.get():
            if on_menus[0]:
                main_menu.check_hover(event)
                button_clicked = main_menu.check_button_click(event)
                main_menu.draw_buttons(self.screen)
                if button_clicked > -1:
                    game_modes[button_clicked] = True
                    on_menus[0] = False
                    self.game_started = True
                    if game_modes[2]:
                        self.total_games += 1

            elif on_menus[1] or on_menus[2]:
                result_menu.check_hover(event)
                on_menus[0] = result_menu.check_back_main_menu(event)
                result_menu.draw_result_objects(self.screen, on_menus[1], self.score_calculation())
                if on_menus[0]:
                    on_menus[1] = False
                    on_menus[2] = False

    def neural_network_action(self):
        """
        @type state: list
        """
        action = self.predictor.predict(self.state)
        self.controller.up = action < 3
        self.controller.left = action in (0, 3)
        self.controller.right = action in (1, 4)
        self.action = action

    def create_background_image(self):
        config_data = self.config_data
        background_image = pygame.image.load(config_data['BACKGROUND_IMG_PATH']).convert_alpha()
        return pygame.transform.scale(background_image, config_data['DIM'])

    def run_game(self, background_image, data_collector, on_menus, game_modes):
        if game_modes[-1]:
            self.on_quit()

        if self.game_started:
            self.game_start(game_modes[2])
            self.state = data_collector.get_state(self.lander, self.surface)

        if any(on_menus):
            self.in_a_menu(on_menus, game_modes)
        else:
            if self.game_started:
                self.update_objects()
                self.game_started = False
            self.handler.handle(pygame.event.get())
            if game_modes[2]:
                self.neural_network_action()

            self.screen.blit(background_image,(0,0))

            if self.handler.first_key_press:
                self.update_objects()
                if game_modes[1]:
                    data_collector.save_state(self.state, self.controller)
            self.sprites.draw(self.screen)

            self.check_if_game_ended(on_menus, game_modes, data_collector)
            game_over = on_menus[1] or on_menus[2]
            self.update_state(game_over, data_collector.get_state(self.lander, self.surface))

            if game_over:
                if game_modes[2]:
                    self.restart_game()
                    self.state = data_collector.get_state(self.lander, self.surface)
                    on_menus[1], on_menus[2] = [False] * 2
                else:
                    self.game_started = False
                    for index, _ in enumerate(game_modes):
                        game_modes[index] = False

        # surface_sprites.draw(self.screen)
        pygame.display.flip()
        self.fps_clock.tick(self.fps)

    def main_loop(self):
        """Perform main loop"""
        pygame.font.init() # you have to call this at the start,
        background_image = self.create_background_image()
        data_collector = DataCollection()

        # booleans for what the game state is
        on_menus = [True, False, False] # Main, Won, Lost
        # Game modes: Play Game, Data Collection, Neural Net, Quit
        game_modes = [False] * 4

        # Initialize
        while True:
            self.run_game(background_image, data_collector, on_menus, game_modes)

    def update_state(self, done, next_state):
        if self.predictor.is_rl:
            reward = self.get_reward()
            step = self.state, self.action, reward, next_state, done
            self.predictor.memorize(step)
            batch_size = 16
            if len(self.predictor.memory) > batch_size:
                self.predictor.replay(batch_size)
        self.state = next_state

    def restart_game(self):
        self.total_games += 1
        self.game_start(True)

    def get_reward(self):
        dimmensions = self.config_data['DIM']
        has_lost = self.lander.surface_collision(self.surface) or \
                self.lander.window_collision(dimmensions)
        has_won = self.lander.landing_pad_collision(self.surface)
        x_target = abs(self.surface.centre_landing_pad[0] - self.lander.position.x)
        y_target = abs(self.surface.centre_landing_pad[1] - self.lander.position.y)
        distance = x_target + y_target
        score = self.score_calculation()
        return (score / 1600) / 2 + 0.5 if has_won else \
               0 if has_lost else (distance / 1000) / 2

    def update_objects(self):
        # update the speeds and positions of the objects in game
        self.game_logic.update(0.2)

    def setup_lander(self, config_data):
        lander = Lander(config_data['LANDER_IMG_PATH'],
                        [config_data['SCREEN_WIDTH'] / 2, config_data['SCREEN_HEIGHT'] / 2],
                        Vector(0, 0),
                        self.controller)
        self.game_logic.add_lander(lander)
        return lander

    def game_start(self, ai_is_playing):
        config_data = self.config_data
        self.controller = Controller()
        self.handler = EventHandler(self.controller, self)
        self.handler.first_key_press = ai_is_playing
        self.lander = self.setup_lander(config_data)
        self.surface = Surface(config_data['DIM'])

        self.sprites = pygame.sprite.Group()
        self.sprites.add(self.lander)
        self.sprites.add(self.surface)

    def check_if_game_ended(self, on_menus, game_modes, data_collector):
        collided_window = self.lander.window_collision(self.config_data['DIM'])
        if self.lander.landing_pad_collision(self.surface):
            on_menus[1] = True
            if game_modes[2]:
                self.won_games += 1
            if game_modes[1]:
                data_collector.write_to_file()
                data_collector.reset()
        elif self.lander.surface_collision(self.surface) or collided_window:
            on_menus[2] = True
            data_collector.reset()
