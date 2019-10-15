
from sklearn.metrics import pairwise_distances_argmin
import numpy as np
import getData
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import os

def find_clusters(X, n_clusters, rseed=2):
    # 1. Randomly choose clusters
    rng = np.random.RandomState(rseed)
    i = rng.permutation(X.shape[0])[:n_clusters]
    centers = X[i]
    
    while True:
        # 2a. Assign labels based on closest center
        labels = pairwise_distances_argmin(X, centers)
        
        # 2b. Find new centers from means of points
        new_centers = np.array([X[labels == i].mean(0) for i in range(n_clusters)])
        
        # 2c. Check for convergence
        if np.all(centers == new_centers):
            break
        centers = new_centers
    
    return centers, labels
folders = os.listdir("eventChunkData/")

numberOfCenters =4

for folder in folders:
    data = getData.getEventChunkData(folder)
    pts = np.asarray(data)
    centers, labels = find_clusters(pts,numberOfCenters)
    plt.scatter(pts[:, 0], pts[:, 1], c=labels, s=10, cmap='viridis')
plt.show()
