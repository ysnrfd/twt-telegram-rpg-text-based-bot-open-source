class EventSystem:
    def __init__(self):
        self.subscribers = {}
    
    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def publish(self, event_type, data=None):
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback(data)

# Global event system
event_system = EventSystem()

# Common events
PLAYER_CREATED = "player_created"
EQUIPMENT_ADDED = "equipment_added"
LEVEL_UP = "level_up"
SKILL_UPGRADED = "skill_upgraded"