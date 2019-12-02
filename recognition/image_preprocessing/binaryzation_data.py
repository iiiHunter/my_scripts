# -*- coding: utf-8 -*-
'''
@project: recog_attn
@author: iiihunter@JinGroup
@file: preprocess_data.py
@time: 19-1-2 上午11:17
@email: hesuozhang@gmail.com
'''
import numpy as np
from PIL import Image
import cv2
import os


def data_prepropossing(img, mask, height, width, hdivw, wdivh):
    if height < 40:
        adaptiveThreshold_kernel = 5
    elif height < 60:
        adaptiveThreshold_kernel = 7
    elif height < 80:
        adaptiveThreshold_kernel = 11
    else:
        adaptiveThreshold_kernel = 15
    adaptiveThreshold_bias = 3
    if img.size[1] > height:
        if img.size[0] > width:
            if float(img.size[0]) / float(width) > float(img.size[1]) / float(height):
                img = img.resize((width, int(width * hdivw)))
                img = np.array(img)
                img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,
                                            adaptiveThreshold_kernel, adaptiveThreshold_bias)
                img = cv2.medianBlur(img, 3)
                img = Image.fromarray(np.uint8(img))
                mask.paste(img, (0, int((height - int(width * hdivw)) / 2)))
            else:
                img = img.resize((int(height * wdivh), height))
                img = np.array(img)
                img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,
                                            adaptiveThreshold_kernel, adaptiveThreshold_bias)
                img = cv2.medianBlur(img, 3)
                img = Image.fromarray(np.uint8(img))
                mask.paste(img, (0, 0))
        else:
            img = img.resize((int(height * wdivh), height))
            img = np.array(img)
            img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,
                                        adaptiveThreshold_kernel, adaptiveThreshold_bias)
            img = cv2.medianBlur(img, 3)
            img = Image.fromarray(np.uint8(img))
            mask.paste(img, (0, 0))
    else:
        if img.size[0] > width:
            img = img.resize((width, int(width * hdivw)))
            img = np.array(img)
            img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,
                                        adaptiveThreshold_kernel, adaptiveThreshold_bias)
            img = cv2.medianBlur(img, 3)
            img = Image.fromarray(np.uint8(img))
            mask.paste(img, (0, int((height - int(width * hdivw)) / 2)))
        else:
            if float(img.size[0]) / float(width) > float(img.size[1]) / float(height):
                img = img.resize((width, int(width * hdivw)))
                img = np.array(img)
                img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,
                                            adaptiveThreshold_kernel, adaptiveThreshold_bias)
                img = cv2.medianBlur(img, 3)
                img = Image.fromarray(np.uint8(img))
                mask.paste(img, (0, int((height - int(width * hdivw)) / 2)))
            else:
                img = img.resize((int(height * wdivh), height))
                img = np.array(img)
                img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,
                                            adaptiveThreshold_kernel, adaptiveThreshold_bias)
                img = cv2.medianBlur(img, 3)
                img = Image.fromarray(np.uint8(img))
                mask.paste(img, (0, 0))


def process_all(root, des_root):
    imgs_list = [os.path.join(root, item) for item in os.listdir(root)]
    for i, img_path in enumerate(imgs_list):
        if i % 100 == 0:
            print("Processing: %d / %d" % (i, len(imgs_list)))
        img = Image.open(img_path).convert('L')
        hdivw = float(img.size[1]) / float(img.size[0])
        wdivh = float(img.size[0]) / float(img.size[1])
        new_h = img.size[1]
        # new_w = int(new_h * wdivh)
        new_w = img.size[0]
        mask = Image.new('L', (new_w, new_h), 'white')
        data_prepropossing(img, mask, new_h, new_w, hdivw, wdivh)
        mask.save(os.path.join(des_root, os.path.basename(img_path)))


def resize_all(root, des_root):
    imgs_list = [os.path.join(root, item) for item in os.listdir(root)]
    for i, img_path in enumerate(imgs_list):
        img = Image.open(img_path).convert('L')
        img = img.resize((576, 126), Image.ANTIALIAS)
        img.save(os.path.join(des_root, os.path.basename(img_path)))


def replace_path():
    txt = "/home/dl/iiihunter/labeled_images/CCHW_v3_6/test/test_encode.txt"
    new_txt = "/home/dl/iiihunter/labeled_images/CCHW_v3_6/test/test_encode0.txt"
    new_L = []
    with open(txt, "r") as f:
        for item in f.readlines():
            item = item.replace("crop_images", "crop_images_bi")
            new_L.append(item)
        f.close()
    with open(new_txt, "w") as f:
        f.writelines(new_L)
        f.close()


if __name__ == "__main__":
    # root = "/home/sol/data/Datasets/CCHW_v5_0/CCHW_v5_0/crop/test_image"
    # # root = "/home/dl/iiihunter/labeled_images/CCHW_v3_6/test/pick_images"
    # # img_path = "/home/dl/iiihunter/labeled_images/CCHW_v3_6/test/crop_images/weixin_8944_13.jpg"
    # des_root = "/home/sol/data/Datasets/CCHW_v5_0/CCHW_v5_0/crop/test_bi_small_kernel"
    # # des_root = "/home/dl/iiihunter/labeled_images/CCHW_v3_6/test/pick_images_result"
    # if not os.path.exists(des_root):
    #     os.mkdir(des_root)
    # process_all(root, des_root)
    # f = open("/home/sol/data/Datasets/CCHW_v5_0/CCHW_v5_0/crop/test_encode.txt", "r")
    # f2 = open("/home/sol/data/Datasets/CCHW_v5_0/CCHW_v5_0/crop/test_encode_bi_small_kernel.txt", "w")
    # L = [item.replace("/test_image", "/test_image_bi_small_kernel") for item in f.readlines()]
    # f2.writelines(L)
    # f.close()
    # f2.close()

    root = "/home/sol/Desktop/CCHW_PR/paper_images/compare/origin"
    des_root = "/home/sol/Desktop/CCHW_PR/paper_images/compare/origin_bi"
    if not os.path.exists(des_root):
        os.mkdir(des_root)
    process_all(root, des_root)

    # source_txt = "/home/sol/Project/new_db_process/e2e_recog_tools/crop_from_det_east.txt"
    # des_txt = "/home/sol/Project/new_db_process/e2e_recog_tools/crop_from_det_east_bi.txt"
    # with open(source_txt, "r") as f:
    #     L = f.readlines()
    # new_L = []
    # for item in L:
    #     path, label = item.split(" ")
    #     path = path.replace("/cropped_images_east/", "/cropped_images_east_bi/")
    #     new_L.append(path + " " + label)
    # with open(des_txt, "w") as f:
    #     f.writelines(new_L)
