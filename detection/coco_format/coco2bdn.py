import json
import numpy as np
from shapely.geometry import LineString, Polygon
import matplotlib.patches as patches
import os
import matplotlib.pyplot as plt
import cv2


def coco2bdn(source_json, target_json):
    source_dict = json.load(open(source_json, "r"))
    annotations = source_dict["annotations"]
    obj_list = []
    '''
    {"image_id": 450, 
    "segmentation": [[1403.0, 832.5, 97.0, 832.5, 96.5, 720.0, 1403.0, 719.5, 1403.0, 832.5]], 
    "width": 1497, 
    "bbox": [97.0, 720.0, 1307.0, 113.0], 
    "area": 147691, 
    "category_id": 1, 
    "iscrowd": 0, 
    "id": 6717, 
    "height": 2378}
    '''
    count = 0
    for obj in annotations:
        # print(obj["id"])
        # print(obj)
        if not len(obj["segmentation"]) == 1:
            count += 1
            continue
        segs = obj["segmentation"][0][:8]
        xt = [segs[ikpart] for ikpart in range(0, len(segs), 2)]
        yt = [segs[ikpart] for ikpart in range(1, len(segs), 2)]
        # cross
        l1 = LineString([(xt[0], yt[0]), (xt[2], yt[2])])
        try:
            l2 = LineString([(xt[1], yt[1]), (xt[3], yt[3])])
        except:
            print(xt)
            print(yt)
            count += 1
            continue
        p_l1l2 = l1.intersection(l2)
        poly1 = Polygon([(xt[0], yt[0]), (xt[1], yt[1]),
                         (xt[2], yt[2]), (xt[3], yt[3])])
        if not poly1.is_valid:
            print('Not valid polygon found. This bounding box is removing ...')
            count += 1
            continue
        if not p_l1l2.within(poly1):
            print('Not valid intersection found. This bounding box is removing ...')
            count += 1
            continue
        if poly1.area <= 10:
            print('Text region too small. This bounding box is removing ...')
            count += 1
            continue

        mean_x = np.mean(xt)
        mean_y = np.mean(yt)
        xt_sort = np.sort(xt)
        yt_sort = np.sort(yt)
        xt_argsort = list(np.argsort(xt))
        yt_argsort = list(np.argsort(yt))
        # indexing
        ldx = []
        for item in xt_argsort:
            ldx.append(yt_argsort.index(item))
        all_types = [[1, 2, 3, 4], [1, 2, 4, 3], [1, 3, 2, 4], [1, 3, 4, 2], [1, 4, 2, 3], [1, 4, 3, 2],
                     [2, 1, 3, 4], [2, 1, 4, 3], [2, 3, 1, 4], [2, 3, 4, 1], [2, 4, 1, 3], [2, 4, 3, 1],
                     [3, 1, 2, 4], [3, 1, 4, 2], [3, 2, 1, 4], [3, 2, 4, 1], [3, 4, 1, 2], [3, 4, 2, 1],
                     [4, 1, 2, 3], [4, 1, 3, 2], [4, 2, 1, 3], [4, 2, 3, 1], [4, 3, 1, 2], [4, 3, 2, 1]]
        all_types = [[all_types[iat][0] - 1, all_types[iat][1] - 1, all_types[iat][2] - 1, all_types[iat][3] - 1] for
                     iat in range(24)]
        match_type = all_types.index(ldx)

        half_x = (xt_sort + mean_x) / 2
        half_y = (yt_sort + mean_y) / 2

        # add key_point
        keypoints = []
        keypoints.append(mean_x)
        keypoints.append(mean_y)
        keypoints.append(2)
        for i in range(4):
            keypoints.append(half_x[i])
            keypoints.append(mean_y)
            keypoints.append(2)
        for i in range(4):
            keypoints.append(mean_x)
            keypoints.append(half_y[i])
            keypoints.append(2)
        try:
            keypoints.append(int(p_l1l2.x))
            keypoints.append(int(p_l1l2.y))
            keypoints.append(2)
        except Exception as e:
            print(e)
            # print('EIntersection found. This bounding is removing ...')
            continue

        obj["keypoints"] = keypoints
        obj["match_type"] = match_type
        obj_list.append(obj)

    source_dict["annotations"] = obj_list
    with open(target_json, "w") as f:
        json.dump(source_dict, f)
    print(count)


def vis_bdn_json(source_json="/home/sol/Project/general_text_det/data/annotations_bdn/test_scene.json"):
    save_dir = "/home/sol/Project/general_text_det/data/annotations_bdn/vis"
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    data_root = "/home/sol/Project/general_text_det/data"
    target_image_id = 36
    source_dict = json.load(open(source_json, "r"))
    annotations = source_dict["annotations"]
    images = source_dict["images"]
    ids = [item["id"] for item in source_dict["images"]]
    for target_image_id in ids:
        L = []
        for item in annotations:
            if item["image_id"] == target_image_id:
                L.append(item)
        for item in images:
            if item["id"] == target_image_id:
                target_image = item
                break
        target_image_path = os.path.join(data_root, target_image["file_name"])
        if not os.path.exists(target_image_path):
            print("File not found!")
        print(target_image_path)
        im = cv2.imread(target_image_path).astype("uint8")

        segms = []
        for item in L:
            segm = [int(it) for it in item["segmentation"][0]]
            segms.append([(segm[0], segm[1]), (segm[2], segm[3]), (segm[4], segm[5]), (segm[6], segm[7])])
        square = np.array(segms)
        cv2.polylines(im, square, 1, 255, 2)

        point_size = 1
        point_color = (0, 0, 255)  # BGR
        thickness = 4  # 可以为 0 、4、8

        # 要画的点的坐标
        points_list = [(160, 160), (136, 160), (150, 200), (200, 180), (120, 150), (145, 180)]

        for point in points_list:
            cv2.circle(im, point, point_size, point_color, thickness)
        # plt.imshow(im)
        # plt.axis('off')
        # plt.show()
        cv2.imwrite(os.path.join(save_dir, str(target_image_id) + ".jpg"), im)


if __name__ == "__main__":
    source_json = "/home/sol/Project/general_text_det/data/mlt19_others_train.json"
    target_json = "/home/sol/Project/general_text_det/data/mlt19_others.json"
    coco2bdn(source_json, target_json)
    vis_bdn_json()

    # d = json.load(open("/home/sol/Project/general_text_det/data/mlt19_others_train.json", "r"))
    # L = d["annotations"]
    # print(len(L))
    # print(L[0])
