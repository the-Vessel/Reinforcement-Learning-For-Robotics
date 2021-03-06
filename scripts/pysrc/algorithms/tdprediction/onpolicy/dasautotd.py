import numpy as np
from scipy.sparse import csc_matrix as sp
from pysrc.algorithms.tdprediction.tdprediction import TDPrediction
from pysrc.utilities.kanerva_coding import BaseKanervaCoder
from pysrc.utilities.Prototype_MetaGradientDescent import MetaGradientDescent

class TD(TDPrediction):
    """Does Not Use Replacing Traces"""

    def __init__(self, config):
        """    Constructor """
        self.mu = 0.01
        self.tau = 1/10000.

        self.nf = config['nf']
        self.th = np.zeros(self.nf)
        self.v = np.zeros(self.nf)
        self.h = np.zeros(self.nf)
        self.ones = np.ones(self.nf)
        self.z = np.zeros(self.nf)
        try:
          self.initalpha = config['initalpha'] / config['active_features']
        except KeyError:
          self.initalpha = config['initalpha']
        print("here", self.initalpha)
        self.alpha = np.ones(self.nf)*self.initalpha
        print("here", self.alpha)

    def initepisode(self):
        self.z = np.zeros(self.nf)

    def step(self, params):
        phi = params['phi']
        r = params['R']
        phinext = params['phinext']
        g = params['g']
        l = params['l']
        gnext = params['gnext']

        effective_step_size = np.dot(self.alpha * phi, phi) - np.dot(g * self.alpha * phi, phinext)
        # print(np.nonzero(effective_step_size))
        delta = r + gnext*np.dot(phinext, self.th) - np.dot(phi, self.th)
        self.v = np.maximum(
            np.abs(delta*phi*self.h),
            (self.tau * effective_step_size * np.abs(delta * phi * self.h) - self.v)
        )
        self.alpha = self.alpha * np.exp(np.where(self.v == 0, 0, (self.mu * delta * phi * self.h) / self.v))
        print([self.alpha[i] for i in np.nonzero(self.alpha)])
        m = np.maximum(effective_step_size, self.ones)
        self.alpha /= m
        self.z = g * l * self.z + phi
        self.th += self.alpha * delta * self.z
        self.h = self.h * (self.ones-effective_step_size) + self.alpha * delta * phi


class TDR(TDPrediction):
    """ Uses Replacing Traces """

    def __init__(self, config):
        """    Constructor """
        self.mu = 0.01
        self.tau = 1 / 10000.

        self.nf = config['nf']
        self.th = np.zeros(self.nf)
        self.v = np.zeros(self.nf)
        self.h = np.zeros(self.nf)
        self.ones = np.ones(self.nf)
        self.z = np.zeros(self.nf)
        try:
          self.initalpha = config['initalpha'] / config['active_features']
        except KeyError:
          self.initalpha = config['initalpha']
        self.alpha = np.ones(self.nf)*self.initalpha

    def initepisode(self):
        self.z = np.zeros(self.nf)

    def step(self, params):
        phi = params['phi']
        r = params['R']
        phinext = params['phinext']
        g = params['g']
        l = params['l']
        gnext = params['gnext']

        effective_step_size = np.dot(self.alpha * phi, phi) - np.dot(g * self.alpha * phi, phinext)
        delta = r + gnext*np.dot(phinext, self.th) - np.dot(phi, self.th)
        self.v = np.maximum(
            np.abs(delta*phi*self.h),
            (self.tau * effective_step_size * np.abs(delta * phi * self.h) - self.v)
        )
        self.alpha = self.alpha * np.exp(np.where(self.v == 0, 0, (self.mu * delta * phi * self.h) / self.v))
        m = np.maximum(effective_step_size, self.ones)
        self.alpha /= m
        self.z = g * l * self.z * (phi == 0.) + (phi != 0.) * phi
        self.th += self.alpha * delta * self.z
        self.h = self.h * (self.ones-effective_step_size) + self.alpha * delta * phi

    def monitor_step(self, params):
        phi = params['phi']
        r = params['R']
        phinext = params['phinext']
        g = params['g']
        l = params['l']
        gnext = params['gnext']

        effective_step_size = np.dot(self.alpha * phi, phi) - np.dot(g * self.alpha * phi, phinext)
        delta = r + gnext*np.dot(phinext, self.th) - np.dot(phi, self.th)
        self.v = np.maximum(
            np.abs(delta*phi*self.h),
            (self.tau * effective_step_size * np.abs(delta * phi * self.h) - self.v)
        )
        self.alpha = self.alpha * np.exp(np.where(self.v == 0, 0, (self.mu * delta * phi * self.h) / self.v))
        m = np.maximum(effective_step_size, self.ones)
        self.alpha /= m
        self.z = g * l * self.z * (phi == 0.) + (phi != 0.) * phi
        self.th += self.alpha * delta * self.z
        self.h = self.h * (self.ones-effective_step_size) + self.alpha * delta * phi
        return effective_step_size, delta, self.alpha, self.h

    def estimate(self, phi):
        return np.dot(phi, self.th)


class TDR_Kanerva(TDR):

    def __init__(self, config):
        self.mu = 0.01
        self.tau = 1 / 10000.

        self.nf = config['nf']
        self.th = np.zeros(self.nf)
        self.v = np.zeros(self.nf)
        self.h = np.zeros(self.nf)
        self.ones = np.ones(self.nf)
        self.z = np.zeros(self.nf)

        try:
          self.initalpha = config['initalpha'] / config['active_features']
        except KeyError:
          self.initalpha = config['initalpha']

        self.alpha = np.ones(self.nf) * self.initalpha
        self.mgd = MetaGradientDescent(_startingPrototypes=self.nf, _dimensions=4)

    def step(self, params):
        phi = params['phi']
        r = params['R']
        phinext = params['phinext']
        g = params['g']
        l = params['l']
        gnext = params['gnext']

        obs = phi

        phi = self.mgd.get_features(phi)
        phinext = self.mgd.get_features(phinext)

        effective_step_size = np.dot(self.alpha * phi, phi) - np.dot(g * self.alpha * phi, phinext)
        delta = r + gnext * np.dot(phinext, self.th) - np.dot(phi, self.th)
        self.v = np.maximum(
            np.abs(delta * phi * self.h),
            (self.tau * effective_step_size * np.abs(delta * phi * self.h) - self.v)
        )
        self.alpha = self.alpha * np.exp(np.where(self.v == 0, 0, (self.mu * delta * phi * self.h) / self.v))
        m = np.maximum(effective_step_size, self.ones)
        self.alpha /= m
        self.z = g * l * self.z * (phi == 0.) + (phi != 0.) * phi
        self.th += self.alpha * delta * self.z
        self.h = self.h * (self.ones - effective_step_size) + self.alpha * delta * phi
#        self.kanerva.update_prototypes(self.alpha, delta, phi, self.th)

#    def estimate(self, phi):
#          return np.dot(self.kanerva.get_features(phi), self.th)

        self.mgd.update_prototypes(obs, self.alpha, delta, self.th)


    def estimate(self, phi):
        phi = self.mgd.get_features(phi)
        return np.dot(phi, self.th)
