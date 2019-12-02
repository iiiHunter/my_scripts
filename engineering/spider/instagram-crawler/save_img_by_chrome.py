import sys
from sele nium import webdriver
import time
import json
import os


def get_img(driver, url, im_path):
    driver.get(url)
    driver.save_screenshot(im_path)
    # driver.close()


def claw_imgs(save_dir, url_list, img_url_path, invalid_url_path):
    f = open(img_url_path, "a+")
    driver = webdriver.Chrome('/home/owen/iiihunter/instagram-crawler-master/inscrawler/bin/chromedriver')
    for i in range(67284, len(url_list)):
        im_path = os.path.join(save_dir, str(i) + ".png")
        get_img(driver, url_list[i], im_path)
        f.write(im_path + "," + url_list[i] + "\n")
        time.sleep(0.1)
        if i % 100 == 0:
            print(i, "/", len(url_list))
    f.close()


def sort_images():
    f1 = open("/home/owen/iiihunter/HCHW_URL/insta_39k+67284_url.txt", 'r')
    f2 = open("/home/owen/iiihunter/HCHW_URL/insta_39k_url.txt", 'r')
    f3 = open("/home/owen/iiihunter/HCHW_URL/insta_100k_left_url.txt", 'r')

    L1 = f1.readlines()
    L2 = f2.readlines()
    L3 = f3.readlines()

    print(len(L1), len(L2), len(L3))
    L_all = L2 + L1[39000:] + L3
    f = open("/home/owen/iiihunter/HCHW_URL/insta_url.txt", 'w')
    f.writelines(L_all)



if __name__ == "__main__":
    # url = "https://scontent-nrt1-1.cdninstagram.com/vp/0d21ff1b6ae700f1505252c41d668025/5C0B0135/t51.2885-15/sh0.08/e35/s640x640/14474491_1765888260316939_5041492629917794304_n.jpg"
    # a = open('save_img_list_100k.txt', 'r', encoding='UTF-8')
    # save_dir = '/media/owen/owen/iiihunter/HCHW_URL/insta_100k'
    # img_url_path = '/media/owen/owen/iiihunter/HCHW_URL/insta_100k_left_url.txt'
    # invalid_url_path = '/media/owen/owen/iiihunter/HCHW_URL/insta_100k_invalid_url.txt'
    # url_list = json.loads(a.read())
    # claw_imgs(save_dir, url_list, img_url_path, invalid_url_path)

    sort_images()

