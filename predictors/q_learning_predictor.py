"""Module containing Q-Learning predictor"""
from collections import deque
from random import random, randint, sample

from numpy import amax, argmax, array

from extra.model import create_rl_model

class QLearningPredictor():
    gamma = 0.95
    epsilon = 1
    epsilon_min = 0.01
    epsilon_decay = 0.995
    is_rl = True

    def __init__(self, scaler):
        """
        @type scaler: MinMaxScaler
        """
        self.memory = deque(maxlen=2000)
        self.model = create_rl_model()
        self.scaler = scaler

    def memorize(self, step):
        """
        Memorize the current step

        @param step: Tuple containing state, action, reward, next_state
                     and done in that order
        @type step: (list, int, float, list, bool)
        """
        self.memory.append(step)

    def scaled_state(self, state):
        """
        Scale the state using the predictor scaler

        @creturn: ndarray
        """
        return self.scaler.transform(state)

    def predict(self, state):
        """
        Makes a prediction based on the state provided

        @creturn: int
        """
        if random() <= self.epsilon:
            return randint(0, 5)
        prediction = self.model.predict(self.scaled_state(state))[0]
        return argmax(prediction)

    def replay(self, batch_size):
        """Replay a sequence of steps to learn from them"""
        print('Replay')
        minibatch = sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                scaled = self.scaled_state(next_state)
                target += self.gamma * amax(self.model.predict(scaled)[0])
            target_f = self.model.predict(self.scaled_state(state))
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
