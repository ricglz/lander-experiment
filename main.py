from game_loop import GameLoop

def get_config_file():
    keys = []
    values = []
    file = open('config.txt', 'r')
    for line in file:
        line_split = line.split(',')
        for individual in line_split:
            individual = individual.replace(' ', '')
            individual = individual.replace('\n', '')
            content = individual.split('=')
            keys.append(content[0])
            values.append(content[1])
    return dict(zip(keys, values))


def start_game_window():
    config_data = get_config_file()
    game = GameLoop(config_data)
    game.main_loop(config_data)

if __name__ == "__main__":
    start_game_window()
