#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Project: new_db_process
@Author: sol@JinGroup
@File: crop_detection_result.py
@Time: 10/11/19 2:53 PM
@E-mail: hesuozhang@gmail.com
'''

import json
import cv2
import os
from e2e_recog_tools.get_imgs2recog import crop_image


def get_encode_dict():
    dict_txt = "/home/sol/data/Datasets/HCTW/dict_8615.txt"
    f = open(dict_txt, "r")
    char_list = [item.strip() for item in f.readlines()]
    char_dict = {}
    for i, char in enumerate(char_list):
        char_dict[char] = str(i)
    f.close()
    return char_dict


def encode_label(label):
    char_dict = get_encode_dict()
    s = ''
    for c in label:
        if c not in char_dict:
            print(c)
            continue
        s += char_dict[c] + ","
    return s[:-1]


def analyze_result_json(json_path):
    with open(json_path, "r") as f:
        result = json.loads(f.read())
    return result["pairs"]


def match_gt_pred(gt_txt, pred_txt, match_json_path, image_path, save_cropped_image_path, final_txt_path):
    '''
    match the detection result and gt, crop the box IOU over 0.5, and get the detection box's text label
    :param gt_txt: gt txt, with text label
    :param pred_txt: pred txt, without text label
    :param match_json_path: match jons label generated from icdar evluation tool(output/results_x.zip)
    :param image_path: image path
    :param save_cropped_image_path: the dir to save the cropped images
    :param final_txt_path: txt to write the cropped images path and its text related (for recognition)
    :return:
    '''
    id = os.path.basename(image_path).split(".")[0]
    with open(gt_txt) as f_gt:
        gt_list = f_gt.readlines()
    with open(pred_txt, "r") as f_pred:
        pred_list = f_pred.readlines()
    pairs = analyze_result_json(match_json_path)
    coor_list, text_list = [], []
    for pair in pairs:
        text = gt_list[pair["gt"]].split(",")[-1]
        text_list.append(text.strip().replace("\"", ""))
        coor_list.append(pred_list[pair["det"]].strip())
    # cropped_image_list = crop_image(image_path, coor_list)
    cropped_image_list = coor_list
    # f_final = open(final_txt_path, "a+")
    f_path_det = "/home/sol/data/Project/new_db_process/e2e_recog_tools/path_det_east.txt"
    f_path_det = open(f_path_det, "a+")
    for i, (cropped_image, text, coor) in enumerate(zip(cropped_image_list, text_list, coor_list)):
        save_path = os.path.join(save_cropped_image_path, "%s_%d.jpg" % (id, i))
        # cv2.imwrite(save_path, cropped_image)
        # f_final.write(save_path + " " + encode_label(text) + "\n")
        f_path_det.write(save_path + " " + coor + "\n")


if __name__ == "__main__":
    gt_root = "/home/sol/data/Datasets/CCHW_v5_0/HCTW/test_set/gt"
    pred_root = "/home/sol/Project/new_db_process/e2e_recog_tools/subm_12"
    match_root = "/home/sol/data/labeled_images/new_db_process/e2e_recog_tools/results_12"
    image_root = "/home/sol/data/Datasets/CCHW_v5_0/HCTW/test_set/images"
    save_cropped_image_path = "/home/sol/data/Project/new_db_process/e2e_recog_tools/cropped_images_east"
    final_txt_path = "/home/sol/data/Project/new_db_process/e2e_recog_tools/crop_from_det_east.txt"
    # analyze_result_json(json_path="/home/sol/data/labeled_images/new_db_process/e2e_recog_tools/results_8/1045.json")
    if not os.path.exists(save_cropped_image_path):
        os.mkdir(save_cropped_image_path)
    for n in range(2452):
        print(n)
        gt_txt = os.path.join(gt_root, "%d.txt" % n)
        pred_txt = os.path.join(pred_root, "%d.txt" % n)
        match_json_path = os.path.join(match_root, "%d.json" % n)
        image_path = os.path.join(image_root, "%d.jpg" % n)
        if not os.path.exists(pred_txt):
            print(pred_txt)
            continue
        match_gt_pred(gt_txt, pred_txt, match_json_path, image_path, save_cropped_image_path, final_txt_path)
