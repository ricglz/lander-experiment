"""Main module of the program"""
from pandas import read_csv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from game.game_loop import GameLoop
from predictors.supervised_predictor import SupervisedPredictor

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

def create_datasets():
    dataset = read_csv('data.csv', header=None).drop_duplicates()
    scaler = MinMaxScaler()
    values = scaler.fit_transform(dataset)
    inputs, output = values[:, :-1], values[:, -1]
    train_x, val_x, train_y, val_y = train_test_split(inputs, output, test_size=0.3)
    return (train_x, train_y), (val_x, val_y), scaler

def create_predictor():
    train_set, val_set, scaler = create_datasets()
    predictor = SupervisedPredictor()
    predictor.fit(train_set, val_set)
    predictor.set_scaler(scaler)
    return predictor

def start_game_window():
    """Starts the game window"""
    config_data = get_config_file()
    GameLoop(config_data).main_loop(config_data)

if __name__ == "__main__":
    start_game_window()
