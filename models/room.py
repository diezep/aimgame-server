from pymongo import ReturnDocument
import random
import string

class Room():
    
    def __init__(self, mongo):
        self.rooms =  mongo.local.rooms

    def create(self, sid):
        print('Create game room called:', sid)
        code = self.generate_code(5)
        nRoom = {
            'code':code,
            'admin':sid,
            'state':'WAITING_FOR_PLAYERS',
            'players' : []
        }
        self.rooms.insert_one(nRoom)
        
        return nRoom
    
    def join(self, name, code, sid):    
        print('Join to game called:', sid)
        _room = self.rooms.find_one_and_update({'code':code}, {
            '$push': {
                'players' :{
                'sid'   : sid,
                'name' : name,
                'score': 0
                } 
            }
        },
        return_document=ReturnDocument.AFTER)
        return _room

    def leave(self, sid, code=None):
        print('Leave from game called:', sid)
        if code is not None:
            room = self.rooms.find_one_and_update({'code':code} , {
                '$pull': {
                    'players':{
                        'sid' : sid
                    }
                }
            })
        else:
            room = self.rooms.find_one_and_update({},
            {
                '$pull': {
                    f'players':{
                        '$elemMatch':{
                            'sid' : sid
                        }
                    }   
                }
            }, return_document=ReturnDocument.AFTER)
        return room
    def generate_code(self, length):
        return ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(length))
