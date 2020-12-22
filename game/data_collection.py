"""Module for collection data and getting state"""
import pandas as pd
from numpy import array

columns = [
    'Current speed', 'Velocity (X)', 'Velocity (Y)', 'Current Angle',
    'Target (X)', 'Target (Y)', 'Distance To Surface', 'Action'
]

def parse_into_action(up, left, right):
    """Parse into all the possible actions that the user can make"""
    return 0 if up and left and not right else \
           1 if up and not left and right else \
           2 if up and not left and not right else \
           3 if not up and left and not right else \
           4 if not up and not left and right else 5

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
        current_velocity = lander.velocity
        current_speed = current_velocity.length()
        current_angle = lander.current_angle
        x_target = surface.centre_landing_pad[0] - lander.position.x
        y_target = surface.centre_landing_pad[1] - lander.position.y
        dist_to_surface = surface.polygon_rect.topleft[1] - lander.position.y

        state = [current_speed, current_velocity.x, current_velocity.y, current_angle]
        state += [x_target, y_target, dist_to_surface]

        return array(state).reshape(1, -1)

    def save_state(self, state, controller):
        """
        Save the current state of the game and the outputs to be able to
        predict it later on.

        @type state: ndarray
        @type lander: Lander
        @type controller: Controller
        """
        action = parse_into_action(controller.up, controller.left, controller.right)
        state_list = state.tolist()
        state_list.append(action)
        self.buffer.append(state_list)

    def write_to_file(self):
        """Appends buffer data in data.csv"""
        dataframe = pd.DataFrame(self.buffer, columns=columns)
        dataframe.to_csv('data.csv', index=False, header=None, mode='a')

    def reset(self):
        """Clears the buffer"""
        self.buffer.clear()
