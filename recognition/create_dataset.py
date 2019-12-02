import os
import lmdb # install lmdb by "pip install lmdb"
import cv2
import numpy as np
import six
from PIL import Image
import random


def checkImageIsValid(imageBin):
    if imageBin is None:
        return False
    # imageBuf = np.fromstring(imageBin, dtype=np.uint8)
    # img = cv2.imdecode(imageBuf, cv2.IMREAD_GRAYSCALE)

    try:
        buf = six.BytesIO()
        buf.write(imageBin)
        buf.seek(0)
        img = Image.open(buf).convert('L')

        imgH, imgW = img.size[0], img.size[1]
        if imgH * imgW == 0:
            return False
    except:
        print('Found a invalid image!')
        return False
    return True


def writeCache(env, cache):
    invalid_num = 0
    with env.begin(write=True) as txn:
        for k, v in cache.items():
            if k.split('-')[0] == 'label' or k == 'num-samples':
                txn.put(k.encode(), str(v).encode())
            else:
                try:
                    txn.put(k.encode(), v)
                except:
                    print('jump a image!')
                    invalid_num += 1
                    continue
        # txn.commit()
    return invalid_num


def createDataset(outputPath, imagePathList, labelList, lexiconList=None, checkValid=True):
    """
    Create LMDB dataset for CRNN training.
    ARGS:
        outputPath    : LMDB output path
        imagePathList : list of image path
        labelList     : list of corresponding groundtruth texts
        lexiconList   : (optional) list of lexicon lists
        checkValid    : if true, check the validity of every image
    """
    assert(len(imagePathList) == len(labelList))
    nSamples = len(imagePathList)
    env = lmdb.open(outputPath, map_size=1099511627776)
    cache = {}
    cnt = 1
    invalid_num = 0
    for i in range(nSamples):
        imagePath = imagePathList[i]
        label = labelList[i]
        if not os.path.exists(imagePath):
            print('%s does not exist' % imagePath)
            continue
        with open(imagePath, 'rb') as f:
            imageBin = f.read()
        if checkValid:
            if not checkImageIsValid(imageBin):
                print('%s is not a valid image' % imagePath)
                continue

        imageKey = 'image-%09d' % cnt
        labelKey = 'label-%09d' % cnt
        cache[imageKey] = imageBin
        cache[labelKey] = label
        if lexiconList:
            lexiconKey = 'lexicon-%09d' % cnt
            cache[lexiconKey] = ' '.join(lexiconList[i])
        if cnt % 1000 == 0:
            invalid_num += writeCache(env, cache)
            cache = {}
            print('Written %d / %d' % (cnt, nSamples))
        cnt += 1
    nSamples = cnt-1
    invalid_num += writeCache(env, cache)
    cache['num-samples'] = str(nSamples-invalid_num)
    writeCache(env, cache)

    print('Created dataset with %d samples' % nSamples)
    print('Jump invalid images num:', invalid_num)


def add_38_class():
    label_txt1 = '/home/iiihunter/space/dataset/SynthText80k/train.txt'
    label_txt2 = '/home/iiihunter/space/dataset/SynthText80k/train4.txt'
    f = open(label_txt1, 'r')
    L1 = f.readlines()
    L_new = []
    f.close()
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    for item in L1:
        path, label = item.strip().split(' ')
        tmp = []
        for char in label.lower():
            if not char in alphabet:
                tmp.append(char)
        tmp2 = list(set(tmp))
        for c in tmp2:
            new_label = label.replace(c, "")
            label = new_label
        new_line = path + " " + label + "\n"
        L_new.append(new_line)
    f2 = open(label_txt2, "w")
    f2.writelines(L_new)
    f2.close()


if __name__ == '__main__':
    output_path = '/home/dl/iiihunter/labeled_images/CCHW_v3_6/train/CCHW_train'
    # env = lmdb.open(output_path, map_size=1099511627776)
    # with env.begin() as txn:
    #     num = txn.get("label-007260347".encode())
    #     print(num)

    label_txt = '/home/dl/iiihunter/labeled_images/CCHW_v3_6/train/train.txt'
    f = open(label_txt, 'r')
    L = f.readlines()
    f.close()

    image_path_list = []
    label_list = []
    for item in L:
        if len(item.strip().split(" ")) != 2:
            continue
        path, label = item.strip().split(' ')
        image_path_list.append(path)
        label_list.append(label)

    createDataset(output_path, image_path_list, label_list)
    # add_38_class()

