import urllib.request
import os


url = "https://scontent-nrt1-1.cdninstagram.com/vp/0d21ff1b6ae700f1505252c41d668025/5C0B0135/t51.2885-15/sh0.08/e35/s640x640/14474491_1765888260316939_5041492629917794304_n.jpg"
url2 = 'http://img3.imgtn.bdimg.com/it/u=2484226909,3831788142&fm=27&gp=0.jpg'
url3 = 'https://mmbiz.qpic.cn/mmbiz_jpg/0LpJmuvBHvyJYTibic8aRocnVbgiaGvN1dqDVInIjnf9GrhztW9UpIVyibicJGU4dHsnrDQx4Fqmo7UFicpHhZEcyg8Q/0?wx_fmt=jpeg'
path ="out/test.jpg"
baidu = 'http://www.baidu.com'

# opener = urllib.request.build_opener()
# opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
# urllib.request.install_opener(opener)
# urllib.request.urlretrieve(url3, path)



headers= {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
}
import requests
# res = requests.get(url, headers=headers)

i = urllib.request.urlopen(url).read()
