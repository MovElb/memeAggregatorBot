class StateManager:
    S_NULL = 0
    S_WAIT_URL_SUB = 1
    S_WAIT_URL_UNSUB = 2

    def __init__(self):
        self.state = {}

    def set_state(self, id, current_state=S_NULL):
        self.state[id] = current_state

    def get_state(self, id):
        return self.state.get(id, self.S_NULL)
