"""
Classifying SWE Images with SWEpy
=================================

Learn how to quickly generate optimal jenks classified imagery with SWEpy's tools.

This guide covers using the ``swepy.classify`` module to find the optimal number of
jenks classes for a given image and produce a quick and dirty plot displaying the findings.
"""

########################################################################################
# Import Packages
# ---------------
#
# To begin, import the needed packages.

import swepy.classify as classify
import swepy.process as proc
import matplotlib.pyplot as plt
import numpy as np

########################################################################################
# Load SWE Array
#
# We can use swepy to load in tb19/tb37 files or we can load a .npy file into memory
# But in this example we will just open a numpy array for simplicity

swe = np.load("ex_data/swe_lg_img.npy")

########################################################################################
# Determine Optimal Number of Classes
#
# The optimal number of classes in a jenks classification is based on the threshold
# GVF value. Meaning optimization is reached when the GVF value is maximized given a max value
# between 0 and 1.
#
# Here we will demonstrate the different optimal number of classes for varying threshold values
#
# When the threshold is set very high, like 0.99, it takes much longer to optimize, and returns
# significantly more classes!

print(classify.optimal_jenk(swe.ravel(), 0.5))

print(classify.optimal_jenk(swe.ravel(), 0.6))

print(classify.optimal_jenk(swe.ravel(), 0.7))

print(classify.optimal_jenk(swe.ravel(), 0.8))

print(classify.optimal_jenk(swe.ravel(), 0.9))

print(classify.optimal_jenk(swe.ravel(), 0.99))


########################################################################################
# Plot an Example Jenks Classification
#
# SWEpy includes a simple fucntion to generate you a plot of you area of interest
# classified using jenks. This can be done manually, but to save time, there is a
# basic funtion provided.
#
# This is a good way to view that lower values a GVF threshold result in more generalized
# classes. This can be a good thing, as we want classes to be grouped together if possible.
# There is a sweet spot where we have good class definition without over complicating the
# class distribution.

classify.plot_jenks(swe, 0.8)
