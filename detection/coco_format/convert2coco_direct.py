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


def get_category_id(dataset, cls):
  for category in dataset['categories']:
    if category['name'] == cls:
      return category['id']


def gen(dataset, image_files):
    j = 1
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

        anno_file = im_path.replace("/image/", "/label/").split(".")[0] + ".txt"
        if not os.path.exists(anno_file):
            print("label not found:", anno_file)
            exit(-1)
        with open(anno_file) as f:
            lines = [line for line in f.readlines() if line.strip()]
        for i, line in enumerate(lines):
            parts = line.strip().split(',')
            assert len(parts) == 8
            cls = 'text'
            xmin = min(int(parts[0]), int(parts[2]), int(parts[4]), int(parts[6]))
            ymin = min(int(parts[1]), int(parts[3]), int(parts[5]), int(parts[7]))
            xmax = max(int(parts[0]), int(parts[2]), int(parts[4]), int(parts[6]))
            ymax = max(int(parts[1]), int(parts[3]), int(parts[5]), int(parts[7]))
            width = max(0, xmax - xmin + 1)
            height = max(0, ymax - ymin + 1)
            if width == 0 or height == 0:
                continue
            segs = [int(kkpart) for kkpart in parts]  # four points

            dataset['annotations'].append({
                'area': width * height,
                'bbox': [xmin, ymin, width, height],
                'category_id': get_category_id(dataset, cls),
                'id': j,
                'image_id': int(index),
                'iscrowd': 0,
                'segmentation': [segs],
            })
            j += 1
    return dataset


if __name__ == "__main__":
    IMAGE_DIR = '/home/sol/data/Datasets/试卷数据/picked_images/image'
    save_dir = '/home/sol/data/Datasets/试卷数据/picked_images/annotations'  # output path
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    all_images = [os.path.join(IMAGE_DIR, item) for item in os.listdir(IMAGE_DIR)]
    random.shuffle(all_images)

    train_num = int(len(all_images) * 0.8)
    train_images = all_images[:train_num]
    test_num = len(all_images) - train_num
    test_images = all_images[train_num:]

    dataset1 = {
        'licenses': [],
        'info': {},
        'categories': [],
        'images': [],
        'annotations': []
    }

    classes = ['text']
    for i, cls in enumerate(classes, 1):
        dataset1['categories'].append({
            'id': i,
            'name': cls,
            'supercategory': 'text',
        })

    train_dataset = gen(dataset1, train_images)
    # test_dataset = gen(dataset1, test_images)
    #
    json_name = os.path.join(save_dir, '{}.json'.format("coco_ep_train2019"))
    with open(json_name, 'w') as f:
      json.dump(train_dataset, f)

    # json_name = os.path.join(save_dir, '{}.json'.format("coco_ep_test2019"))
    # with open(json_name, 'w') as f:
    #     json.dump(test_dataset, f)
