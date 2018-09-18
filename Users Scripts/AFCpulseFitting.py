import numpy
from scipy.optimize import minimize
from matplotlib import pyplot as plt

def pulseFunc(t0,amp,N):
    return numpy.concatenate((numpy.zeros(int(t0)), amp*numpy.ones(N-int(t0))), axis=None)

def AFCpulseFitting(burnThroughPulseVolts):

    N = len(burnThroughPulseVolts)

    fun  = lambda p: sum((burnThroughPulseVolts - pulseFunc(p[0],p[1],N)) ** 2)
    bnds =((1,N-1),(0,None))
    res = minimize(fun, numpy.array([0, 1], dtype=numpy.float64), method="SLSQP", bounds = bnds)
    t0, amp = res.x
    func = pulseFunc(t0,amp,N)

    return t0, amp, func