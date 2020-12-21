"""Util module for managing tensorflow models"""
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.models import Sequential

def create_sequential_model(layers):
    """
    Create a sequential model using the layers passed as param

    @layers: list
    """
    model = Sequential(layers)
    model.compile(
        optimizer=Adam(learning_rate=2e-3),
        loss=SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy']
    )
    return model
