import numpy
import math
from scipy.optimize import curve_fit
from scipy.signal import decimate
from scipy.signal import resample_poly
from scipy import fftpack

def sigmoid(t,timeConst):
    return 1/(1+numpy.exp(-t+timeConst))

# volts and Time are numpy vectors!
def carefulDecimation(volts,Time,dec):

    voltsZeroMean  = volts-numpy.mean(volts)
    y              = fftpack.fft(voltsZeroMean)
    y              = abs(y[1:math.floor(len(y)/2)])
    y              = y/max(abs(y))
    y[abs(y)<0.01] = 0

    referencePower = sum(abs(y))/len(y)

    lenVec    = 1000000
    powerDrop = []
    exponent  = 1
    while lenVec > 2:

        yFiltered = abs(y[0:math.ceil(len(y)/(2**exponent))])
        lenVec    = len(yFiltered)

        newPower  = sum(abs(yFiltered))/lenVec

        powerDrop.append(newPower/referencePower)

        exponent = exponent + 1

    goalFunc = numpy.asarray([x / max(powerDrop) for x in powerDrop])
    t        = numpy.arange(1,len(powerDrop)+1)

    init_vals = [10]
    best_vals, _ = curve_fit(sigmoid,t,goalFunc, p0=init_vals)

    new_t = numpy.linspace(1,len(powerDrop),1000)
    func  = sigmoid(new_t,best_vals)

    index = numpy.where(func>0.02)[0][0]

    r    = math.floor(index/1000*len(powerDrop))

    if dec == 1:
        Y    = volts
        time = Time
        for i in range(r):
            Y    = decimate(Y,2)
            time = decimate(time,2)

    if dec == 0:
        Y    = resample_poly(volts,1,math.ceil(len(volts)/(2**r)))
        time = resample_poly(Time,1,math.ceil(len(volts)/(2**r)))

    threshold = numpy.mean(Y)

    index1 = numpy.where(Y>threshold)[0][0]
    index2 = numpy.where(Y>threshold)[0][-1]

    Yfinal = Y[index1:index2]
    Tfinal = time[index1:index2]

    return Yfinal, Tfinal, r