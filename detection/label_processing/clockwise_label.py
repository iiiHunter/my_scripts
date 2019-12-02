import numpy as np


def order_point(coor):
    coor = [int(item) for item in coor]
    arr = np.array(coor).reshape([4, 2])
    sum_ = np.sum(arr, 0)
    centroid = sum_ / arr.shape[0]
    theta = np.arctan2(arr[:, 1] - centroid[1], arr[:, 0] - centroid[0])
    sort_points = arr[np.argsort(theta)]
    sort_points = sort_points.reshape([-1])
    sort_points = sort_points.reshape([8]).tolist()
    sort_points = [str(item) for item in sort_points]
    return sort_points
