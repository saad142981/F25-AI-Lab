
class ClassroomAgent:
    def __init__(self):
        self.prev_mode = None

    def act(self, temp, occupied):
        if not occupied:
            target = "ECO"
        elif temp > 26:
            target = "COOL"
        elif temp < 20:
            target = "WARM"
        else:
            target = "IDLE"

        if target != self.prev_mode:
            command_outcome = "COMMAND"
        else:
            command_outcome = "NO_COMMAND"

        self.prev_mode = target
        return target, command_outcome

agent = ClassroomAgent()
percepts = [(29, True), (29, True), (20, True),
            (26, True), (19, True), (29, False)]
for step, percept in enumerate(percepts, 1):
    prev_mode = agent.prev_mode
    target, command_outcome = agent.act(*percept)
    print(step, prev_mode, percept, target, command_outcome)

