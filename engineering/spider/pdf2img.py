# -*- coding: utf-8 -*-
import io

from wand.image import Image
from wand.color import Color
from PyPDF2 import PdfFileReader, PdfFileWriter
import os
import re
memo = {}

def getPdfReader(filename):
    reader = memo.get(filename, None)
    if reader is None:
        reader = PdfFileReader(filename, strict=False)
        memo[filename] = reader
    return reader


def _run_convert(filename, i, page, res=120):
    idx = page + 1
    pdfile = getPdfReader(filename)
    pageObj = pdfile.getPage(page)
    dst_pdf = PdfFileWriter()
    dst_pdf.addPage(pageObj)

    pdf_bytes = io.BytesIO()
    dst_pdf.write(pdf_bytes)
    pdf_bytes.seek(0)

    img = Image(file=pdf_bytes, resolution=res)
    img.format = 'png'
    img.compression_quality = 90
    img.background_color = Color("white")
    path_dir=filename[:filename.rindex('.')]+'/'
    #print(os.path.exists(path_dir))
    if os.path.exists(path_dir)==False:
        os.mkdir(path_dir)
    img_path = '%s%d.png' % (path_dir+i, idx)
    img.save(filename=img_path)
    img.destroy()

# path='pdf/(一线教师精品实用手写)高考物理总复习备课笔记(必修一).pdf'
# for i in range(27):
#     _run_convert(path,str(0),i)


path = '/home/dl/iiihunter/handwriting_data/pdf/'
file = os.listdir(path)
for i in file:
    if '.pdf' in i:
        print(i[:-4])
        try:
            for page in range(200):
                print(path+str(i) + ' page:' + str(page))
                _run_convert(path+str(i), i[:-4], page)
        except:
            print('不足200页')
