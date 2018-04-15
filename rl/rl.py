# -*- coding: utf-8 -*-

import random

''' RL Agent
'''
class RlAgent():
    ''' Constructor
    '''
    def __init__(self):
        self.lamda = 0.1 # Learning rate
        self.p = {
            "trident1" : 1.0 / 3.0, 
            "trident2" : 1.0 / 3.0, 
            "trident3" : 1.0 / 3.0
        }
        self.actions = {
            "trident1" : "trident1.vlab.cs.hioa.no", 
            "trident2" : "trident2.vlab.cs.hioa.no", 
            "trident3" : "trident3.vlab.cs.hioa.no"
        }

    ''' Choose Action 
    '''
    def takeAction(self): 
        r = random.uniform(0, 1) 
        if r < self.p["trident1"]:
            action = self.actions["trident1"]
        elif r <  self.p["trident1"] + self.p["trident2"]:
            action = self.actions["trident2"]
        else:
            action = self.actions["trident3"]

        return action

    ''' Learn
        @param action: action choosen
        @param maxTemp: maximum Temperature
        @param hostTemp: host temperature
    '''
    def learn(self, action, maxTemp, hostTemp):   
        # Update 
        feedback = self._getFeedback(maxTemp, hostTemp)
        
        if action == "trident1.vlab.cs.hioa.no":
            self.p["trident1"] += self.lamda * feedback * (1.0 - self.p["trident1"])
            self.p["trident2"] += self.lamda * feedback * (0.0 - self.p["trident2"])
            self.p["trident3"] += self.lamda * feedback * (0.0 - self.p["trident3"])
        elif action == "trident2.vlab.cs.hioa.no":
            self.p["trident1"] += self.lamda * feedback * (0.0 - self.p["trident1"])
            self.p["trident2"] += self.lamda * feedback * (1.0 - self.p["trident2"])
            self.p["trident3"] += self.lamda * feedback * (0.0 - self.p["trident3"])
        elif action == "trident3.vlab.cs.hioa.no":
            self.p["trident1"] += self.lamda * feedback * (0.0 - self.p["trident1"])
            self.p["trident2"] += self.lamda * feedback * (0.0 - self.p["trident2"])
            self.p["trident3"] += self.lamda * feedback * (1.0 - self.p["trident3"])
        else:
            print("Error: invalid action")

        print("Updated probabilities: {}".format(self.p))

    ''' Reward function
        @param maxTemp: maximum Temperature
        @param hostTemp: host temperature 
    '''
    def _getFeedback(self, maxTemp, hostTemp):
        feedback = 1 - (hostTemp / maxTemp)
        return feedback

''' Main
'''
if __name__ == "__main__":
    maxTemp = 100
    hostTemp = 10

    agent = RlAgent()
    action = agent.takeAction()
    print(agent.learn(action, maxTemp, hostTemp))