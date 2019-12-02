#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os
import sys
import cv2
import numpy as np
from shapely.geometry import *
import random
random.seed(123)


IMAGE_DIR = '/home/sol/data/Datasets/CCHW_v5_0/CCHW_v5_0/image'
    
save_dir = '/home/sol/data/Datasets/CCHW_v5_0/CCHW_v5_0/annotations'  # output path
if not os.path.exists(save_dir):
    os.mkdir(save_dir)
image_files = []

subset_key = [("CCHW-WT", "HCTW-WT"), ("CCHW-WS", "HCTW-WS"), ("CCHW-WSF", "HCTW-WSF"), ("CCHW-SN", "HCTW-SN"), ("CCHW-EP", "HCTW-EP")]
with open("/home/sol/data/Datasets/CCHW_v5_0/CCHW_v5_0/train_new.json", "r") as f:
    d = json.loads(f.read())
for key_pair in subset_key:
    _, key = key_pair
    for item in d[key]:
        image_files.append(os.path.join(IMAGE_DIR, item["file_path"]))

print(image_files)
random.shuffle(image_files)
train_num = len(image_files)
print("train num", train_num)

dataset = {
    'licenses': [],
    'info': {},
    'categories': [],
    'images': [],
    'annotations': []
}

classes = ['text']
for i, cls in enumerate(classes, 1):
  dataset['categories'].append({
      'id': i,
      'name': cls,
      'supercategory': 'beverage',
      'keypoints': ['mean',
                    'xmin',
                    'x2',
                    'x3',
                    'xmax',
                    'ymin',
                    'y2',
                    'y3',
                    'ymax',
                    'cross']  # only for keypoints
  })


def get_category_id(cls):
  for category in dataset['categories']:
    if category['name'] == cls:
      return category['id']

j = 1
#import pdb;pdb.set_trace()
random.shuffle(image_files)
for index, im_path in enumerate(image_files):
  print('Processing: ', index)
  im = cv2.imread(im_path)
  height, width, _ = im.shape
  dataset['images'].append({
      'coco_url': '',
      'date_captured': '',
      'file_name': im_path.split("/image/")[-1],
      'flickr_url': '',
      'id': index,
      'license': 0,
      'width': width,
      'height': height
  })

  # f_index = open('/home/jingroup/storage/lcy/yuliang_mask/mask/data/mlt2019/test/index2oriImages.txt',"a")
  # f_index.writelines(str(int(index)) + ': '+ index + '.jpg' + '\n')

  anno_file = im_path.replace("/image/", "/label/").split(".")[0] + ".txt"
  if not os.path.exists(anno_file):
    print("label not found:", anno_file)
    exit(-1)
  with open(anno_file) as f:
    lines = [line for line in f.readlines() if line.strip()]
    for i, line in enumerate(lines):
      if i == 0:
        continue
      # print(line)
      parts = line.strip().split(',')[:-1]
      assert len(parts) == 8
      #print parts
      cls = 'text'
      xmin = min(int(parts[0]), int(parts[2]), int(parts[4]), int(parts[6]))
      ymin = min(int(parts[1]), int(parts[3]), int(parts[5]), int(parts[7]))
      xmax = max(int(parts[0]), int(parts[2]), int(parts[4]), int(parts[6]))
      ymax = max(int(parts[1]), int(parts[3]), int(parts[5]), int(parts[7]))
      width = max(0, xmax - xmin + 1)
      height = max(0, ymax - ymin + 1)
      #import pdb;pdb.set_trace()
      if width == 0 or height == 0:
        continue
      # add seg_shrink
      segs = [int(kkpart) for kkpart in parts]  # four points
      xt = [segs[ikpart] for ikpart in range(0, len(segs), 2)]
      yt = [segs[ikpart] for ikpart in range(1, len(segs), 2)]
      # cross
      l1 = LineString([(xt[0], yt[0]), (xt[2], yt[2])])
      l2 = LineString([(xt[1], yt[1]), (xt[3], yt[3])])
      p_l1l2 = l1.intersection(l2)
      poly1 = Polygon([(xt[0], yt[0]), (xt[1], yt[1]),
                       (xt[2], yt[2]), (xt[3], yt[3])])
      if not poly1.is_valid:
        print('Not valid polygon found. This bounding box is removing ...')
        continue
      if not p_l1l2.within(poly1):
        print('Not valid intersection found. This bounding box is removing ...')
        continue
      if poly1.area <= 10:
        print('Text region too small. This bounding box is removing ...')

      mean_x = np.mean(xt)
      mean_y = np.mean(yt)
      xt_sort = np.sort(xt)
      yt_sort = np.sort(yt)
      xt_argsort = list(np.argsort(xt))
      yt_argsort = list(np.argsort(yt))
      # indexing
      ldx = []
      for ildx in range(4):
        ldx.append(yt_argsort.index(xt_argsort[ildx]))
      all_types = [[1,2,3,4],[1,2,4,3],[1,3,2,4],[1,3,4,2],[1,4,2,3],[1,4,3,2],
                   [2,1,3,4],[2,1,4,3],[2,3,1,4],[2,3,4,1],[2,4,1,3],[2,4,3,1],
                   [3,1,2,4],[3,1,4,2],[3,2,1,4],[3,2,4,1],[3,4,1,2],[3,4,2,1],
                   [4,1,2,3],[4,1,3,2],[4,2,1,3],[4,2,3,1],[4,3,1,2],[4,3,2,1]]
      all_types = [[all_types[iat][0]-1,all_types[iat][1]-1,all_types[iat][2]-1,all_types[iat][3]-1] for iat in range(24)]
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
      ''' indexing gt
      
      '''
      dataset['annotations'].append({
          'area': width * height,
          'bbox': [xmin, ymin, width, height],
          'category_id': get_category_id(cls),
          'id': j,
          'image_id': int(index),
          'iscrowd': 0,
          'segmentation': [segs],
          # 'segmentation_shrink': [segs_shrink],
          'keypoints': keypoints,
          'match_type': match_type
      })
      j += 1
# f_index.close()

json_name = os.path.join(save_dir, '{}.json'.format("hctw_train2018"))
with open(json_name, 'w') as f:
  json.dump(dataset, f)
