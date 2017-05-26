from modshogun import *
from numpy import array

def load_data():
    f = open('./play_freq.data')
    features = []
    names = []
    for line in f:
        words = line.rstrip().split(',')
        # Store player names
        names.append(words[0])
        # Store features of each player
        features.append([float(i) for i in words[1:]])

    f.close()

    return (array(features).T, names)

data, names = load_data()

def train_kmeans(k, data):
    train_features = RealFeatures(data)

    # calculate euclidean distance of features
    distance = EuclideanDistance(train_features, train_features)

    # initialize KMeans++ object
    kmeans = KMeans(k, distance, True)

    # training kmeans
    kmeans.train(train_features)

    # labels for data points
    result = kmeans.apply()
    centers = kmeans.get_cluster_centers()
    radiuses = kmeans.get_radiuses()

    return result, centers, radiuses

def show_result(data):
    ys = []
    xs = []

    for k in range(5, 40):
        xs.append(k)
        _ys = []

        for i in range(1, 151):
            result, centers, radiuses = train_kmeans(k, data)
            _ys.append(sum(radiuses)/k)

        ys.append(sum(_ys)/150)

    import matplotlib.pyplot as plt

    plt.plot(xs,ys)
    plt.show()

def get_result(k, data):
    centers = []
    result = []
    while True:
        result, centers, radiuses = train_kmeans(k, data)
        r = sum(radiuses)/13
        if r < 16.9:
            print(r)
            break
    return result, centers

import json

result, centers = get_result(13, data)
with open('centers.json', 'w') as outfile:
    json.dump(centers.tolist(), outfile)

output = {}
for i, name in enumerate(names):
    output[name] = int(result[i])

with open('result.json', 'w') as outfile:
    json.dump(output, outfile)