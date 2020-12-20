import math

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f'X = {self.x}, Y = {self.y}'

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def scalar_multiply(self, scalar):
        """Applied a scalar multiplication with the current vector"""
        return Vector(self.x * scalar, self.y * scalar)

    def rotate(self, theta):
        """Applied a rotation with the current vector"""
        theta = math.radians(theta)
        x = (self.x * math.cos(theta)) - (self.y * math.sin(theta))
        y = (self.x * math.sin(theta)) + (self.y * math.cos(theta))
        return Vector(x, y)

    def normalize_vector(self):
        """Normalize current vector"""
        distance = self.length()
        return Vector(self.x / distance, self.y / distance)

    def length(self):
        """Get length/distance of the current vector"""
        x2 = self.x * self.x
        y2 = self.y * self.y
        return math.sqrt((x2 + y2))

    def clone(self):
        """Return new copy of the vector"""
        return Vector(self.x, self.y)
