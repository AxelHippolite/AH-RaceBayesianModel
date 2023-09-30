class Pilot:
    def __init__(self, id, code, previous, pts):
        self.id = id
        self.code = code
        self.previous = previous
        self.pit_stops = pts
        self.cumulative = [sum(previous[0:i:1]) for i in range(0, len(previous) + 1)][1:]
        self.pace, self.tire_age, self.delta = 0, 0, 0
    
    def update(self, lap, front):
        self.pace = (self.previous[-1] - self.previous[-5])/4
        self.cumulative = [sum(self.previous[0:i:1]) for i in range(0, len(self.previous) + 1)][1:]
        self.update_tire_age(lap)
        self.update_delta(front)
    
    def update_tire_age(self, lap):
        if lap in self.pit_stops:
            self.tire_age = 1
        else:
            self.tire_age += 1

    def update_delta(self, front):
        self.delta = front.cumulative[-1] - self.cumulative[-1] if front is not None else 0