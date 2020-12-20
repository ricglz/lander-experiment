import pygame

from .collision_utility import CollisionUtility
from .vector import Vector

class Lander(pygame.sprite.Sprite):
    gravity = Vector(0, 0.5)
    current_angle = 0
    is_going_down = True

    def __init__(self, filepath, location, velocity, controller):
        """
        @type filepath: str
        @type location: list
        @type velocity: Vector
        @type controller: Controller
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(filepath)
        self.original_image = self.image
        self.rect = self.image.get_rect()
        image_left = location[0] + 16
        image_top = location[1] + 28
        self.rect.left = image_left
        self.rect.top = image_top
        self.velocity = velocity
        self.position = Vector(location[0], location[1])
        self.controller = controller

    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.original_image, angle)

    def landing_pad_collision(self, surface):
        return self.rect.colliderect(surface.landing_pad)

    def surface_collision(self, surface):
        if self.rect.colliderect(surface.polygon_rect):
            collided = CollisionUtility.check_lander_collision_with_surface(self, surface)
            return collided

    def window_collision(self, screen_dimensions):
        return CollisionUtility.check_gameobject_window_collision(self, screen_dimensions)

    def update_lander(self, delta_time):
        movement = Vector(0, 0)
        if self.controller.up:
            movement = (movement + Vector(0, -1)).scalar_multiply(delta_time)

        theta = 10 * delta_time if self.controller.left else \
                -10 * delta_time if self.controller.right else 0

        self.current_angle += theta
        if self.current_angle < 0:
            self.current_angle += 360
        elif self.current_angle >= 360:
            self.current_angle = self.current_angle % 360

        movement = movement.rotate(-self.current_angle)

        air_resistance = Vector(-0.2, 0) if self.velocity.x > 0 else Vector(0.2, 0)
        air_resistance = air_resistance.scalar_multiply(delta_time)
        gravity = self.gravity.scalar_multiply(delta_time)

        last_velocity = self.velocity.clone()
        self.velocity += air_resistance + gravity + movement
        if self.velocity.length() > 8:
            self.velocity = last_velocity

        last_position = self.position
        self.position += self.velocity
        self.is_going_down = self.position.y - last_position.y > 0

        location = [self.position.x, self.position.y]
        self.rect.left, self.rect.top = location
        self.rotate(self.current_angle)
