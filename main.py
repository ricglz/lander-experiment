"""Main module of the program"""
from game.game_loop import GameLoop
from predictors.supervised_predictor import SupervisedPredictor
from extra.datasets import create_datasets

def get_config_file():
    """Gets dictionary containing the config values"""
    keys = []
    values = []
    file = open('config.txt', 'r')
    for line in file:
        line_split = line.split(',')
        for individual in line_split:
            content = individual.replace(' ', '').replace('\n', '').split('=')
            keys.append(content[0])
            values.append(content[1])
    return dict(zip(keys, values))

def create_predictor():
    train_set, val_set, scaler = create_datasets()
    predictor = SupervisedPredictor()
    predictor.fit(train_set, val_set)
    predictor.set_scaler(scaler)
    return predictor

def start_game_window():
    """Starts the game window"""
    config_data = get_config_file()
    predictor = create_predictor()
    GameLoop(config_data, predictor).main_loop(config_data)

if __name__ == "__main__":
    start_game_window()
