import numpy as np
from scipy import stats
from scipy.stats import norm
import matplotlib.pyplot as plt
import matplotlib
from sklearn.metrics import pairwise_distances_argmin
import typing
from typing import Dict, Tuple, Sequence, List

def paddBins(bins2: np.ndarray, paddTimes: int):

    # pad left & right
    difference = bins2[1] - bins2[0]
    for i in range(paddTimes):
        bins2= np.insert(bins2,0,bins2[0] -(difference*(i+1)))
    
    for i in range(paddTimes):
        bins2= np.append(bins2,bins2[len(bins2)-1]+difference*(i+1) )

    
    return bins2

def plot_hist(data: list, axes, plot_major: int, plot_minor: int, plot_color: str, log_values: bool)->matplotlib.lines.Line2D :
    """
    Plots only the hist.
    """
    y, x, _ = axes[plot_major][plot_minor].hist(data, bins=400, color=plot_color,edgecolor='black', linewidth=1.2, normed=1)
    x = paddBins(x,100)
    
    (mu, sigma) = norm.fit(data)
    y = stats.norm.pdf(x, mu, sigma)
    accuracy = 0.002
    if log_values == False:
        accuracy = 0.00002
    while(y[0] < accuracy):
        y = np.delete(y,0)
        x = np.delete(x,0)
    while(y[len(y)-1] < accuracy):
        y = np.delete(y,len(y)-1)
        x = np.delete(x,len(x)-1)

    l = axes[plot_major][plot_minor].plot(x, y, linewidth=2)
    
    return l[0]

def find_clusters(X: list, n_clusters: int, rseed: int=2) -> Tuple[list, np.ndarray]:
    # 1. Randomly choose clusters
    rng = np.random.RandomState(rseed)
    i = rng.permutation(X.shape[0])[:n_clusters]
    centers = X[i]
    
    while True:
        # 2a. Assign labels based on closest center
        labels = pairwise_distances_argmin(X, centers)
        
        # 2b. Find new centers from means of points
        new_centers = np.array([X[labels == i].mean(0)
                                for i in range(n_clusters)])
        
        # 2c. Check for convergence
        if np.all(centers == new_centers):
            break
        centers = new_centers
    
    return centers, labels

def plotKmeans(data,axes, row, columnIndex,numberOfCenters):
    pts = np.asarray(data)
    centers, labels = find_clusters(pts,numberOfCenters)
    axes[row][columnIndex].scatter(pts[:, 0], pts[:, 1], c=labels, s=10, cmap='viridis')
    axes[row][columnIndex].scatter(centers[:, 0], centers[:, 1], c='red')

def centerAllGuas(lines: List[matplotlib.lines.Line2D],axesIndex: int, labels: List[str], title: str, axes: np.ndarray):
        maxHeight = 0#Get the largest y value in all the lines
        for line in lines:
            if np.max(line._y) > maxHeight:
                maxHeight = np.max(line._y)


        for i,line in enumerate(lines):
            max_y = np.max(line._y) 
            index = np.where(line._y == max_y)
            offset = line._x[index[0][0]]
            for j in range(len(line._x)):
                line._x[j] = line._x[j]- offset
            row = 0
            if "NoPolarizer" in labels[i]:
                row = 1
                labels[i] = labels[i].replace(" NoPolarizer","")
            labels[i] =labels[i].replace(" Off Events","")
            labels[i] =labels[i].replace(" On Events","")
            labels[i] =labels[i].replace(" All Events","")
            labels[i] =labels[i].replace("  "," ")
            axes[axesIndex][row].plot(line._x,line._y/maxHeight, label=labels[i])
        axes[axesIndex][1].title.set_text("Non-Polarized "+title)
        axes[axesIndex][0].title.set_text("Polarized " +title)
        axes[axesIndex][0].legend(loc=1, prop={'size':11})
        axes[axesIndex][1].legend(loc=1, prop={'size': 11})


def showAllGuas(lines: List[matplotlib.lines.Line2D], labels: List[str], axesIndex: int, title: str, axes: np.ndarray):

    max_height = 0

    for line in lines:
        if np.max(line._y) > max_height:
            max_height = np.max(line._y)

    for i, line in enumerate(lines):
        shiftX = line._x[0]
        for j, x in enumerate(line._x):
            line._x[j] = x - shiftX
        shiftY = line._y[0]
        for j, y in enumerate(line._y):
            line._y[j] = y - shiftY
        row = 0
        if "NoPolarizer" in labels[i]:
            labels[i] = labels[i].replace(" NoPolarizer","")
            row = 1
        
        labels[i] =labels[i].replace(" Off Events","")
        labels[i] =labels[i].replace(" On Events","")
        labels[i] =labels[i].replace(" All Events","")
        labels[i] =labels[i].replace("  "," ")
        axes[axesIndex][row].plot(line._x,line._y/max_height, label=labels[i])

    axes[axesIndex][1].title.set_text("Non-Polarized "+title)
    axes[axesIndex][0].title.set_text("Polarized " +title)
    axes[axesIndex][0].legend(loc=1, prop={'size':11})
    axes[axesIndex][1].legend(loc=1, prop={'size': 11})

def showFFT(data, file_count, folders):
    fftX = np.linspace(0.0, 1.0/(2.0*(1.0 / 800.0)), file_count/2)

    polLabels =[]
    polFreq = []
    noPolLabels = []
    noPolFreq = []

    for i, y in enumerate(data):
        if("no pol" in folders[i] ):
            noPolLabels.append(folders[i])
            noPolFreq.append(y)
        else:
            polLabels.append(folders[i])
            polFreq.append(y)

        _, axes = plt.subplots(nrows=1, ncols=2, sharex=True, sharey=True)

    for i, y in enumerate(polFreq):
        axes[0].plot(fftX, 2.0/file_count * np.abs(y[:file_count//2]), label=polLabels[i].replace('Event Chunks', ''))

    axes[0].set_xlim(2,60)
    axes[0].legend()

    for i, y in enumerate(noPolFreq):
        axes[1].plot(fftX, 2.0/file_count * np.abs(y[:file_count//2]), label=noPolLabels[i].replace('Event Chunks', ''))

    axes[1].set_xlim(2,60)
    axes[1].legend()
    plt.show()