# -*- coding: utf-8 -*-

import random

''' RL Agent
'''
class RlAgent():
    ''' Constructor
    '''
    def __init__(self):
        self.lamda = 0.1 # Learning rate
        self.prob = {
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
        r = random.uniform(0.0, 1.0) 
        print("random number picked from uniform distribution: {}".format(r))

        print("probabilities: {}".format(self.prob))

        if r <= self.prob["trident1"]:
            action = self.actions["trident1"]
        elif r <=  self.prob["trident1"] + self.prob["trident2"]:
            action = self.actions["trident2"]
        else:
            action = self.actions["trident3"]

        print("Action choosen: {}".format(action))
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
            self.prob["trident1"] += self.lamda * feedback * (1.0 - self.prob["trident1"])
            self.prob["trident2"] += self.lamda * feedback * (0.0 - self.prob["trident2"])
            self.prob["trident3"] += self.lamda * feedback * (0.0 - self.prob["trident3"])
        elif action == "trident2.vlab.cs.hioa.no":
            self.prob["trident1"] += self.lamda * feedback * (0.0 - self.prob["trident1"])
            self.prob["trident2"] += self.lamda * feedback * (1.0 - self.prob["trident2"])
            self.prob["trident3"] += self.lamda * feedback * (0.0 - self.prob["trident3"])
        elif action == "trident3.vlab.cs.hioa.no":
            self.prob["trident1"] += self.lamda * feedback * (0.0 - self.prob["trident1"])
            self.prob["trident2"] += self.lamda * feedback * (0.0 - self.prob["trident2"])
            self.prob["trident3"] += self.lamda * feedback * (1.0 - self.prob["trident3"])
        else:
            print("Error: invalid action")

        print("Updated probabilities: {}".format(self.prob))

    ''' Reward function
        @param maxTemp: maximum Temperature
        @param hostTemp: host temperature 
    '''
    def _getFeedback(self, maxTemp, hostTemp):
        feedback = 1.0 - (hostTemp / maxTemp)
        return feedback if feedback >= 0.0 else 0.0