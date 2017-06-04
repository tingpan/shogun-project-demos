# functions for creating kmeans notebook
from modshogun import *
import numpy as np
from numpy import array
import matplotlib.pyplot as plt
import json

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

    player_count = len(data[0])
    for k in range(5, 30):
        xs.append(k)
        _ys = []
        for i in range(1, 11):
            result, centers, radiuses = train_kmeans(k, data)
            for player_i in range(0, player_count):
                cluster_i = int(result[player_i])
                center = array([x[cluster_i] for x in centers])
                player = array([y[player_i] for y in data])
                _ys.append(np.sum((center - player)**2))
        ys.append(sum(_ys)/player_count)
    import matplotlib.pyplot as plt

    plt.plot(xs,ys)
    plt.show()

def get_result(k, data):
    centers = []
    result = []
    while True:
        result, centers, radiuses = train_kmeans(k, data)
        r = sum(radiuses)/13
        if r < 100:
            print(r)
            break
    return result, centers

def save_result(data):
    result, centers = get_result(13, data)
    with open('centers.json', 'w') as outfile:
        json.dump(centers.tolist(), outfile)

    output = {}
    for i, name in enumerate(names):
        output[name] = int(result[i])

    with open('result.json', 'w') as outfile:
        json.dump(output, outfile)

def draw_values(k, data, index):
    ind = np.arange(10)
    width = 0.5
    result, centers = get_result(k, data)
    headers = ['Transition', 'Isolation', 'PRBallHandler', 'PRRollman', 'Postup', 'Spotup', 'Handoff', 'Cut', 'OffScreen', 'OffRebound']
    fig, ax = plt.subplots()
    rects = plt.bar(ind, [values[index] for values in centers], width, color=[(min(x/10.0, 1), x/20.0, 0.55) for x in range(1,21,2)])
    ax.set_ylabel('Freq Rating')
    ax.set_title('Player Cluster')
    ax.set_xticks(ind)
    ax.legend(rects, headers)
    plt.show()


# draw_values(13, data, 0)

show_result(data)