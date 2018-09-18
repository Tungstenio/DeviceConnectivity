import numpy
from carefulDecimation import carefulDecimation
from AFCpeakFitting import AFCpeakFitting
from AFCpulseFitting import AFCpulseFitting
from numpy import genfromtxt

from matplotlib import pyplot as plt

def next_power_of_2(x):
    return 1 if x == 0 else 2**(x - 1).bit_length()

def stepFindConv(volts):
    func = numpy.array(volts)
    func -= numpy.average(func)
    step = numpy.hstack((numpy.ones(len(func)), -1 * numpy.ones(len(func))))

    func_conv_step = numpy.convolve(func, step, mode='valid')
    return numpy.argmax(func_conv_step)

def calcEfficiency(I0, d0Volts, d0d1Volts):

    d0Log   = -numpy.log(d0Volts / I0)
    d0d1Log = -numpy.log(d0d1Volts / I0)
    d1Log   = d0d1Log - d0Log

    eff = (d1Log / 2)**2 * numpy.exp(-d0Log) * numpy.exp(-d1Log / 2) * numpy.exp(-7 / 4)
    eff_pc = eff * 100

    return eff_pc

def afc_fitting(afcFreqSpan):

    filename    = 'dataAnalysisAFC.csv'
    # afcFreqSpan = findFreqSpan(filename)

    data_array = genfromtxt(filename, delimiter=',')

    data_first_column  = []
    data_second_column = []
    for i in range(len(data_array)):
        data_first_column.append(data_array[i][0])
        data_second_column.append(data_array[i][1])

    timeNP  = numpy.asarray(data_first_column)
    voltsNP = numpy.asarray(data_second_column)

    dec = 0
    volts,time,r = carefulDecimation(voltsNP,timeNP,dec)

    step_index = stepFindConv(volts)

    voltsAFC = volts[0:step_index]
    timeAFC  = time[0:step_index]

    peakFitFunc, d0Volts, d0d1Volts = AFCpeakFitting(timeAFC, voltsAFC, afcFreqSpan, 2**r)

    voltsPulse = volts[step_index:]
    t0, I0, pulseFitFunc = AFCpulseFitting(voltsPulse)

    fitFunc = numpy.concatenate((peakFitFunc, pulseFitFunc), axis=None)

    eff_pc = calcEfficiency(I0,d0Volts,d0d1Volts)
    print(eff_pc)

    return eff_pc,time,volts,fitFunc

afcFreqSpan = 2e9
eff,time,volts,fitFunc = afc_fitting(afcFreqSpan)

fig, ax = plt.subplots()
ax.plot(time, volts)
ax.plot(time, fitFunc)
plt.show()