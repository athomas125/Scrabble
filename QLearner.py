import random as rand

import numpy as np


class QLearner(object):
    """
    This is a Q learner object.

    :param num_states: The number of states to consider.
    :type num_states: int
    :param num_actions: The number of actions available..
    :type num_actions: int
    :param alpha: The learning rate used in the update rule. Should range between 0.0 and 1.0 with 0.2 as a typical value.
    :type alpha: float
    :param gamma: The discount rate used in the update rule. Should range between 0.0 and 1.0 with 0.9 as a typical value.
    :type gamma: float
    :param rar: Random action rate: the probability of selecting a random action at each step. Should range between 0.0 (no random actions) to 1.0 (always random action) with 0.5 as a typical value.
    :type rar: float
    :param radr: Random action decay rate, after each update, rar = rar * radr. Ranges between 0.0 (immediate decay to 0) and 1.0 (no decay). Typically 0.99.
    :type radr: float
    :param dyna: The number of dyna updates for each regular update. When Dyna is used, 200 is a typical value.
    :type dyna: int
    :param verbose: If “verbose” is True, your code can print out information for debugging.
    :type verbose: bool
    """
    def __init__(
        self,
        num_states=100,
        num_actions=4,
        alpha=0.2,
        gamma=0.9,
        rar=0.5,
        radr=0.99,
        dyna=0,
        verbose=False,
    ):
        """
        Constructor method
        """
        self.verbose = verbose
        self.num_actions = num_actions
        self.num_states = num_states
        self.alpha = alpha
        self.gamma = gamma
        self.rar = rar
        self.radr = radr
        self.dyna = dyna
        self.s = 0
        self.a = 0
        self.Q = np.zeros((self.num_states, self.num_actions))
        self.experiences = []

    def querysetstate(self, s):
        """
        Update the state without updating the Q-table

        :param s: The new state
        :type s: int
        :return: The selected action
        :rtype: int
        """
        self.s = s
        action = np.argmax(self.Q[s])
        self.a = action
        if self.verbose:
            print(f"s = {s}, a = {action}")
        return action

    def query(self, s_prime, r):
        """
        Update the Q table and return an action

        :param s_prime: The new state
        :type s_prime: int
        :param r: The immediate reward
        :type r: float
        :return: The selected action
        :rtype: int
        """
        # update Q table
        a_prime = np.argmax(self.Q[s_prime])
        self.Q[self.s][self.a] = (1 - self.alpha)*self.Q[self.s][self.a] + \
                                 self.alpha*(r + self.gamma * self.Q[s_prime][a_prime])

        self.experiences.append([self.s, self.a, s_prime, r])

        if self.dyna != 0:
            exp_list = np.random.randint(0, len(self.experiences), size=self.dyna)
            for i in range(0,self.dyna):
                ds, da, dsp, dr = self.experiences[exp_list[i]]
                dap = np.argmax(self.Q[dsp])
                self.Q[ds][da] = (1 - self.alpha) * self.Q[ds][da] + \
                                         self.alpha * (dr + self.gamma * self.Q[dsp][dap])

        if np.random.rand() < self.rar:
            action = np.random.randint(0, self.num_actions)
        else:
            action = np.argmax(self.Q[s_prime])

        self.rar *= self.radr
        self.s = s_prime
        self.a = action

        if self.verbose:
            print(f"s = {s_prime}, a = {action}, r={r}")
        return action
