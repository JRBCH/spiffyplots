"""
Plotting examples for SpiffyPlots
"""
import numpy as np
import matplotlib.pyplot as plt
from spiffyplots import MultiPanel

# Functions
# # # # # # # #

def hist(axis):
    axis.hist()



data = {
            "scatter-x": np.random.randn(200),
            "scatter-y": np.random.randn(200),
            "hist-gauss": np.random.randn(500),
            "hist-gamma": np.random.gamma(5, 8, 500),
            "heatmap": np.random.rand(100).reshape(10, 10),
            "timeseries": np.array(
                [
                    np.sin(np.arange(0, 25, 0.1)) + np.random.randn(250)
                    for _ in range(20)
                ]
            ),
            "timeseries-true": np.sin(np.arange(0, 25, 0.1)),
        }

fig = MultiPanel(grid=(4, 2, 3), figsize=(8, 6), labels=True)
plt.show()
