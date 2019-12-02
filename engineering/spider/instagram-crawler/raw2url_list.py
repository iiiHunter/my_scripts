import json
import urllib.request
import re

b = open('output_400_jiantizi.txt', "r", encoding='UTF-8')
out = json.loads(b.read())
L = []
for item in out:
    L.append(item['img_url'])
print(len(L))
print(L[0])
a = open('save_img_list_400_jiantizi.txt', 'w', encoding='UTF-8')
a.write(json.dumps(L))
a.close()

