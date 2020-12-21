"""Util module for managing tensorflow models"""
from tensorflow.keras.layers import Dense
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam

def create_sequential_model(layers):
    """
    Create a sequential model using the layers passed as param

    @layers: list
    """
    model = Sequential(layers)
    model.compile(
        optimizer=Adam(learning_rate=1e-3),
        loss=SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy']
    )
    return model

def create_best_sequential():
    """Creates the best sequential architecture"""
    layers = [
        Dense(83, activation='tanh', input_shape=(7,)),
        Dense(100, activation='tanh'),
        Dense(90, activation='tanh'),
        Dense(94, activation='tanh'),
        Dense(46, activation='tanh'),
        Dense(6, activation='softmax')
    ]
    return create_sequential_model(layers)
