"""Module for creating and managing the main menu"""
import pygame

class MainMenu:
    def __init__(self, screen_dimension):
        self.colors=[(0,0,0), (128,128,128), (255,255,255)]
        self.top_left=(screen_dimension[0]/2, 100)

        font = pygame.font.SysFont("Times New Norman", 60)
        texts = ['Play Game', 'Data Collection', 'Neural Network', 'Quit']
        create_text_button = lambda text: font.render(text, True, self.colors[2])
        text_buttons = list(map(create_text_button, texts))

        left_initial = self.top_left[0] - 200
        create_rect_button = lambda values: pygame.Rect(
            left_initial, self.top_left[1] + 100 * values[0], 400, 80)
        rect_buttons = list(map(create_rect_button, enumerate(text_buttons)))

        create_button = lambda values: [text_buttons[values[0]], values[1], self.colors[0]]
        self.buttons = list(map(create_button, enumerate(rect_buttons)))

    def draw_buttons(self, screen):
        screen.fill(self.colors[2])
        for text, rect, color in self.buttons:
            pygame.draw.rect(screen, color, rect)
            screen.blit(text, rect)

    def onHover(self, num_button):
        self.buttons[num_button][2] = self.colors[1]

    def offHover(self, num_button):
        self.buttons[num_button][2] = self.colors[0]

    def check_hover(self, event):
        if event.type == pygame.MOUSEMOTION:
            for button in self.buttons:
                if (button[1].collidepoint(event.pos)):
                    button[2] = self.colors[1]
                else:
                    button[2] = self.colors[0]

    def check_button_click(self, event):
        # mouse button was clicked
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 1 == left mouse button, 2 == middle button, 3 == right button
            if event.button == 1:
                for i, button in enumerate(self.buttons):
                    if (button[1].collidepoint(event.pos)):
                        return i
        return -1
