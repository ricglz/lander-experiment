import pygame
from pygame.locals import *

class EventHandler:
    first_key_press = True

    def __init__(self, controller, game):
        """
        @type controller: Controller
        """
        self.controller = controller
        self.game = game

    def handle(self, event_list):
        for event in event_list:
            if event.type == QUIT:
                self.quit()
            if event.type == KEYDOWN:
                self.keyboard_controller_down(event)
                self.first_key_press = True
            if event.type == KEYUP:
                self.keyboard_controller_up(event)
            if event.type == MOUSEBUTTONDOWN:
                self.mouse_down()
            if event.type == MOUSEBUTTONUP:
                self.mouse_up()

    def keyboard_controller_down(self, event):
        if event.key == 273 or event.key == 1073741906:
            self.controller.up = True
        elif event.key == 276 or event.key == 1073741904:
            self.controller.left = True
        elif event.key == 275 or event.key == 1073741903:
            self.controller.right = True
        elif event.key == 113 or event.key == 27:
            self.quit()

    def keyboard_controller_up(self, event):
        if event.key == 273 or event.key == 1073741906:
            self.controller.up = False
        if event.key == 276 or event.key == 1073741904:
            self.controller.left = False
        if event.key == 275 or event.key == 1073741903:
            self.controller.right = False

    def quit(self):
        self.game.on_quit()

    def mouse_down(self):
        self.controller.mouse_pos = pygame.mouse.get_pos()
        self.controller.mouse = True

    def mouse_up(self):
        self.controller.mouse = False
