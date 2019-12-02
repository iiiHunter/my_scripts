import datetime
import os
from PIL import Image
import process_label.data_converter.pycococreatortools as pycococreatortools
from pycocotools.coco import COCO
import fnmatch, re
import cv2
import numpy as np
import json
import random
import threading
from queue import Queue
from multiprocessing import cpu_count
import matplotlib.pyplot as plt
random.seed(123)

TRAIN_RATIO = 4./5.
IMAGE_DIR = '/home/sol/data/Datasets/试卷数据/picked_images/image'
ANNOTATION_DIR = '/home/sol/data/Datasets/试卷数据/picked_images/label'
ROOT_DIR = '/home/sol/data/Datasets/试卷数据/picked_images/annotations'
# if not os.path.exists(ROOT_DIR):
#     os.mkdir(ROOT_DIR)
INFO = {
    "description": "Examination Paper Database",
    "url": "local disk",
    "version": "1.0.0",
    "year": 2019,
    "contributor": "JinGroup",
    "date_created": datetime.datetime.utcnow().isoformat(' ')
}

LICENSES = [
    {
        "id": 1,
        "name": "Attribution-NonCommercial-ShareAlike License",
        "url": ""
    }
]

CATEGORIES = [
    {
        'id': 1,
        'name': 'text',
        'supercategory': 'text',
    },
]


def filter_for_jpeg(root, files):
    file_types = ['*.jpeg', '*.jpg']
    file_types = r'|'.join([fnmatch.translate(x) for x in file_types])
    files = [os.path.join(root, f) for f in files]
    files = [f for f in files if re.match(file_types, f)]

    return files


def filter_for_annotations(root, files, image_filename):
    file_types = ['*.txt']
    file_types = r'|'.join([fnmatch.translate(x) for x in file_types])
    basename_no_extension = os.path.splitext(os.path.basename(image_filename))[0]
    file_name_prefix = basename_no_extension + '.*'
    files = [os.path.join(root, f) for f in files]
    files = [f for f in files if re.match(file_types, f)]
    files = [f for f in files if re.match(file_name_prefix, os.path.splitext(os.path.basename(f))[0])]

    return files


def generate_mask(gt_file, image_filename):
    image = cv2.imread(image_filename)

    objs = open(gt_file, 'r').readlines()
    num_objs = len(objs) - 1
    masks = np.zeros(image.shape[0:2] + (num_objs, ))
    # poly_each_pic = np.zeros((num_objs, 4, 2), dtype=np.float)
    for ix, obj in enumerate(objs):
        # if ix == 0:
        #     continue
        obj = obj.replace('\xef\xbb\xbf', '')
        obj = obj.replace('\ufeff', '')
        obj = obj.strip()
        bbox = np.array(obj.split(','))[0:8]
        bbox = bbox.astype(np.float32).reshape((4, 2))
        mask = np.zeros(image.shape[0:2])
        mask = cv2.fillConvexPoly(mask, bbox.astype(np.int32), color=1)
        masks[:, :, ix-1] = mask.copy()
    return (masks > 0).astype(np.uint8)


def main():
    train_coco_output = {
        "info": INFO,
        "licenses": LICENSES,
        "categories": CATEGORIES,
        "images": [],
        "annotations": []
    }
    train_image_id = 1
    train_segmentation_id = 1
    val_coco_output = {
        "info": INFO,
        "licenses": LICENSES,
        "categories": CATEGORIES,
        "images": [],
        "annotations": []
    }
    val_image_id = 1
    val_segmentation_id = 1
    # filter for jpeg images
    image_files = [os.path.join(IMAGE_DIR, item) for item in os.listdir(IMAGE_DIR)]
    # go through each image
    image_files.sort()
    random.shuffle(image_files)
    num_train = int(TRAIN_RATIO * len(image_files))
    num_test = len(image_files) - num_train

    train_quene = Queue(maxsize=0)
    val_quene = Queue(maxsize=0)

    train_start = 0
    train_end = num_train
    val_start = 0
    val_end = num_test
    anno_idx_begin = 1
    print('loading multi_processing quene......')
    for i in range(train_start, train_end):
        print(i)
        train_quene.put([i, anno_idx_begin])
        # annotation_file = image_files[i].replace(IMAGE_DIR, ANNOTATION_DIR).split(".")[0] + ".txt"
        annotation_file = os.path.join(ANNOTATION_DIR, os.path.basename(image_files[i]).split(".")[0] + ".txt")
        assert os.path.exists(annotation_file)
        objs = open(annotation_file, 'r').readlines()
        anno_idx_begin += (len(objs) - 1)

    anno_idx_begin = 1
    for i in range(val_start, val_end):
        val_quene.put([i, anno_idx_begin])
        # annotation_file = image_files[i].replace(IMAGE_DIR, ANNOTATION_DIR).split(".")[0] + ".txt"
        annotation_file = os.path.join(ANNOTATION_DIR, os.path.basename(image_files[i]).split(".")[0] + ".txt")
        assert os.path.exists(annotation_file)
        objs = open(annotation_file, 'r').readlines()
        anno_idx_begin += (len(objs) + 1)
    print('finish loading')
    print('processing train data')
    global count
    count = 0
    def train_process():
        global count
        while not train_quene.empty():
            print('%d/%d:' % (count, num_train))
            count += 1
            idx, train_segmentation_id = train_quene.get()
            train_image_id = idx + 1
            image_filename = image_files[idx]
            print("-----process train img {}".format(image_filename))
            image = Image.open(image_filename)
            related_file_name = image_filename.split("/image/")[1]
            image_info = pycococreatortools.create_image_info(train_image_id, related_file_name, image.size)
            train_coco_output["images"].append(image_info)
            annotation_files = [os.path.join(ANNOTATION_DIR, os.path.basename(image_filename).split(".")[0] + ".txt")]
            assert os.path.exists(annotation_files[0])
            for annotation_filename in annotation_files:
                # print(annotation_filename)
                class_id = 1  # [x['id'] for x in CATEGORIES if x['name'] in annotation_filename][0]
                category_info = {'id': class_id, 'is_crowd': False}
                binary_masks = generate_mask(annotation_filename, image_filename)
                for i in range(binary_masks.shape[2]):
                    annotation_info = pycococreatortools.create_annotation_info(
                        train_segmentation_id, train_image_id, category_info, binary_masks[:, :, i].copy(),
                        image.size, tolerance=2)
                    if annotation_info is not None:
                        train_coco_output["annotations"].append(annotation_info)
                        train_segmentation_id += 1
    print('processing val data')
    count = 0
    def val_process():
        global count
        while not val_quene.empty():
            print('%d/%d:' % (count, num_test))
            count += 1
            idx, val_segmentation_id = val_quene.get()
            # val_segmentation_id = idx - val_start + 1
            val_image_id = idx - val_start + 1
            image_filename = image_files[idx]
            print("-----process val img {}".format(image_filename))
            image = Image.open(image_filename)
            related_file_name = image_filename.split("/image/")[1]
            image_info = pycococreatortools.create_image_info(
                val_image_id, related_file_name, image.size)
            val_coco_output["images"].append(image_info)

            annotation_files = [os.path.join(ANNOTATION_DIR, os.path.basename(image_filename).split(".")[0] + ".txt")]
            assert os.path.exists(annotation_files[0])
            for annotation_filename in annotation_files:
                print(annotation_filename)
                class_id = 1  # [x['id'] for x in CATEGORIES if x['name'] in annotation_filename][0]
                category_info = {'id': class_id, 'is_crowd': False}
                binary_masks = generate_mask(annotation_filename, image_filename)
                for i in range(binary_masks.shape[2]):
                    annotation_info = pycococreatortools.create_annotation_info(
                        val_segmentation_id, val_image_id, category_info, binary_masks[:, :, i].copy(),
                        image.size, tolerance=2)
                    if annotation_info is not None:
                        val_coco_output["annotations"].append(annotation_info)
                        val_segmentation_id += 1

    threads = [threading.Thread(target=train_process, args=()) for i in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    threads = [threading.Thread(target=val_process, args=()) for i in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    with open('{}/coco_ep_train2019.json'.format(ROOT_DIR), 'w') as output_json_file:
        json.dump(train_coco_output, output_json_file)

    with open('{}/coco_ep_val2019.json'.format(ROOT_DIR), 'w') as output_json_file:
        json.dump(val_coco_output, output_json_file)


if __name__ == '__main__':
    # main()


    # coco = COCO('d{}/coco_cchw_val2018.json'.format(ROOT_DIR))
    # coco = COCO("/home/sol/data/Datasets/CCHW_v5_0/CCHW_v5_0/annotations/hctw_test2018.json")
    coco = COCO("/home/sol/data/Datasets/试卷数据/picked_images/annotations/coco_ep_train2019.json")
    imgIds = coco.getImgIds(catIds=1)
    img = coco.loadImgs(imgIds[np.random.randint(0, len(imgIds))])[0]
    # I = cv2.imread(os.path.join(IMAGE_DIR, img['file_name']))
    # I = cv2.imread(os.path.join("/home/sol/data/Datasets/CCHW_v5_0/CCHW_v5_0/image", img['file_name']))
    I = cv2.imread(os.path.join("/home/sol/data/Datasets/试卷数据/picked_images/image", img['file_name']))
    annIds = coco.getAnnIds(imgIds=img['id'], catIds=1)
    anns = coco.loadAnns(annIds)
    plt.imshow(I)
    coco.showAnns(anns)
    plt.show()
