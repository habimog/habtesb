# -*- coding: utf-8 -*-

import numpy

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
        print("pdf: {}".format(self.prob))
        
        choices = []
        for it in range(0, 5):
            choices.append(numpy.random.choice(["trident1", "trident2", "trident3"],
                                               p=[self.prob["trident1"], self.prob["trident2"], self.prob["trident3"]]))
        print("Servers choosen: {}".format(choices))

        choice = max(set(choices), key=choices.count)
        action = self.actions[choice]
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
   
'''
if __name__ == "__main__":
    rl = RlAgent()
    action = rl.takeAction()
    rl.learn(action, 300, 100)
'''
