import random
import string

class Room():
    def __init__(self, mongo):
        self.rooms =  mongo.rooms

    def create(self, name):
        pass
    
    def join(self, name, code):
        pass

    def leave(self, name, code):
        pass

    def leave(self, name, code):
        pass

    def generate_code(self, length):
        return ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(length))
