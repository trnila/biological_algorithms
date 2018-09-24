#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

measurements = pd.read_csv("./measurement.csv").set_index('cities')
measurements.plot(marker='.')
plt.xlabel("cities")
plt.ylabel("time [sec]")
plt.title("time to find all possible trajectories between cities")

plt.show()
