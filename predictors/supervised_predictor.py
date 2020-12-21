"""Module containing supervised predictor"""
from numpy import array

import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import load_model

from extra.model import create_best_sequential

class SupervisedPredictor():
    def __init__(self, filepath=None, scaler=None):
        error_msg = 'Both filepath and scaler must be either None or not None'
        assert not bool(filepath) ^ bool(scaler), error_msg
        self.is_trained = filepath is not None
        self.model = create_best_sequential() if filepath is None else load_model(filepath)
        self.scaler = scaler

    def set_scaler(self, scaler):
        """Sets the scaler"""
        self.scaler = scaler

    def fit(self, training_set, validation_data):
        """
        @type training_set: (ndarray, ndarray)
        """
        callback = EarlyStopping(patience=10)
        self.model.fit(
            training_set[0], training_set[1], batch_size=10,
            epochs=100, validation_data=validation_data, callbacks=[callback]
        )
        self.is_trained = True

    def predict(self, inputs):
        """Makes a prediction using the model based on the inputs"""
        scaled_inputs = self.scaler.transform(array(inputs).reshape(1, -1))
        prediction = self.model.predict(scaled_inputs)[0]
        return tf.math.argmax(prediction)

    def save(self, filepath):
        self.model.save(filepath)
