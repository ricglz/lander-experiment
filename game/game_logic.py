class GameLogic:
    lander = None

    def __int__(self):
        pass

    def add_lander(self, lander):
        self.lander = lander

    def update(self, delta_time):
        self.lander.update_lander(delta_time)
