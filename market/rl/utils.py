import random


class agent_selector:
    def __init__(self, agents: list, reorder=False):
        self.agents = agents
        self.reorder = reorder
        self.agent_selection = -1
    
    def next(self):
        if self.agent_selection == len(self.agents) - 1 and self.reorder:
            random.shuffle(self.agents)
        self.agent_selection = (self.agent_selection + 1) % len(self.agents)
        return self.agents[self.agent_selection]

    def reset(self):
        self.agent_selection = -1
    
    def is_last(self):
        return self.agent_selection == len(self.agents) - 1
