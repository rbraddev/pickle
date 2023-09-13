class Basket:
    def __init__(self):
        self.items: dict = {}


class Session:
    def __init__(self, basket=None):
        self.basket: Basket = basket


class User:
    def __init__(self, username: str, department: str):
        self.username: str = username
        self.department: str = department