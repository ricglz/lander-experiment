"""GA for obtain the best architecture for a supervise predictor"""
from random import randint

from tensorflow.keras.layers import Dense
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.models import Sequential
from deap import algorithms, base, creator, tools

from datasets import create_datasets

training_set, validation_data, _ = create_datasets()

def evaluate(individual):
    """
    @param individual: A list of numbers representing the architecture
    @type individual: list
    """
    int_layers = list(map(int, individual))
    create_layers = lambda units: Dense(units, activation='relu')
    layers = [Dense(int_layers[0], activation='relu', input_shape=(7,))]
    layers += list(map(create_layers, int_layers[1:]))
    layers.append(Dense(6, activation='softmax'))
    model = Sequential(layers)
    model.compile(
        optimizer='adam',
        loss=SparseCategoricalCrossentropy(),
        metrics=['accuracy']
    )
    history = model.fit(
        training_set[0], training_set[1], batch_size=16,
        epochs=5, validation_data=validation_data, verbose=0
    ).history
    return history['accuracy'][-1],

creator.create('FitnessMax', base.Fitness, weights=(1.0,))
creator.create('Individual', list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

toolbox.register('attribute', randint, 10, 101)
toolbox.register('mate', tools.cxTwoPoint)
toolbox.register('mutate', tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
toolbox.register('select', tools.selTournament, tournsize=3)
toolbox.register('evaluate', evaluate)

if __name__ == "__main__":
    hall_of_fame = tools.HallOfFame(1)
    for size in range(5, 11):
        toolbox.register('individual', tools.initRepeat, creator.Individual, toolbox.attribute, size)
        toolbox.register('population', tools.initRepeat, list, toolbox.individual)
        population = toolbox.population(n=10)
        current_hall_of_fame = tools.HallOfFame(1)
        algorithms.eaSimple(population, toolbox, 0.6, 0.2, 10, halloffame=current_hall_of_fame)
        hall_of_fame.insert(current_hall_of_fame[0])
    print(hall_of_fame[0])
