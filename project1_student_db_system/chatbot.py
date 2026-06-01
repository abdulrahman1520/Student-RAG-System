from engines.base import ChatEngine

class Chatbot:
    def __init__(self, engine: ChatEngine):
        self.engine = engine
    
    def respond(self, query):
        return self.engine.answer(query)