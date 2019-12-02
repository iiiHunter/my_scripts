# !/usr/bin/local/python3
# -*- coding: utf-8 -*-
'''
@project: new_db_process
@author: iiihunter@JinGroup
@file: crop_perspective2.py
@time: 18-12-10 下午9:09
@email: hesuozhang@gmail.com
'''

import cv2
import numpy as np
import glob
import os
import math


def crop_image(image_path, boxes):
    def distance(x1, y1, x2, y2):
        return math.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))
    img = cv2.imread(image_path)

    croped_imgs = []

    for ibox in boxes:
        if(ibox.strip()):
            label_list = (ibox.strip()).split(",")
            x1s, y1s, x2s, y2s, x3s, y3s, x4s, y4s = \
                    label_list[0], label_list[1], label_list[2], label_list[3],\
                    label_list[4], label_list[5], label_list[6], label_list[7]

            if len(label_list) > 9:
                print("ERR!")

            # sort the (x, y)
            position = [[float(x1s), float(y1s)], [float(x2s), float(y2s)],
                        [float(x3s), float(y3s)],[float(x4s), float(y4s)]]
            for i in range(4):
                for j in range(i+1, 4):
                    if position[i][0] > position[j][0]:
                        tmp = position[j]
                        position[j] = position[i]
                        position[i] = tmp
            if position[0][1] > position[1][1]:
                tmp = position[0]
                position[0] = position[1]
                position[1] = tmp
            if position[2][1] > position[3][1]:
                tmp = position[2]
                position[2] = position[3]
                position[3] = tmp
            x1, y1 = position[0][0], position[0][1]
            x2, y2 = position[2][0], position[2][1]
            x3, y3 = position[3][0], position[3][1]
            x4, y4 = position[1][0], position[1][1]
        else:
            break

        corners = np.zeros((4, 2), np.float32)
        corners[0] = [x1, y1]
        corners[1] = [x2, y2]
        corners[2] = [x4, y4]
        corners[3] = [x3, y3]

        img_width = distance(
            (x1 + x4) / 2, (y1 + y4) / 2, (x2 + x3) / 2, (y2 + y3) / 2)
        img_height = distance(
            (x1 + x2) / 2, (y1 + y2) / 2, (x4 + x3) / 2, (y4 + y3) / 2)

        corners_trans = np.zeros((4, 2), np.float32)
        corners_trans[0] = [0, 0]
        corners_trans[1] = [img_width - 1, 0]
        corners_trans[2] = [0, img_height - 1]
        corners_trans[3] = [img_width - 1, img_height - 1]

        transform = cv2.getPerspectiveTransform(corners, corners_trans)
        dst = cv2.warpPerspective(img, transform, (int(img_width), int(img_height)))

        fname = ''
        for c in range(7):
            fname += str(label_list[c]) + ','
        if len(label_list) >= 8:
            fname += str(label_list[7])
        else:
            fname += str(label_list[7][:-2])

        if (img_height > 1.5 * img_width):
            t = cv2.transpose(dst)
            dst = cv2.flip(t, 0)
        croped_imgs.append(dst)
    return croped_imgs


if __name__ == "__main__":
    pass
