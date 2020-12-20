"""Module for collection data and getting state"""
import pandas as pd

columns = [
    'Current speed', 'Velocity (X)', 'Velocity (Y)', 'Current Angle',
    'Target (X)', 'Target (Y)', 'Distance To Surface', 'Thrust', 'New Vel (Y)',
    'New Vel (X)', 'New Angle', 'Left', 'Right'
]

class DataCollection:
    def __init__(self):
        self.buffer = []

    @staticmethod
    def get_state(lander, surface):
        """
        Get the current state of the game depending if it's desired to gather
        all the data or not

        @type lander: Lander
        @type surface: Surface
        """
        # inputs
        current_velocity = lander.velocity
        current_speed = current_velocity.length()
        current_angle = lander.current_angle
        x_target = surface.centre_landing_pad[0] - lander.position.x
        y_target = surface.centre_landing_pad[1] - lander.position.y
        dist_to_surface = surface.polygon_rect.topleft[1] - lander.position.y

        # create comma separated string row
        state = [current_speed, current_velocity.x, current_velocity.y, current_angle]
        state += [x_target, y_target, dist_to_surface]

        return state

    def save_state(self, state, lander, controller):
        """
        Save the current state of the game and the outputs to be able to
        predict it later on.

        @type state: list
        @type lander: Lander
        @type controller: Controller
        """
        # outputs
        thrust = int(controller.up)
        new_vel_y = lander.velocity.y
        new_vel_x = lander.velocity.x

        turning = [int(controller.left), int(controller.right)]
        new_angle = lander.current_angle

        state += [thrust, new_vel_y, new_vel_x, new_angle, turning[0], turning[1]]

        self.buffer.append(state)

    def write_to_file(self):
        """Appends buffer data in data.csv"""
        dataframe = pd.DataFrame(self.buffer, columns=columns)
        dataframe.to_csv('data.csv', index=False, header=None, mode='a')

    def reset(self):
        self.buffer.clear()
