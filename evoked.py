# -*- coding: utf-8 -*-
"""
Created on Sat Dec 24 17:26:30 2016

@author: rgshe

import a trace as an abf file using the neo module and plot
it in a new figure window.
"""

from neo import io
import numpy as np
from itertools import groupby
from operator import itemgetter


def unpack(trace):
    """reads an abf file and outputs the data as a numpy
    array as well as the time points in seconds.
    ----------------------------------------------------
    Usage:
        import evoked as ev
        signal, times = ev.unpack('trace')
    """

    read = io.AxonIO(filename=trace)
    bl = read.read_block(cascade=True, lazy=False)

    signal = np.empty([len(bl.segments[0].analogsignals[0]), len(bl.segments)])
    for i in range(0, len(bl.segments)):
        sweep = bl.segments[i].analogsignals[0]
        sweep = np.squeeze(sweep)
        signal[:, i] = sweep

    for i, asig in enumerate(bl.segments[0].analogsignals):
        times = asig.times.rescale('s').magnitude

    return signal, times


def average(signal):
    "baseline_mean = []"

    for i in range(0, len(signal[1])):
        sweep = signal[:, i]
        sweep = np.squeeze(sweep)
        dy = np.diff(sweep)

        j = 0
        baseline = []
        while(abs(dy[j]) < 200):
            baseline.append(sweep[j])
            j = j + 1

        signal[:, i] = signal[:, i] - np.mean(baseline)

    sweep_average = np.mean(signal, 1)
    return sweep_average


def artifacts(sweep_average):
    
    """there's somethign off with the way i'm identifying artifacts
    it's too sensitive to the variable shape and amplitude of the facts.
    I think a better way may be to search for the sign inversion"""

    ddy = np.diff(np.diff(sweep_average))
    fact_index = np.where(abs(ddy[1500:]) > 300)  # index protocol sensitive
    index_list = []
    events = []
    index_list = fact_index[0]
    for k, g in groupby(enumerate(index_list), lambda x: x[1] - x[0]):
        events.append(list(map(itemgetter(1), g)))
        events[len(events)-1] = list(map(lambda x: x + 1500, events[len(events)-1]))
        events[(len(events)-1)].append(max(events[len(events)-1])+1)
        events[(len(events)-1)].append(max(events[len(events)-1])+1)

    return events


def amplitude(average, events):

    if len(events) == 1:
        amplitude = min(average[max(events[0]):])
        return amplitude

    else:
        amplitude = np.empty(len(events))
        norm_amp = np.empty(len(events))
        for i in range(0, len(events)):
            if (i <= (len(events) - 2)) and (len(events) > 2):
                amplitude[i] = min(average[max(events[i]):min(events[i+1])]) \
                               - average[max(events[i])]
                norm_amp[i] = amplitude[i] / amplitude[0]
            else:
                amplitude[i] = min(average[max(events[i]):]) \
														- average[max(events[i])]
            norm_amp[i] = amplitude[i] / amplitude[0]

    return amplitude, norm_amp

    """there's something off with running this in KO conditions"""