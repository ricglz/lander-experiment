"""Game loop logic"""
import sys

import pygame

from event_handler import EventHandler
from lander import Lander
from controller import Controller
from vector import Vector
from game_logic import GameLogic
from surface import Surface
from main_menu import MainMenu
from result_menu import ResultMenu
from data_collection import DataCollection

class GameLoop:
    controller = Controller()
    fps = 60
    fps_clock = pygame.time.Clock()
    game_logic = GameLogic()
    game_started = False
    lander = None
    main_menu = None
    myfont = None
    neuralnet = None
    object_list = []
    result_menu = None
    screen = None
    surface = None
    total_games = 0
    won_games = 0

    def __init__(self, config_data):
        self.handler = EventHandler(self.controller, self)
        self.config_data = config_data
        pygame.init()
        config_data['SCREEN_WIDTH'] = int(config_data['SCREEN_WIDTH'])
        config_data['SCREEN_HEIGHT'] = int(config_data['SCREEN_HEIGHT'])
        config_data['DIM'] = config_data['SCREEN_WIDTH'], config_data['SCREEN_HEIGHT']
        self.screen = pygame.display.set_mode(config_data['DIM'])
        pygame.display.set_caption('Lander game')
        pygame.display.set_icon(pygame.image.load(config_data['LANDER_IMG_PATH']))

    def score_calculation(self):
        score = 1000.0 - (self.surface.centre_landing_pad[0] - self.lander.position.x)

        angle = self.lander.current_angle
        angle = 1 if angle == 0 else abs(angle - 360) if angle > 180 else angle
        score /= angle

        velocity = 500 - (self.lander.velocity.x + self.lander.velocity.y)
        score += velocity

        return score

    def on_quit(self):
        if self.total_games > 0:
            win_ratio = self.won_games / self.total_games
            print(f'NN win ratio: {win_ratio:.4%}, Games: {self.total_games}')
        pygame.quit()
        sys.exit()

    def not_in_game(self, on_menus, game_modes):
        result_menu = self.result_menu
        main_menu = self.main_menu

        if on_menus[1] or on_menus[2]:
            score = self.score_calculation()
            result_menu.draw_result_objects(self.screen, on_menus[1], score)
        else:
            main_menu.draw_buttons(self.screen)
            # draw the version number
            textsurface = self.myfont.render('Version 1', False, (0, 0, 0))
            self.screen.blit(textsurface, (0, 0))

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

    def neural_network_action(self, data_collector):
        """
        @type data_collector: DataCollection
        """
        state = data_collector.get_state(self.lander, self.surface)
        nn_prediction = self.neuralnet.predict(state)
        self.controller.up = self.lander.velocity.y > nn_prediction[0]
        self.controller.right = self.lander.velocity.x < nn_prediction[1]
        self.controller.left = not self.controller.right

        if self.lander.current_angle > 30 and self.lander.current_angle < 330:
            ang_val = round((self.lander.current_angle - 30) / 300)
            self.lander.current_angle = 30 if ang_val == 0 else 330

    def main_loop(self, config_data):
        pygame.font.init()  # you have to call this at the start,
        # if you want to use this module you need to call pygame.font.init()
        self.myfont = pygame.font.SysFont('Comic Sans MS', 30)

        # create the group for visuals to be updated
        sprites = pygame.sprite.Group()

        # booleans for what the game state is
        on_menus = [True, False, False] # Main, Won, Lost

        # Game modes: Play Game, Data Collection, Neural Net, Quit
        game_modes = [False, False, False, False]

        # The main loop of the window
        background_image = pygame.image.load(config_data['BACKGROUND_IMG_PATH']).convert_alpha()
        background_image = pygame.transform.scale(background_image, config_data['DIM'])

        data_collector = DataCollection()
        self.main_menu = MainMenu(config_data['DIM'])
        self.result_menu = ResultMenu(config_data['DIM'])
        # Initialize
        while True:
            if game_modes[-1]:
                self.on_quit()

            # if game is started, initialize all objects
            if self.game_started:
                self.controller = Controller()
                self.handler = EventHandler(self.controller, self)
                sprites = pygame.sprite.Group()
                self.game_start(config_data, sprites)

            if on_menus[0] or on_menus[1] or on_menus[2]:
                self.not_in_game(on_menus, game_modes)
            else:
                if self.game_started:
                    self.update_objects()
                    self.game_started = False

                # game
                self.handler.handle(pygame.event.get())
                # check if data collection mode is activated
                if game_modes[2]:
                    self.neural_network_action(data_collector)

                self.screen.blit(background_image,(0,0))

                if self.handler.first_key_press:
                    self.update_objects()
                    if game_modes[1]:
                        state = data_collector.get_state(self.lander, self.controller)
                        data_collector.save_state(state, self.lander, self.controller)
                # then update the visuals on screen from the list
                sprites.draw(self.screen)
                # the win state and the score calculation
                collided_window = self.lander.window_collision(config_data['DIM'])
                if self.lander.landing_pad_collision(self.surface):
                    on_menus[1] = True
                    if game_modes[2]:
                        self.won_games += 1
                        # data_collector.write_to_file()
                        # data_collector.reset()
                    if game_modes[1]:
                        data_collector.write_to_file()
                        data_collector.reset()
                # check if lander collided with surface
                elif self.lander.surface_collision(self.surface) or collided_window:
                    on_menus[2] = True
                    data_collector.reset()

                game_over = on_menus[1] or on_menus[2]

                if game_modes[2]:
                    state = data_collector.get_state(self.lander, self.surface)
                    # feedback = state, self.get_reward(), game_over
                    # self.neuralnet.step_finished(feedback)
                    if game_over:
                        # self.neuralnet.episode_finished()
                        sprites = pygame.sprite.Group()
                        self.restart_game(sprites)
                        on_menus[1], on_menus[2], game_over = [False] * 3

                if game_over:
                    self.game_started = False
                    for index, _ in enumerate(game_modes):
                        game_modes[index] = False

            # surface_sprites.draw(self.screen)
            pygame.display.flip()
            self.fps_clock.tick(self.fps)

    def restart_game(self, sprites):
        self.total_games += 1
        self.controller = Controller()
        self.handler = EventHandler(self.controller, self)
        self.game_start(self.config_data, sprites)

    def get_reward(self):
        dimmensions = self.config_data['DIM']
        has_lost = self.lander.surface_collision(self.surface) or \
                self.lander.window_collision(dimmensions)
        has_won = self.lander.landing_pad_collision(self.surface)
        x_target = abs(self.surface.centre_landing_pad[0] - self.lander.position.x)
        y_target = abs(self.surface.centre_landing_pad[1] - self.lander.position.y)
        distance = x_target + y_target
        return self.score_calculation() * 1000 if has_won else \
                (-distance) * 50 if has_lost else (250 - x_target) + (250 - y_target)

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

    def game_start(self, config_data, sprites):
        self.lander = self.setup_lander(config_data)
        self.surface = Surface(config_data['DIM'])
        sprites.add(self.lander)
        sprites.add(self.surface)
