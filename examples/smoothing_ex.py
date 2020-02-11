"""
Why Filter Time Series with Sav-Gol
===================================

See why we choose to use a savitsky golay filter to smooth
the time vectors of our SWE cubes.

This guide covers a couple examples of loading in data and
manually applying the filters that are built into SWEpy.
"""

########################################################################################
# Import packages
# ---------------
#
# To begin, import needed packages.
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import swepy.process as proc
import numpy as np

########################################################################################
# Open arrays into memory using swepy's built in functionality
#
# The 37H band is a higher resolution (3.125km) compared to the 19H band (6.25km)
# SWEpy automatically downsamples the 37H band to match the size of the 19H band.

tb19 = np.load("ex_data/filtered19", allow_pickle=True)
tb37 = np.load("ex_data/filtered37", allow_pickle=True)

########################################################################################
# Create a smoothed version of one time vector in swe
#
# We will see in a second that the raw swe data is not very smooth. There
# are lots of spikes, which makes it difficult to infer any information from
# the curve itself, like rate of accumulation.
#
# To avoid this, we can use a sav-gol filter to increase the signal to noise ratio

swe_clean = proc.safe_subtract(tb19, tb37)

tb19_filtered = proc.apply_filter_mphelper(tb19)
tb37_filtered = proc.apply_filter_mphelper(tb37)

swe_filtered = proc.safe_subtract(tb19_filtered, tb37_filtered)

########################################################################################
# Visualize difference in raw and smoothed data
#
# In this plot, we can see how much better our clean version of the data looks
# versus the raw data that we have access to. The smooth curve is generally clean
# enough to derive information like rates.

x = np.array(range(len(swe_clean)))
start = 320
end = 600

fig, ax = plt.subplots(1, 1, figsize=(30, 15))
plt.plot(x[start:end], swe_clean[start:end, 4, 4])
plt.plot(x[start:end], swe_filtered[start:end, 4, 4], color="red")
plt.grid(0.25, zorder=3)
plt.xlabel("Day of Timeseries", fontsize=20)
plt.ylabel("SWE (mm)", fontsize=20)
plt.title("Applying Savgol Filter to SWE Data", fontsize=26)
plt.show()
