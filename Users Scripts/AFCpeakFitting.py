import numpy
from scipy import fftpack
from scipy.signal import find_peaks
from scipy.optimize import minimize
from scipy.signal.windows import triang

def rect(T):
    """create a centered rectangular pulse of width $T"""
    return lambda t: (-T/2 <= t) & (t < T/2)

def pulse_train(t, at, width):
    """create a train of pulses over $t at times $at and shape $shape"""
    shape      = rect(width)
    oneZeroVec = numpy.float32(numpy.sum(shape(t - at[:, numpy.newaxis]), axis=0))
    notConv    = 1
    index      = 0
    while notConv == 1:
        if oneZeroVec[index] == 1:
            oneZeroVec[index:index+width] = triang(int(width))
            index = index + width
        else:
            index = index + 1

        if index >= len(oneZeroVec):
            notConv = 0

    return oneZeroVec

def AFCpeakFitting(time,volts,afcFreqSpan,r):

    afcVolts = volts

    afcTime = time*afcFreqSpan*r
    dtAll = []
    for i in range(len(afcTime)-1):
        dtAll.append(abs(afcTime[i+1]-abs(afcTime[i])))
    dtAll   = numpy.asarray(dtAll)
    dt      = sum(dtAll)/len(dtAll)
    df      = 1/max(afcTime)
    F       = 1/dt
    f       = numpy.arange(0,F,df)

    y       = fftpack.fft(volts)

    firstPeak = max(abs(y[1:]))
    pos       = numpy.argmin((abs(y) - firstPeak) ** 2)
    freqPeaks = abs(f[pos])

    freqSep        = (1/freqPeaks)
    distPeaks      = numpy.floor(freqSep/dt)

    pks, _ = find_peaks(afcVolts, distance=distPeaks)

    timeFake = numpy.arange(len(afcTime))

    afcVolts = afcVolts.astype(numpy.float64)

    fun = lambda p: sum((afcVolts - (p[0] + p[1] * (pulse_train(timeFake, pks, int(p[2]))))) ** 2)
    res = minimize(fun, numpy.array([0, 1, distPeaks / 2], dtype=numpy.float64), method="Nelder-Mead")
    offset, amp, width = res.x
    func = offset + amp * pulse_train(timeFake, pks, int(width))

    d0 = numpy.max(func)
    d0d1 = numpy.min(func)
    return func, d0, d0d1

    # fun = lambda x: ((x[0] + x[1]*(pulse_train(timeFake,pks,x[2])))-afcVolts)
    # res = minimize(fun,(0,1,3))
    # print(res.x)

    # best_vals, _ = curve_fit(pulse_train, timeFake, afcVolts, p0=init_vals)
    # print(best_vals)
    # sig = pulse_train(
    #     t=timeFake,  # time domain
    #     at=best_vals[0],  # times of pulses
    #     width=best_vals[1]
    # )