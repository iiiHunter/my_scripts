# -*- coding: utf-8 -*-
'''
@project: new_db_process
@author: iiihunter@JinGroup
@file: test.py
@time: 18-12-10 下午9:09
@email: hesuozhang@gmail.com
'''

from langconv import *
import os
import shutil


# 转换繁体到简体
def cht_to_chs(line):
    line = Converter('zh-hans').convert(line)
    line.encode('utf-8')
    return line


# 转换简体到繁体
def chs_to_cht(line):
    line = Converter('zh-hant').convert(line)
    line.encode('utf-8')
    return line


def sim2tra():
    for num in range(25):
        label_path = '/home/dl/iiihunter/labeled_images/CCHW_v3_5/labels/' + str(num)
        new_label_path = '/home/dl/iiihunter/labeled_images/CCHW_v3_5/labels_tra/' + str(num)
        if not os.path.exists(new_label_path):
            os.mkdir(new_label_path)
        L = os.listdir(label_path)
        for item in L:
            path = os.path.join(label_path, item)
            new_path = os.path.join(new_label_path, item)
            if not item.split("_")[0] == "insta":
                shutil.copy(path, new_path)
                continue
            f = open(path, 'r')
            new_content = []
            for indx, line in enumerate(f.readlines()):
                if indx == 0:
                    new_content.append(line)
                    continue
                label = line.split(',')[-1].strip().replace("\"", "")
                new_label = chs_to_cht(label)
                new_line = line.replace(label, new_label)
                new_content.append(new_line)
            f = open(new_path, "w")
            f.writelines(new_content)
            print(new_path)


def tra2sim():
    for num in range(25):
        label_path = '/home/dl/iiihunter/labeled_images/HCHW_v3_3/labels_tra/' + str(num)
        new_label_path = '/home/dl/iiihunter/labeled_images/HCHW_v3_3/labels_sim/' + str(num)
        if not os.path.exists(new_label_path):
            os.mkdir(new_label_path)
        L = os.listdir(label_path)
        for item in L:
            path = os.path.join(label_path, item)
            new_path = os.path.join(new_label_path, item)
            if not item.split("_")[0] == "insta":
                shutil.copy(path, new_path)
                continue
            f = open(path, 'r')
            new_content = []
            for indx, line in enumerate(f.readlines()):
                if indx == 0:
                    new_content.append(line)
                    continue
                label = line.split(',')[-1].strip().replace("\"", "")
                new_label = cht_to_chs(label)
                new_line = line.replace(label, new_label)
                new_content.append(new_line)
            f = open(new_path, "w")
            f.writelines(new_content)

if __name__ == "__main__":
    # line_cht = '<>123asdasd把中文字符串進行繁體和簡體中文的轉換'
    # ret_chs = "%s\n" % cht_to_chs(line_cht)
    #
    # print(ret_chs)
    # tra2sim()
    sim2tra()
