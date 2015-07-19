"""specifies the configuration for the algorithms"""
import numpy as np
import cPickle as pickle

alphas = 10**np.arange(-3, 0.1, .5)                                         #values for alpha sweep-over
lambdas = np.concatenate((np.arange(0, .9, .3), np.arange(.9, 1.01, .3)))    #values of lambda to sweep over

configs = [{'alpha': alpha, 'lmbda': lm} for alpha in alphas for lm in lambdas]
# configs = [{'alpha': 0.01, 'lmbda': 0.9},{'alpha': 0.01, 'lmbda': 0.9}]
f = open('configalg.pkl', 'wb')
print(len(configs))
pickle.dump(configs, f)