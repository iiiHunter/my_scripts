#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
  2017.2.5 更新如下
  1. 矩形标注模式现在支持缩放下操作
  2. 缩放下标注时， 或者滑动窗口时，点击鼠标右键将不会变回原图，而是停留在当前状态。
  3. 缩放下或者滑动窗口时，点击删除将不会变回原图，而是停留在当前状态。
  4. 增加“回车”跳图快捷键，且打开工具时自动会把输入框聚焦在输入跳图的框内。
  5. 增加“INFO”来指引用户使用该标注工具
'''
import math
import os
import sys
import glob
from Tkinter import *   
import Tkinter as ttk
import tkMessageBox
from PIL import Image, ImageTk
import random
import shutil
import types
import tkMessageBox
import argparse
import codecs
import cv2
import numpy
from sympy.geometry import *

COLORS = ['red', 'blue', 'Dark Goldenrod', 'pink', 'cyan', 'green', 'Dark Orange', 'Light Salmon', 'Light Slate Blue', 'Medium Aquamarine']
isUseRectangle = 0 # switch mode 0 quad 1 rect  2 rotate rect
parser = argparse.ArgumentParser()
parser.add_argument("--num", type=str, help="index of dir")
parser.add_argument("--image", type=str, help="image dir")
parser.add_argument("--label", type=str, help="label dir")
opt = parser.parse_args()

if opt.num:
    num = opt.num
else:
    num = "0"
if opt.image:
    image_root = opt.image
else:
    image_root = './image/'
if opt.label:
    label_root = opt.label
else:
    label_root = './label/'

selfimageDir = os.path.join(image_root, num)
selfoutDir = os.path.join(label_root, num)
print(selfimageDir)

print("Loading image from: ", selfimageDir)
print("Loading label from:", selfoutDir)
if not os.path.exists(selfimageDir) and os.path.exists(selfoutDir):
    print("Exit! \n Please enter the correct image and label path!")
    exit(-1)


class DialogINFO:
    def __init__(self, parent):
        top = self.top = ttk.Toplevel(parent)
        top.title('功能介绍(image & label)')
        self.myLabel_TOP = ttk.Label(top, justify=LEFT, text="热键及部分功能介绍 ('i' 可以显示)：")
        self.myLabel_TOP.pack(padx =10, pady=5, side=TOP)
        self.myLabel_key = ttk.Label(top, justify=LEFT, text="1. 所有按钮旁边都有一个小字母作为这个按键的快键键，功能相同。")
        self.myLabel_key.pack(padx =10, pady=5, side=TOP)
        self.myLabel_c = ttk.Label(top, text="2. \'c\': （绑定Collect/Remove按钮）将图片及标注保存到collect_文件夹（自动创建），再次点击就是移除.  YES 已保存当前图片。NO 未保存当前图片。")
        self.myLabel_c.pack(padx =10, pady=5, side=TOP)
        self.myLabel_MouseRight = ttk.Label(top, text = "3. 鼠标右键可以用来取消当前标注动作。（例如画一半发现错了可以方便取消）")
        self.myLabel_MouseRight.pack(padx =10, pady=5, side=TOP)
        self.myLabel_Enter = ttk.Label(top, text = "4. \'Enter\': 跳到第x张图片。")
        self.myLabel_Enter.pack(padx =10, pady=5, side=TOP)
        self.myLabel_r = ttk.Label(top, text = "5. \'r\': 切换标注模式，使用矩形标注或者四点标注。")
        self.myLabel_r.pack(padx =10, pady=5, side=TOP)
        self.myLabel_select = ttk.Label(top, text = "6. Bounding boxes框每行代表一个标注，颜色对应，按't'，在图片中会在对应框左上角显示笑脸。点'd'则会删除该框，还可结合ctrl或者shift多选删除。")
        self.myLabel_select.pack(padx =10, pady=5, side=TOP)
        self.myLabel_MouseRoll = ttk.Label(top, text = "7. 鼠标滚轮可以用来放大缩小图片进行标注（两种模式都支持）。")
        self.myLabel_MouseRoll.pack(padx =10, pady=5, side=TOP)
        self.myLabel_Attention = ttk.Label(top, text = "8. 'f'看下张图片，'b'看前一张图片。上一张标注完的图片会自动保存。")
        self.myLabel_Attention.pack(padx =10, pady=5, side=TOP)
        self.myLabel_Scroll = ttk.Label(top, text = "9. 方向上下左右键对应滑动条的方向，方便对大图的标注。")
        self.myLabel_Scroll.pack(padx =10, pady=5, side=TOP)
        self.myLabel_recLabel = ttk.Label(top, text = "10. '鼠标左键双击' 选定右边列出的文本框后双击可以为当前文本框内容进行标注。")
        self.myLabel_recLabel.pack(padx =10, pady=5, side=TOP)
        self.myLabel_fastResize = ttk.Label(top, text = "11. 'shift+鼠标滚轮' 能够快速将图片放大/缩小。'ctrl+shift+鼠标滚轮' 能够极速i将图片放大/缩小。")
        self.myLabel_fastResize.pack(padx =10, pady=5, side=TOP)
        self.myLabel_labelEscResize = ttk.Label(top, text = "12. 'Esc' 在标注框文本内容时，点击ESC可以直接放弃操作退出。")
        self.myLabel_labelEscResize.pack(padx =10, pady=5, side=TOP)

    def send(self):
        # global username
        self.top_update.destroy()

    def onClick_update(self):
        top_update = self.top_update = ttk.Toplevel(root)
        top_update.title('更新信息')
        self.myLabel_Update = ttk.Label(top_update, text = " 2017.2.5 更新如下:\n\n\
            1. 矩形标注模式现在支持缩放下操作\n\n\
            2. 缩放下标注时， 或者滑动窗口时，点击鼠标右键将不会变回原图，而是停留在当前状态。\n\n\
            3. 缩放下或者滑动窗口时，点击删除将不会变回原图，而是停留在当前状态。\n\n\
            4. 增加“回车”跳图快捷键，且打开工具时自动会把输入框聚焦在输入跳图的框内。\n\n\
            5. 增加“INFO”来指引用户使用该标注工具。 \n\n\n\n\
            2017.2.16 更新： \n\n\
            1. 界面优化。\n\n\
            2. 增加文本内容读取与标注功能。\n\n\
            3. 针对大分辨率图片增加了快速缩放图片功能。\n\n\
            4. 文本框删除时会自动储存文本内容，方便修正时重新输入。 \n\n\
            5. 改进文本框内容标注时，不会变回原图大小。 \n\n\
            6. 修改文本bug修复，修复删除框之后显示问题。 \n\n\
            "
            )
        self.myLabel_Update.pack(padx =10, pady=5, side=TOP)

        self.myOKButton = ttk.Button(top_update, text='OK', command = self.send)
        self.myOKButton.pack()
        centerToplevel(self.top_update)
        root.wait_window(self.top_update)


def onClick(event=None):
    inputDialog = DialogINFO(root)
    centerToplevel(inputDialog.top)
    root.wait_window(inputDialog.top)


def centerToplevel(toplevel): # centered toplevelWindow
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w/2 - size[0]/2
    y = h/2 - size[1]/2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))


class ScrolledCanvas(Canvas):
    """
    a canvas in a container that automatically makes
    vertical and horizontal scroll bars for itself
    """
    def __init__(self,container):
        Canvas.__init__(self,container, cursor='tcross')

        self.vbar = Scrollbar(container)
        self.hbar = Scrollbar(container, orient = 'horizontal')



class LabelTool():
    def __init__(self, master): 
        self.parent = master
        self.parent.title("yl_LabelTool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = TRUE, height = TRUE)

        # initialize global state
        self.imageDir = ''
        self.imageList= []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''
        self.cur_ncr = 0
        self.x_move = 0
        self.y_move = 0
        self.tkimg = None
        self.points = [0, 0, 0, 0, 0, 0, 0, 0]
        self.tempCnt = '""'

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0
        self.STATE['continue'] = 0
        # quad_mode
        self.STATE['cor'] = self.points  # save coordinates
        self.STATE['counts'] = 0
        # quad_mode
        self.STATE['rot_cor'] = self.points  # save coordinates
        self.STATE['rot_counts'] = 0
        # attention change
        self.STATE['attention'] = 0  # switch for attention mode
        self.STATE['attFirst'] = 0  # swituch for change point attention
        self.STATE['attNext'] = 3

        # reference to bbox
        self.bboxIdList = []
        self.textIdList = []
        # recoke bounding boxes
        self.revokeBboxIdList = []
        self.revokeBboxList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None  
        self.vl = None  
        # ref lines for rot. mode.
        self.slope1 = None  
        self.slope2 = None  
        self.bboxId_1 = None # delete terms.
        self.bboxId_2 = None
        self.bboxId_3 = None
        self.bboxId1 = None # delete terms.
        self.bboxId2 = None
        self.bboxId3 = None
        # attention mode
        self.p1_bboxIdtemp = None 
        self.p1_bboxIdtemp3 = None
        self.p2_bboxIdtemp = None
        self.p2_bboxIdtemp3 = None
        self.p3_bboxIdtemp = None
        self.p3_bboxIdtemp3 = None
        self.p4_bboxIdtemp = None
        self.p4_bboxIdtemp3 = None
        self.end_bboxIdtemp = None
        self.end_bboxIdtemp3 = None
        self.end_bboxIdIndex = 0
        self.attx = 0
        self.atty = 0
        self.firstEnterAttention =  True
        self.mouseMoveEventx = 0 
        self.mouseMoveEventy = 0
        self.count_emphasize = 0
        self.rightCleanstate = 0

        # ----------------- GUI stuff ---------------------
        self.mainPanel = ScrolledCanvas(self.frame)
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.mainPanel.bind("<Button-3>", self.rightClean) # press 'BackSpace' to save bbox
        self.parent.bind("<Right>", lambda x: self.mainPanel.xview_scroll(1, "units"))
        self.parent.bind("<Left>", lambda x: self.mainPanel.xview_scroll(-1, "units"))
        self.parent.bind("<Up>", lambda x: self.mainPanel.yview_scroll(-1, "units"))
        self.parent.bind("<Down>", lambda x: self.mainPanel.yview_scroll(1, "units"))

        # self.parent.bind("<MouseWheel>", self.onZoomIn)
        self.parent.bind("<Button-4>", lambda x: self.zoomUp(1.1))
        self.parent.bind("<Button-5>", lambda x: self.zoomDown(1.1))
        self.parent.bind("<Shift-Button-4>", lambda x: self.zoomUp(1.61051))
        self.parent.bind("<Shift-Button-5>", lambda x: self.zoomDown(1.61051))
        self.parent.bind("<Control-Button-4>", lambda x: self.zoomUp(2.5937424601))
        self.parent.bind("<Control-Button-5>", lambda x: self.zoomDown(2.5937424601))

        self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
        self.parent.bind("b", self.prevImage) # press 'a' to go backforward
        self.parent.bind("f", self.nextImage) # press 'd' to go forward
        self.parent.bind("<Double-1>", self.typeText) # press 'BackSpace' to save bbox
        self.parent.bind("d",self.delBBox)
        self.parent.bind("r",self.switchMode)
        self.parent.bind("<Return>",self.gotoImage)
        self.parent.bind("i", onClick) 
        self.parent.bind("t", self.emphasize) 
        self.parent.bind("q", self.adjust) # do not use.
        self.parent.bind("<F1>", self.attentionTab) 
        # revoke. Undo last operation.
        self.parent.bind("<Control-z>", self.revoke) # do not use.

        self.mainPanel.vbar.grid(row = 1, column = 2, rowspan = 4, sticky = W+N+S)
        self.mainPanel.hbar.grid(row = 5, column = 1, sticky = W+E+N)
        self.mainPanel.grid(row = 1, column = 1, rowspan = 4, sticky = W+N)
        self.mainPanel.vbar.config(command = self.mainPanel.yview)       # call on scroll move
        self.mainPanel.hbar.config(command = self.mainPanel.xview)      # call on canvas movex
        self.mainPanel.config(yscrollcommand=self.mainPanel.vbar.set)
        self.mainPanel.config(xscrollcommand=self.mainPanel.hbar.set)

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text = 'Bounding boxes:')
        self.lb1.grid(row = 2, column = 3,  sticky = W+N)
        self.listbox = Listbox(self.frame, width = 42, height = 45, selectmode = 'extended', exportselection = 0) # 'multiple'
        self.listbox.grid(row = 3, column = 3, sticky = N)
        self.btnDel = Button(self.frame, text = 'SelectDelete (d)', command = self.delBBox)
        self.btnDel.grid(row = 4, column = 3, sticky = W+E+N)
        self.btnClear = Button(self.frame, text = 'Clear all boxes in current image', command = self.clearBBox) # clearALLBBox clearBBox
        self.btnClear.grid(row = 1, column = 3, sticky = W+E+N)

        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = 6, column = 1, columnspan = 2, sticky = W+E)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev (b)', width = 10, command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.nextBtn = Button(self.ctrPanel, text='Next (f) >>', width = 10, command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.progLabel = Label(self.ctrPanel, text = "Progress:     /    ")
        self.progLabel.pack(side = LEFT, padx = 5)
        self.tmpLabel = Label(self.ctrPanel, text = "Go to Image No.")
        self.tmpLabel.pack(side = LEFT, padx = 5)
        self.idxEntry = Entry(self.ctrPanel, width = 5, takefocus= "g")
        self.idxEntry.pack(side = LEFT)
        self.idxEntry.focus_force() 
        self.goBtn = Button(self.ctrPanel, text = 'Go (Enter) ', command = self.gotoImage)
        self.goBtn.pack(side = LEFT, padx =5)

        entrykwargs = dict(width = 6,  font = ('Helvetica', '14', 'bold'), justify = 'center', foreground = 'black', background = 'gray', state = 'normal', highlightbackground ='gray', relief = 'groove') #, textvariable = content)
        self.selectEntry = Entry(self.ctrPanel, **entrykwargs)
        self.selectEntry.pack(side = LEFT, padx = 0)
        # info button
        self.infoBtn = Button(self.ctrPanel, text = 'INFO (i)', width=5, foreground = 'black', command = onClick)
        self.infoBtn.pack(side = RIGHT, padx = 15)

        # r/q button
        self.btnSWmode = Button(self.ctrPanel, text = 'Ret/Quad (r)', command = self.switchMode)
        self.btnSWmode.pack(side = LEFT, padx=10)
        # ret/quad/rot show
        Mode_content=StringVar()
        Mode_content.set('Quad')
        entrykwargs = dict(width = 6,  font = ('Helvetica', '14', 'bold'), justify = 'center', foreground = 'red', background = 'gray', state = 'normal', highlightbackground ='gray', relief = 'groove', textvariable = Mode_content) #, textvariable = content)
        self.selectEntry2 = Entry(self.ctrPanel, **entrykwargs)
        self.selectEntry2.pack(side = LEFT, padx = 0)

        # show image file name
        fn = StringVar()
        fn.set('loading filename')
        entrykwargs = dict(width=20, justify='center', foreground='green',
                           background='white', state='normal', highlightbackground='white', relief='groove',
                           textvariable=fn)  # , textvariable = content)
        self.filenameShow = Entry(self.ctrPanel, **entrykwargs)
        self.filenameShow.pack(side=LEFT, padx=0)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side = RIGHT)

        self.frame.columnconfigure(1, weight = 1)
        self.frame.rowconfigure(4, weight = 1)

        self.loadDir()

    def loadDir(self, dbg = False):
        if not dbg:
            # s = self.entry.get()
            self.parent.focus()
            # self.category = int(s)
        self.imageDir = selfimageDir   # ch4_test_images text_image text_image
        self.imageListjpg = glob.glob(os.path.join(self.imageDir, '*.jpg'))
        self.imageListJPG = glob.glob(os.path.join(self.imageDir, '*.JPG'))
        self.imageListjpeg = glob.glob(os.path.join(self.imageDir, '*.jpeg'))
        self.imageListJPEG = glob.glob(os.path.join(self.imageDir, '*.JPEG'))
        self.imageListpng = glob.glob(os.path.join(self.imageDir, '*.png'))
        self.imageListPNG = glob.glob(os.path.join(self.imageDir, '*.PNG'))
        self.imageList = self.imageListjpg+ self.imageListJPG +self.imageListjpeg +self.imageListpng +self.imageListPNG +self.imageListJPEG
        self.imageList.sort()
        if len(self.imageList) == 0:
            print 'No images found in the specified dir!'
            return

        self.cur = 1
        self.total = len(self.imageList)

        self.outDir = selfoutDir
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        self.loadImage()

    def isCollectImage(self, labelname):
        self.selectEntry.delete(0, END)
        # print('collect_image/'+labelname[:-3]+'jpg', 'collect_image_label/'+labelname)
        if os.path.isfile('./collect_image/'+labelname[:-3]+'jpg') and os.path.isfile('./collect_image_label/'+labelname):
            self.selectEntry.insert(0, 'YES')
        else: 
            self.selectEntry.insert(0, 'NO')

    def swCollectImage(self, imagepath, imagename, labelname, labelfilename, imageform):
        if os.path.isfile('./collect_image/'+labelname[:-3]+'jpg') and os.path.isfile('./collect_image_label/'+labelname):
            os.remove('./collect_image/'+labelname[:-3]+'jpg')
            os.remove('./collect_image_label/'+labelname)
        else:
            shutil.copy(imagepath, 'collect_image/'+imagename+'.'+imageform)
            shutil.copy(labelfilename, 'collect_image_label/'+labelname)

    def loadImage(self):
        # load image
        imagepath = self.imageList[self.cur - 1]

        self.filenameShow.delete(0, END)
        self.filenameShow.insert(0, os.path.basename(imagepath))

        self.img = Image.open(imagepath)
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        
        fullsize = (0,0,self.tkimg.width(),self.tkimg.height())
        viewwide = min(self.tkimg.width(),1480)
        viewhigh = min(self.tkimg.height(),1030)

        self.mainPanel.delete('all')
        self.mainPanel.config(height = viewhigh, width = viewwide) # viewable window size
        self.mainPanel.config(scrollregion = fullsize)
        self.saveimage = self.img
        self.savephoto = self.tkimg
        ################################################################

        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        if self.tkimg.width()<= 1480 and self.tkimg.height()<=1030:
            self.parent.state('normal')
        else:
            if sys.platform[:3] == 'win':
                self.parent.state('zoomed')

        self.progLabel.config(text="%04d/%04d" %(self.cur, self.total))

        # load labels
        self.clearALLBBox()
        self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        bbox_cnt = 0

        # check if collected
        self.isCollectImage(labelname)

        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    if i == 0:
			try:
                            bbox_cnt = int(line.strip())
			except:
			    print (self.labelfilename)
                        continue
                    line_without_info = line.split(',')
                    tmp = [int(t.strip()) for t in line_without_info[:8]]

                    content_string = ''
                    if len(line_without_info) is 9:
                        content_string = line_without_info[8].strip()
                        if len(line_without_info) >9:
                            for string_label in line_without_info[9:]:
                                content_string +=','+string_label.strip()
                        self.bboxList.append(tuple(tmp+[content_string]))
                    else:
                        self.bboxList.append(tuple(tmp))
                    
                    tmpId=[0,0,0,0]
                    index_content = StringVar()
                    index_content.set(str(i))
                    textId = self.mainPanel.create_text(tmp[0], tmp[(1)], \
                                                            text = str(i), \
                                                            font =  24, \
                                                            anchor = 'nw', \
                                                            fill=COLORS[(len(self.bboxList)-1) % len(COLORS)])
                    self.textIdList.append(textId)
                    for j in range(4):
                        tmpId[j] = self.mainPanel.create_line(tmp[2*j%8], tmp[(2*j+1)%8], \
                                                            tmp[(2*j+2)%8], tmp[(2*j+3)%8], \
                                                            width = 2, \
                                                            fill=COLORS[(len(self.bboxList)-1) % len(COLORS)])
                    self.bboxIdList.append(tmpId) 
                    
                    if len(line_without_info) is 9:
                        self.listbox.insert(END, '%s (%d, %d)-> %s' %(str(i), tmp[0], tmp[1], content_string))    
                    else: 
                        self.listbox.insert(END, '%s (%d, %d)-> ' %(str(i), tmp[0], tmp[1]))
                    
                    self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])

    def drawImage(self, imgpil):
        tkimg = ImageTk.PhotoImage(imgpil)
        self.mainPanel.config(width = max(tkimg.width(), 400), height = max(tkimg.height(), 400))
        fullsize = (0,0,tkimg.width(),tkimg.height())
        viewwide = min(tkimg.width(),1480)
        viewhigh = min(tkimg.height(),1030)
        self.mainPanel.delete('all')
        self.mainPanel.config(height = viewhigh, width = viewwide) # viewable window size
        self.mainPanel.config(scrollregion = fullsize)
        self.mainPanel.create_image(0, 0, image = tkimg, anchor=NW)
        if self.tkimg.width()<= 1480 and self.tkimg.height()<=1030:
            self.parent.state('normal')
        else:
            if sys.platform[:3] == 'win':
                self.parent.state('zoomed')
        self.saveimage = imgpil
        self.savephoto = tkimg      
        self.progLabel.config(text = "%04d/%04d" %(self.cur, self.total))


        # load labels
        self.clearALLBBox()
        self.imagename = os.path.split(self.imageList[self.cur - 1])[-1].split('.')[0]
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        bbox_cnt = 0
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    if i == 0:
                        bbox_cnt = int(line.strip())
                        continue
                    line_without_info = line.split(',')
                    tmp = [int(t.strip()) for t in line_without_info[:8]]
                    # self.bboxList.append(tuple(tmp))
                    content_string = ''
                    if  len(line_without_info) is 9:
                        content_string = line_without_info[8].strip()
                        if len(line_without_info) >9:
                            for string_label in line_without_info[9:]:
                                content_string +=','+string_label.strip()
                        self.bboxList.append(tuple(tmp+[content_string]))
                    else:
                        self.bboxList.append(tuple(tmp))
                    
                    tmpId=[0,0,0,0]
                    
                    textId = self.mainPanel.create_text(tmp[0]*math.pow(1.10015,self.cur_ncr), tmp[(1)]*math.pow(1.10015,self.cur_ncr), \
                                                            text = str(i), \
                                                            font =  24, \
                                                            anchor = 'nw', \
                                                            fill=COLORS[(len(self.bboxList)-1) % len(COLORS)])
                    self.textIdList.append(textId)
                    for j in range(4):
                        tmpId[j] = self.mainPanel.create_line((int(tmp[2*j%8]*math.pow(1.10015,self.cur_ncr))), (int(tmp[(2*j+1)%8]* math.pow(1.10015,self.cur_ncr))), \
                                                            (int(tmp[(2*j+2)%8]* math.pow(1.10015,self.cur_ncr))), (int(tmp[(2*j+3)%8]* math.pow(1.10015,self.cur_ncr))), \
                                                            width = 2, \
                                                            fill=COLORS[(len(self.bboxList)-1) % len(COLORS)])
                        
                    self.bboxIdList.append(tmpId) 
                    
                    if  len(line_without_info) is 9:
                        self.listbox.insert(END, '%s (%d, %d)-> %s' %(str(i), tmp[0], tmp[1], content_string))    
                    else: 
                        self.listbox.insert(END, '%s (%d, %d)-> ' %(str(i), tmp[0], tmp[1]))
                    
                    self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])

    def saveImage(self):
        with open(self.labelfilename, 'w') as f:
            # f.write(str.encode('gbk'))
            f.write('%d\n' %len(self.bboxList))
            for bbox in self.bboxList:
                # print(bbox)
                if len(bbox) >= 9:
                    f.write(','.join(map(str, bbox[:8])))
                    reload(sys) 
                    sys.setdefaultencoding('utf-8')
                    f.write(','+ bbox[8].encode('utf-8') + '\n')
                    sys.setdefaultencoding('ascii')
                else:
                    f.write(','.join(map(str, bbox))+ '\n')

        print 'Image No. %d saved' %(self.cur)

    def mouseClick(self, event):
        self.x_move = self.tkimg.width() * self.mainPanel.hbar.get()[0]
        self.y_move = self.tkimg.height() * self.mainPanel.vbar.get()[0]
        event.x = (event.x/ math.pow(1.10015,self.cur_ncr)) + self.x_move
        event.y = (event.y/ math.pow(1.10015,self.cur_ncr)) + self.y_move
        event.x = int(event.x)
        event.y = int(event.y)
        if self.STATE['click'] == 0:
            self.bboxId1 = None
            self.bboxId2 = None
            self.bboxId3 = None
            self.bboxId_1 = None
            self.bboxId_2 = None
            self.bboxId_3 = None
            self.STATE['x'], self.STATE['y'] = event.x, event.y
            if self.STATE['attention'] ==0: # attention mode must not use simutaneously.
                self.STATE['click'] = 1 - self.STATE['click']
            self.STATE['counts'] = 0
            self.STATE['rot_counts'] = 0
            self.rightCleanstate = 1
        else:
            global isUseRectangle
            if isUseRectangle == 0:
                if self.STATE['counts']<2:
                    self.STATE['cor'][self.STATE['counts']], self.STATE['cor'][self.STATE['counts']+1] = self.STATE['x'], event.x
                    self.STATE['cor'][self.STATE['counts']+4], self.STATE['cor'][self.STATE['counts']+1+4] = self.STATE['y'], event.y
                    self.STATE['x'], self.STATE['y'] = event.x, event.y
                    self.STATE['counts'] +=1
                    if self.STATE['counts'] == 1:
                        self.bboxId_1 = self.bboxId # clean & delete
                        self.rightCleanstate = 2
                        # self.bboxIdList.append([self.bboxId])
                    if self.STATE['counts'] == 2:
                        self.bboxId_2 = self.bboxId
                        self.rightCleanstate = 3
                        # self.bboxIdList[-1] = self.bboxIdList[-1]+[self.bboxId]
                    self.bboxId = None
                    # self.listbox.itemconfig(len(self.bboxIdList), fg = COLORS[(len(self.bboxIdList)-1) % len(COLORS)])
                else:
                    self.rightCleanstate = 0
                    self.STATE['cor'][self.STATE['counts']], self.STATE['cor'][self.STATE['counts']+1] = self.STATE['x'], event.x
                    self.STATE['cor'][self.STATE['counts']+4], self.STATE['cor'][self.STATE['counts']+1+4] = self.STATE['y'], event.y
                    self.bboxList.append((self.STATE['cor'][0], self.STATE['cor'][4], self.STATE['cor'][1], self.STATE['cor'][5], self.STATE['cor'][2], self.STATE['cor'][6], self.STATE['cor'][3], self.STATE['cor'][7]))
                    # self.bboxIdList.append(self.bboxId)
                    self.bboxId_3 = self.bboxId
                    # self.bboxIdList[-1] = self.bboxIdList[-1]+[self.bboxId]
                    self.bboxId = self.mainPanel.create_line(int((self.STATE['cor'][3])* math.pow(1.10015,self.cur_ncr)), int((self.STATE['cor'][7])* math.pow(1.10015,self.cur_ncr)), \
                                                                int((self.STATE['cor'][0])* math.pow(1.10015,self.cur_ncr)), int((self.STATE['cor'][4])* math.pow(1.10015,self.cur_ncr)), \
                                                                width = 2, \
                                                                fill=COLORS[(len(self.bboxList)-1) % len(COLORS)])
                    # self.bboxId_4 = self.bboxId
                    # self.bboxIdList.append(self.bboxId)
                    # self.bboxIdList[-1] = self.bboxIdList[-1]+[self.bboxId]
                    self.bboxIdList.append([self.bboxId])
                    self.bboxIdList[-1] = self.bboxIdList[-1]+[self.bboxId_1]
                    self.bboxIdList[-1] = self.bboxIdList[-1]+[self.bboxId_2]
                    self.bboxIdList[-1] = self.bboxIdList[-1]+[self.bboxId_3]
                    # print(self.bboxIdList[-1])
                    self.bboxId = None
                    # self.endbboxId = None 
                    # if self.endbboxId:
                    #   self.mainPanel.delete(self.endbboxId)
                    #   print "here"
                    if len(self.bboxList[-1]) is 9:
                        self.listbox.insert(END, '(%d, %d)-> %s' %(self.bboxList[-1][0], self.bboxList[-1][1], self.bboxList[-1][8]))
                    else:    
                        self.listbox.insert(END, '(%d, %d)-> ' %(self.bboxList[-1][0], self.bboxList[-1][1]))
                    # self.listbox.insert(END, '(%d, %d) -> (%d, %d) -> (%d, %d) -> (%d, %d)' %(self.STATE['cor'][0], self.STATE['cor'][4], self.STATE['cor'][1], self.STATE['cor'][5], self.STATE['cor'][2], self.STATE['cor'][6], self.STATE['cor'][3], self.STATE['cor'][7]))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
                    self.STATE['cor'] = [0] * 8
                    self.STATE['counts']=0
                    self.STATE['click'] = 1 - self.STATE['click']
                    self.saveImage()
            elif isUseRectangle == 1:
                x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
                y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
                rt_cor = [int(x1), int(y1), int(x2), int(y1), int(x2), int(y2), int(x1), int(y2)]
                self.bboxList.append((rt_cor[0],rt_cor[1],rt_cor[2],rt_cor[3],rt_cor[4],rt_cor[5],rt_cor[6],rt_cor[7]))
                self.bboxIdList.append([self.bboxId])
                self.bboxIdList[-1] = self.bboxIdList[-1]+[self.bboxId1]
                self.bboxIdList[-1] = self.bboxIdList[-1]+[self.bboxId2]
                self.bboxIdList[-1] = self.bboxIdList[-1]+[self.bboxId3]
                # print(type(self.bboxId))
                self.bboxId = None
                self.bboxId1 = None
                self.bboxId2 = None
                self.bboxId3 = None
                if len(self.bboxList[-1]) is 9:
                    self.listbox.insert(END, '(%d, %d)-> %s' %(self.bboxList[-1][0], self.bboxList[-1][1], self.bboxList[-1][8]))
                else:    
                    self.listbox.insert(END, '(%d, %d)-> ' %(self.bboxList[-1][0], self.bboxList[-1][1]))
                # self.listbox.insert(END, '(%d, %d) -> (%d, %d) -> (%d, %d) -> (%d, %d)' %(rt_cor[0],rt_cor[1],rt_cor[2],rt_cor[3],rt_cor[4],rt_cor[5],rt_cor[6],rt_cor[7]))
                # print(len(self.bboxIdList))
                self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
                self.STATE['cor'] = [0] * 8
                self.STATE['counts']=0
                self.STATE['click'] = 1 - self.STATE['click']
                self.saveImage()
            elif isUseRectangle == 2:
                if self.STATE['rot_counts']<1:
                    self.STATE['rot_cor'][self.STATE['rot_counts']], self.STATE['rot_cor'][self.STATE['rot_counts']+1] = self.STATE['x'], event.x
                    self.STATE['rot_cor'][self.STATE['rot_counts']+4], self.STATE['rot_cor'][self.STATE['rot_counts']+1+4] = self.STATE['y'], event.y
                    self.STATE['x'], self.STATE['y'] = event.x, event.y
                    self.STATE['rot_counts'] += 2
                    # if self.STATE['rot_counts'] == 1:
                    self.bboxId_1 = self.bboxId # clean & delete
                    #     self.rightCleanstate = 2
                    #     # self.bboxIdList.append([self.bboxId])
                    self.bboxId = None
                    # ref lines for rot. mode.
                    self.Lbase = Line(Point(self.STATE['rot_cor'][0] *math.pow(1.10015,self.cur_ncr), self.STATE['rot_cor'][4] *math.pow(1.10015,self.cur_ncr)), Point(event.x *math.pow(1.10015,self.cur_ncr), event.y *math.pow(1.10015,self.cur_ncr)))
                    slope = self.Lbase.slope
                    slope_vert = -1/slope if slope != 0 else 100000
                    self.Lslope1 = Line(Point(self.STATE['rot_cor'][0], self.STATE['rot_cor'][4]), slope = slope_vert)
                    self.Lslope2 = Line(Point(event.x, event.y), slope = slope_vert)
                    cf1_p1 = -self.Lslope1.coefficients[2]/self.Lslope1.coefficients[1] if self.Lslope1.coefficients[1] !=0 else 10000*math.sign(slope_vert) # [0,y] [width,y]
                    cf1_p2 = (-self.Lslope1.coefficients[2] - self.Lslope1.coefficients[0]*self.tkimg.width())/self.Lslope1.coefficients[1] if self.Lslope1.coefficients[1] !=0 else 10000*math.sign(slope_vert) # [0,y] [width,y]
                    cf2_p1 = -self.Lslope2.coefficients[2]/self.Lslope2.coefficients[1] if self.Lslope2.coefficients[1] !=0 else 10000*math.sign(slope_vert) # [0,y] [width,y]
                    cf2_p2 = (-self.Lslope2.coefficients[2] - self.Lslope2.coefficients[0]*self.tkimg.width())/self.Lslope2.coefficients[1] if self.Lslope2.coefficients[1] !=0 else 10000*math.sign(slope_vert) # [0,y] [width,y]
                    self.slope1 =  self.mainPanel.create_line(0, int(cf1_p1 *math.pow(1.10015,self.cur_ncr)), self.tkimg.width() *math.pow(1.10015,self.cur_ncr), int(cf1_p2*math.pow(1.10015,self.cur_ncr)), width = 2, fill=COLORS[(len(self.bboxList)) % len(COLORS)])
                    self.slope2 = self.mainPanel.create_line(0, int(cf2_p1 *math.pow(1.10015,self.cur_ncr)), self.tkimg.width() *math.pow(1.10015,self.cur_ncr), int(cf2_p2*math.pow(1.10015,self.cur_ncr)), width = 2, fill=COLORS[(len(self.bboxList)) % len(COLORS)])
                else:
                    self.Lslope3 = Line(Point(event.x, event.y), slope = self.Lbase.slope)
                    inter_p1 = self.Lslope3.intersection(self.Lslope1)
                    inter_p2 = self.Lslope3.intersection(self.Lslope2)
                    self.bboxId_2 = self.mainPanel.create_line(int(inter_p1[0][0]*math.pow(1.10015,self.cur_ncr)), int(inter_p1[0][1]*math.pow(1.10015,self.cur_ncr)), int(self.STATE['rot_cor'][0]*math.pow(1.10015,self.cur_ncr)), int(self.STATE['rot_cor'][4]*math.pow(1.10015,self.cur_ncr)), width = 2, fill=COLORS[(len(self.bboxList)) % len(COLORS)])
                    self.bboxId_3 = self.mainPanel.create_line(int(self.STATE['rot_cor'][1]*math.pow(1.10015,self.cur_ncr)), int(self.STATE['rot_cor'][5]*math.pow(1.10015,self.cur_ncr)), int(inter_p2[0][0]*math.pow(1.10015,self.cur_ncr)), int(inter_p2[0][1]*math.pow(1.10015,self.cur_ncr)), width = 2, fill=COLORS[(len(self.bboxList)) % len(COLORS)])
                    self.bboxId = self.mainPanel.create_line(int(inter_p1[0][0]*math.pow(1.10015,self.cur_ncr)), int(inter_p1[0][1]*math.pow(1.10015,self.cur_ncr)), int(inter_p2[0][0]*math.pow(1.10015,self.cur_ncr)), int(inter_p2[0][1]*math.pow(1.10015,self.cur_ncr)), width = 2, fill=COLORS[(len(self.bboxList)) % len(COLORS)])
                    self.STATE['rot_cor'][self.STATE['rot_counts']], self.STATE['rot_cor'][self.STATE['rot_counts']+1] = inter_p2[0][0], inter_p1[0][0]
                    self.STATE['rot_cor'][self.STATE['rot_counts']+4], self.STATE['rot_cor'][self.STATE['rot_counts']+1+4] = inter_p2[0][1], inter_p1[0][1]
                    self.STATE['rot_cor'] = [int(kkeach) for kkeach in self.STATE['rot_cor']]
                    self.bboxList.append((self.STATE['rot_cor'][0], self.STATE['rot_cor'][4], self.STATE['rot_cor'][1], self.STATE['rot_cor'][5], self.STATE['rot_cor'][2], self.STATE['rot_cor'][6], self.STATE['rot_cor'][3], self.STATE['rot_cor'][7]))
                    # self.bboxId_3 = self.bboxId
                    # self.bboxId = self.mainPanel.create_line(int((self.STATE['rot_cor'][3])* math.pow(1.10015,self.cur_ncr)), int((self.STATE['rot_cor'][7])* math.pow(1.10015,self.cur_ncr)), \
                    #                                             int((self.STATE['rot_cor'][0])* math.pow(1.10015,self.cur_ncr)), int((self.STATE['rot_cor'][4])* math.pow(1.10015,self.cur_ncr)), \
                    #                                             width = 2, \
                    #                                             fill=COLORS[(len(self.bboxList)-1) % len(COLORS)])
                    self.mainPanel.delete(self.slope1)
                    self.mainPanel.delete(self.slope2)
                    self.bboxIdList.append([self.bboxId])
                    self.bboxIdList[-1] = self.bboxIdList[-1]+[self.bboxId_1]
                    self.bboxIdList[-1] = self.bboxIdList[-1]+[self.bboxId_2]
                    self.bboxIdList[-1] = self.bboxIdList[-1]+[self.bboxId_3]
                    self.bboxId = None
                    self.bboxId_1 = None
                    self.bboxId_2 = None
                    self.bboxId_3 = None
                    if len(self.bboxList[-1]) is 9:
                        self.listbox.insert(END, '(%d, %d)-> %s' %(self.bboxList[-1][0], self.bboxList[-1][1], self.bboxList[-1][8]))
                    else:    
                        self.listbox.insert(END, '(%d, %d)-> ' %(self.bboxList[-1][0], self.bboxList[-1][1]))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
                    self.STATE['rot_cor'] = [0] * 8
                    self.STATE['rot_counts']=0
                    self.STATE['click'] = 1 - self.STATE['click']
                    self.saveImage()
            else:
                assert(0)

    def mouseMove(self, event):
        self.x_move = self.tkimg.width() * self.mainPanel.hbar.get()[0]
        self.y_move = self.tkimg.height() * self.mainPanel.vbar.get()[0]
        event.x = (event.x/ math.pow(1.10015,self.cur_ncr)) + self.x_move
        event.y = (event.y/ math.pow(1.10015,self.cur_ncr)) + self.y_move
        event.x = int(event.x)
        event.y = int(event.y)
        self.mouseMoveEventx = int(event.x)
        self.mouseMoveEventy = int(event.y)
            # print self.cur_ncr
        self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(-10, event.y *math.pow(1.10015,self.cur_ncr), self.tkimg.width()* math.pow(1.10015,self.cur_ncr), event.y * math.pow(1.10015,self.cur_ncr), width = 2)
            # print event.y
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x * math.pow(1.10015,self.cur_ncr), 0, event.x *math.pow(1.10015,self.cur_ncr), self.tkimg.height()* math.pow(1.10015,self.cur_ncr), width = 2)

        ##################### Attention Mode #################################
        if self.STATE['click'] == 0 and self.STATE['attention'] == 1: # for attention_mode self.listbox.curselection()
            if self.STATE['attFirst'] == 0:
                # print(int(event.x), int(event.y))
                if self.STATE['attNext'] == 3:
                    if self.firstEnterAttention is False:
                        # print(self.STATE['attNext'])
                        self.end_bboxIdIndex = 2 
                        self.bboxIdList[int(self.listbox.curselection()[0])][2] = self.p4_bboxIdtemp
                        self.bboxIdList[int(self.listbox.curselection()[0])][3] = self.p4_bboxIdtemp3
                        self.attx = int((event.x))
                        self.atty = int((event.y))
                        self.bboxList[int(self.listbox.curselection()[0])] = tuple(self.bboxList[int(self.listbox.curselection()[0])][:6]+(self.attx, self.atty)+self.bboxList[int(self.listbox.curselection()[0])][8:])
                        self.saveImage()
                        # self.listbox.delete(int(self.listbox.curselection()[0]))
                        # if len(self.bboxList[int(self.listbox.curselection()[0])]) == 9:
                        #     self.listbox.insert(int(self.listbox.curselection()[0]), '(%d, %d)-> %s' %(self.attx, self.atty, self.bboxList[int(self.listbox.curselection()[0])][8]))
                        # else:
                        #     self.listbox.insert(int(self.listbox.curselection()[0]), '(%d, %d)-> ' %(self.attx, self.atty))
                        # self.listbox.itemconfig(int(self.listbox.curselection()[0]), fg = COLORS[(int(self.listbox.curselection()[0])) % len(COLORS)])
                    self.firstEnterAttention = False
                    # print(self.STATE['quitAttention'])
                    # if self.STATE['quitAttention'] == True:
                    #     self.STATE['quitAtt'] = 1 - self.STATE['quitAtt']
                    self.STATE['attNext'] = (self.STATE['attNext'] + 1)%4
                    # print(self.bboxIdList[int(self.listbox.curselection()[0])])
                    self.mainPanel.delete(self.bboxIdList[int(self.listbox.curselection()[0])][3])
                    self.mainPanel.delete(self.bboxIdList[int(self.listbox.curselection()[0])][0])
                if self.p1_bboxIdtemp:
                    self.mainPanel.delete(self.p1_bboxIdtemp)
                if self.p1_bboxIdtemp3:
                    self.mainPanel.delete(self.p1_bboxIdtemp3)
                self.end_bboxIdtemp = self.p1_bboxIdtemp = self.mainPanel.create_line( self.bboxList[int(self.listbox.curselection()[0])][6]  * math.pow(1.10015,self.cur_ncr), self.bboxList[int(self.listbox.curselection()[0])][7] * math.pow(1.10015,self.cur_ncr), \
                                                                int((event.x)* math.pow(1.10015,self.cur_ncr)), int((event.y)* math.pow(1.10015,self.cur_ncr)), \
                                                                width = 2, \
                                                                fill=COLORS[int(self.listbox.curselection()[0]) % len(COLORS)])
                self.end_bboxIdtemp3 = self.p1_bboxIdtemp3 = self.mainPanel.create_line(self.bboxList[int(self.listbox.curselection()[0])][2]* math.pow(1.10015,self.cur_ncr), self.bboxList[int(self.listbox.curselection()[0])][3]* math.pow(1.10015,self.cur_ncr), \
                                                                int((event.x)* math.pow(1.10015,self.cur_ncr)), int((event.y)* math.pow(1.10015,self.cur_ncr)), \
                                                                width = 2, \
                                                                fill=COLORS[int(self.listbox.curselection()[0]) % len(COLORS)])
            elif self.STATE['attFirst'] == 1:
                if self.STATE['attNext'] == 0:
                    self.end_bboxIdIndex = 3
                    self.bboxIdList[int(self.listbox.curselection()[0])][3] = self.p1_bboxIdtemp
                    self.bboxIdList[int(self.listbox.curselection()[0])][0] = self.p1_bboxIdtemp3
                    self.attx = int((event.x))
                    self.atty = int((event.y))
                    self.bboxList[int(self.listbox.curselection()[0])] = tuple((self.attx, self.atty) + self.bboxList[int(self.listbox.curselection()[0])][2:])
                    # self.listbox.delete(int(self.listbox.curselection()[0]))
                    # if len(self.bboxList[int(self.listbox.curselection()[0])]) == 9:
                    #     self.listbox.insert(int(self.listbox.curselection()[0]), '(%d, %d)-> %s' %(self.attx, self.atty, self.bboxList[int(self.listbox.curselection()[0])][8]))
                    # else:
                    #     self.listbox.insert(int(self.listbox.curselection()[0]), '(%d, %d)-> ' %(self.attx, self.atty))
                    # self.listbox.itemconfig(int(self.listbox.curselection()[0]), fg = COLORS[(int(self.listbox.curselection()[0])) % len(COLORS)])
                    self.saveImage()
                    # print(self.STATE['quitAttention'])
                    # if self.STATE['quitAttention'] == True:
                    #     self.STATE['quitAtt'] = 1 - self.STATE['quitAtt']
                    self.STATE['attNext'] = (self.STATE['attNext'] + 1)%4
                    # print(self.bboxIdList[int(self.listbox.curselection()[0])])
                    self.mainPanel.delete(self.bboxIdList[int(self.listbox.curselection()[0])][0])
                    self.mainPanel.delete(self.bboxIdList[int(self.listbox.curselection()[0])][1])
                if self.p2_bboxIdtemp:
                    self.mainPanel.delete(self.p2_bboxIdtemp)
                if self.p2_bboxIdtemp3:
                    self.mainPanel.delete(self.p2_bboxIdtemp3)
                self.end_bboxIdtemp = self.p2_bboxIdtemp = self.mainPanel.create_line( self.bboxList[int(self.listbox.curselection()[0])][0]  * math.pow(1.10015,self.cur_ncr), self.bboxList[int(self.listbox.curselection()[0])][1] * math.pow(1.10015,self.cur_ncr), \
                                                                int((event.x)* math.pow(1.10015,self.cur_ncr)), int((event.y)* math.pow(1.10015,self.cur_ncr)), \
                                                                width = 2, \
                                                                fill=COLORS[int(self.listbox.curselection()[0]) % len(COLORS)])
                self.end_bboxIdtemp3 = self.p2_bboxIdtemp3 = self.mainPanel.create_line(self.bboxList[int(self.listbox.curselection()[0])][4]* math.pow(1.10015,self.cur_ncr), self.bboxList[int(self.listbox.curselection()[0])][5]* math.pow(1.10015,self.cur_ncr), \
                                                                int((event.x)* math.pow(1.10015,self.cur_ncr)), int((event.y)* math.pow(1.10015,self.cur_ncr)), \
                                                                width = 2, \
                                                                fill=COLORS[int(self.listbox.curselection()[0]) % len(COLORS)])
            elif self.STATE['attFirst'] == 2:
                if self.STATE['attNext'] == 1:
                    self.end_bboxIdIndex = 0
                    self.bboxIdList[int(self.listbox.curselection()[0])][0] = self.p2_bboxIdtemp
                    self.bboxIdList[int(self.listbox.curselection()[0])][1] = self.p2_bboxIdtemp3
                    self.attx = int((event.x))
                    self.atty = int((event.y))
                    self.bboxList[int(self.listbox.curselection()[0])] = tuple(self.bboxList[int(self.listbox.curselection()[0])][:2]+(self.attx, self.atty)+self.bboxList[int(self.listbox.curselection()[0])][4:])
                    # self.listbox.delete(int(self.listbox.curselection()[0]))
                    # if len(self.bboxList[int(self.listbox.curselection()[0])]) == 9:
                    #     self.listbox.insert(int(self.listbox.curselection()[0]), '(%d, %d)-> %s' %(self.attx, self.atty, self.bboxList[int(self.listbox.curselection()[0])][8]))
                    # else:
                    #     self.listbox.insert(int(self.listbox.curselection()[0]), '(%d, %d)-> ' %(self.attx, self.atty))
                    # self.listbox.itemconfig(int(self.listbox.curselection()[0]), fg = COLORS[(int(self.listbox.curselection()[0])) % len(COLORS)])
                    self.saveImage()
                    # print(self.STATE['quitAttention'])
                    # if self.STATE['quitAttention'] == True:
                    #     self.STATE['quitAtt'] = 1 - self.STATE['quitAtt']
                    self.STATE['attNext'] = (self.STATE['attNext'] + 1)%4
                    # print(self.bboxIdList[int(self.listbox.curselection()[0])])
                    self.mainPanel.delete(self.bboxIdList[int(self.listbox.curselection()[0])][1])
                    self.mainPanel.delete(self.bboxIdList[int(self.listbox.curselection()[0])][2])
                if self.p3_bboxIdtemp:
                    self.mainPanel.delete(self.p3_bboxIdtemp)
                if self.p3_bboxIdtemp3:
                    self.mainPanel.delete(self.p3_bboxIdtemp3)
                self.end_bboxIdtemp = self.p3_bboxIdtemp = self.mainPanel.create_line( self.bboxList[int(self.listbox.curselection()[0])][2]  * math.pow(1.10015,self.cur_ncr), self.bboxList[int(self.listbox.curselection()[0])][3] * math.pow(1.10015,self.cur_ncr), \
                                                                int((event.x)* math.pow(1.10015,self.cur_ncr)), int((event.y)* math.pow(1.10015,self.cur_ncr)), \
                                                                width = 2, \
                                                                fill=COLORS[int(self.listbox.curselection()[0]) % len(COLORS)])
                self.end_bboxIdtemp3 = self.p3_bboxIdtemp3 = self.mainPanel.create_line(self.bboxList[int(self.listbox.curselection()[0])][6]* math.pow(1.10015,self.cur_ncr), self.bboxList[int(self.listbox.curselection()[0])][7]* math.pow(1.10015,self.cur_ncr), \
                                                                int((event.x)* math.pow(1.10015,self.cur_ncr)), int((event.y)* math.pow(1.10015,self.cur_ncr)), \
                                                                width = 2, \
                                                                fill=COLORS[int(self.listbox.curselection()[0]) % len(COLORS)])
            elif self.STATE['attFirst'] == 3:
                if self.STATE['attNext'] == 2:
                    self.end_bboxIdIndex = 1
                    self.bboxIdList[int(self.listbox.curselection()[0])][1] = self.p3_bboxIdtemp
                    self.bboxIdList[int(self.listbox.curselection()[0])][2] = self.p3_bboxIdtemp3
                    self.attx = int((event.x))
                    self.atty = int((event.y))
                    self.bboxList[int(self.listbox.curselection()[0])] = tuple(self.bboxList[int(self.listbox.curselection()[0])][:4]+(self.attx, self.atty)+self.bboxList[int(self.listbox.curselection()[0])][6:])
                    # self.listbox.delete(int(self.listbox.curselection()[0]))
                    # if len(self.bboxList[int(self.listbox.curselection()[0])]) == 9:
                    #     self.listbox.insert(int(self.listbox.curselection()[0]), '(%d, %d)-> %s' %(self.attx, self.atty, self.bboxList[int(self.listbox.curselection()[0])][8]))
                    # else:
                    #     self.listbox.insert(int(self.listbox.curselection()[0]), '(%d, %d)-> ' %(self.attx, self.atty))
                    # self.listbox.itemconfig(int(self.listbox.curselection()[0]), fg = COLORS[(int(self.listbox.curselection()[0])) % len(COLORS)])
                    self.saveImage()
                    # print(self.STATE['quitAttention'])
                    # if self.STATE['quitAttention'] == True:
                    #     self.STATE['quitAtt'] = 1 - self.STATE['quitAtt']
                    self.STATE['attNext'] = (self.STATE['attNext'] + 1)%4
                    # print(self.bboxIdList[int(self.listbox.curselection()[0])])
                    self.mainPanel.delete(self.bboxIdList[int(self.listbox.curselection()[0])][2])
                    self.mainPanel.delete(self.bboxIdList[int(self.listbox.curselection()[0])][3])
                if self.p4_bboxIdtemp:
                    self.mainPanel.delete(self.p4_bboxIdtemp)
                if self.p4_bboxIdtemp3:
                    self.mainPanel.delete(self.p4_bboxIdtemp3)
                self.end_bboxIdtemp = self.p4_bboxIdtemp = self.mainPanel.create_line( self.bboxList[int(self.listbox.curselection()[0])][4]  * math.pow(1.10015,self.cur_ncr), self.bboxList[int(self.listbox.curselection()[0])][5] * math.pow(1.10015,self.cur_ncr), \
                                                                int((event.x)* math.pow(1.10015,self.cur_ncr)), int((event.y)* math.pow(1.10015,self.cur_ncr)), \
                                                                width = 2, \
                                                                fill=COLORS[int(self.listbox.curselection()[0]) % len(COLORS)])
                self.end_bboxIdtemp3 = self.p4_bboxIdtemp3 = self.mainPanel.create_line(self.bboxList[int(self.listbox.curselection()[0])][0]* math.pow(1.10015,self.cur_ncr), self.bboxList[int(self.listbox.curselection()[0])][1]* math.pow(1.10015,self.cur_ncr), \
                                                                int((event.x)* math.pow(1.10015,self.cur_ncr)), int((event.y)* math.pow(1.10015,self.cur_ncr)), \
                                                                width = 2, \
                                                                fill=COLORS[int(self.listbox.curselection()[0]) % len(COLORS)])               
        ##################### Attention Mode #################################

        if 1 == self.STATE['click']:
            if self.bboxId: 
                self.mainPanel.delete(self.bboxId)
            if self.bboxId1: 
                self.mainPanel.delete(self.bboxId1)
            if self.bboxId2: 
                self.mainPanel.delete(self.bboxId2)
            if self.bboxId3: 
                self.mainPanel.delete(self.bboxId3)
                
            global isUseRectangle
            if isUseRectangle == 0:
                self.bboxId = self.mainPanel.create_line(int((self.STATE['x'])* math.pow(1.10015,self.cur_ncr)), int((self.STATE['y'])* math.pow(1.10015,self.cur_ncr)), \
                                                            int((event.x)* math.pow(1.10015,self.cur_ncr)), int((event.y)* math.pow(1.10015,self.cur_ncr)), \
                                                            width = 2, \
                                                            fill=COLORS[(len(self.bboxList)) % len(COLORS)])
            elif isUseRectangle == 1:
                # self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
                #                                                 event.x, event.y, \
                #                                                 width = 2, \
                #                                                 outline = COLORS[len(self.bboxList) % len(COLORS)])
                # self.bboxId = self.mainPanel.create_rectangle(self.STATE['x']* math.pow(1.10015,self.cur_ncr), self.STATE['y']* math.pow(1.10015,self.cur_ncr), \
                #                                                 int((event.x)* math.pow(1.10015,self.cur_ncr)), int((event.y)* math.pow(1.10015,self.cur_ncr)), \
                #                                                 width = 2, \
                #                                                 outline = COLORS[len(self.bboxList) % len(COLORS)])
                self.bboxId = self.mainPanel.create_line(self.STATE['x']* math.pow(1.10015,self.cur_ncr), self.STATE['y']* math.pow(1.10015,self.cur_ncr), \
                                                                int((event.x)* math.pow(1.10015,self.cur_ncr)), self.STATE['y']* math.pow(1.10015,self.cur_ncr), \
                                                                width = 2, \
                                                                fill=COLORS[(len(self.bboxList)) % len(COLORS)])
                self.bboxId1 = self.mainPanel.create_line(int((event.x)* math.pow(1.10015,self.cur_ncr)), self.STATE['y']* math.pow(1.10015,self.cur_ncr), \
                                                                int((event.x)* math.pow(1.10015,self.cur_ncr)), int((event.y)* math.pow(1.10015,self.cur_ncr)), \
                                                                width = 2, \
                                                                fill=COLORS[(len(self.bboxList)) % len(COLORS)])
                self.bboxId2 = self.mainPanel.create_line(int((event.x)* math.pow(1.10015,self.cur_ncr)), int((event.y)* math.pow(1.10015,self.cur_ncr)), \
                                                                self.STATE['x']* math.pow(1.10015,self.cur_ncr), int((event.y)* math.pow(1.10015,self.cur_ncr)), \
                                                                width = 2, \
                                                                fill=COLORS[(len(self.bboxList)) % len(COLORS)])
                self.bboxId3 = self.mainPanel.create_line(self.STATE['x']* math.pow(1.10015,self.cur_ncr), int((event.y)* math.pow(1.10015,self.cur_ncr)), \
                                                                self.STATE['x']* math.pow(1.10015,self.cur_ncr), self.STATE['y']* math.pow(1.10015,self.cur_ncr), \
                                                                width = 2, \
                                                                fill=COLORS[(len(self.bboxList)) % len(COLORS)])
            elif isUseRectangle == 2:
                if self.STATE['rot_counts'] == 0:
                    self.bboxId = self.mainPanel.create_line(int((self.STATE['x'])* math.pow(1.10015,self.cur_ncr)), int((self.STATE['y'])* math.pow(1.10015,self.cur_ncr)), \
                                                            int((event.x)* math.pow(1.10015,self.cur_ncr)), int((event.y)* math.pow(1.10015,self.cur_ncr)), \
                                                            width = 2, \
                                                            fill=COLORS[(len(self.bboxList)) % len(COLORS)])
            else:
                assert(0)
                # self.mainPanel.delete(self.bboxId)
        # if 1 == self.STATE['continue']:
        #   self.STATE['x'], self.STATE['y'] = event.x, event.y
        #   self.STATE['continue'] =0f
        #   self.bboxIdList.append(self.bboxId)

    def emphasize(self,event):
        sel = self.listbox.curselection()
        # print(1111)
        # self.cancelBBox(event)
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        # font = ('Helvetica', '14', 'bold'), foreground='black', background='white', relief ='groove'
        self.focuseBBox = self.mainPanel.create_text(int(self.bboxList[idx][0]*math.pow(1.10015,self.cur_ncr)), int(self.bboxList[idx][1]*math.pow(1.10015,self.cur_ncr)), text="(*^ _ ^*)", font = ('Helvetica', '25', 'bold'), fill = 'black')
        # self.focuseBBox = self.mainPanel.create_text(int(self.bboxList[idx][0]*math.pow(1.10015,self.cur_ncr)), int(self.bboxList[idx][1]*math.pow(1.10015,self.cur_ncr)), text="(*^ _ ^*)", font = ('Helvetica', '25', 'bold'), fill = 'black')
        # self.focuseBBoxArrow = self.mainPanel.create_text(int(self.bboxList[idx][0]*math.pow(1.10015,self.cur_ncr)), int(self.bboxList[idx][1]*math.pow(1.10015,self.cur_ncr)), text="↘", font = ('Helvetica', '25', 'bold'), fill = 'white')
        self.focuseBBoxArrow = self.mainPanel.create_text(int(self.bboxList[idx][0]*math.pow(1.10015,self.cur_ncr)), int(self.bboxList[idx][1]*math.pow(1.10015,self.cur_ncr)), text=str(self.count_emphasize), font = ('Helvetica', '25', 'bold'), fill = 'white')
        self.count_emphasize +=1
        # print self.bboxList[idx][0]

    def cancelBBox(self, event):
        self.bboxId = None
        self.STATE['click'] = 0
        self.count_emphasize =0 
        self.nextImage()
        self.prevImage()

    def delBBox(self, event = None):
        sel = self.listbox.curselection()
        self.count_emphasize =0 
        # print(len(sel))
        self.revokeBboxIdList = []
        self.revokeBboxList = []
        if len(sel) is 1: # save current delete
            if len(self.bboxList[int(sel[0])]) is 9:
                self.tempCnt = self.bboxList[int(sel[0])][8].strip()               
        for ix,i in enumerate(sel):
            idx = int(i) - ix
            try:
                self.mainPanel.delete(self.textIdList[idx])
            except Exception:
                NotImplemented
            for k in xrange(4):
                try:
                    self.mainPanel.delete(self.bboxIdList[idx][k])
                except Exception,e:
                    self.mainPanel.delete(self.bboxIdList[idx])
            self.revokeBboxIdList.append(self.bboxIdList[idx])
            self.revokeBboxList.append(self.bboxList[idx])

            self.bboxIdList.pop(idx)
            self.bboxList.pop(idx)
            self.listbox.delete(idx)
        # if len(sel)>1:
        #     self.nextImage()
        #     self.prevImage()      
        self.saveImage()
        
    def revoke(self, event=None):
        print('enter_revoke_mode')
        assert(len(self.revokeBboxList) == len(self.revokeBboxIdList)), 'the number of revoke bounding boxes should be the same. ' +str(len(self.revokeBboxList)) +' ' +str(len(self.revokeBboxIdList))
        lenRevoke = len(self.revokeBboxList)
        if(lenRevoke == 0):
            return
        for ix in xrange(lenRevoke):
            self.bboxIdList.append(self.revokeBboxIdList[ix])
            # for ict in xrange(len(self.revokeBboxList[ix])):
            #     print(self.revokeBboxList[ix][ict])
            self.bboxList.append(self.revokeBboxList[ix])
            lenListbox = len(self.bboxIdList)
            if  len(self.revokeBboxList[ix]) is 9:
                self.listbox.insert(END, '%s (%d, %d)-> %s' %(str(lenListbox+1), self.revokeBboxList[ix][0], self.revokeBboxList[ix][1], str(self.revokeBboxList[ix][8].strip())))    
            else: 
                self.listbox.insert(END, '%s (%d, %d)-> ' %(str(lenListbox+1), self.revokeBboxList[ix][0], self.revokeBboxList[ix][1]))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
        self.nextImage()
        self.prevImage()      
        self.saveImage()

    def rightClean(self, event):
        # self.bboxId = None
        if self.rightCleanstate == 0:
            return
        if self.rightCleanstate >= 1:
            self.mainPanel.delete(self.bboxId)
        if self.rightCleanstate >= 2:
            try:
                self.mainPanel.delete(self.bboxId_1)
            except Exception, e:
                NotImplemented
        if self.rightCleanstate == 3:
            try:
                self.mainPanel.delete(self.bboxId_2)
            except Exception, e:
                NotImplemented
        try:
            self.mainPanel.delete(self.bboxId_1)
        except Exception, e:
            NotImplemented
        try:
            self.mainPanel.delete(self.bboxId_2)
        except Exception, e:
            NotImplemented
        try:
            self.mainPanel.delete(self.bboxId1)
        except Exception, e:
            NotImplemented
        try:
            self.mainPanel.delete(self.bboxId2)
        except Exception, e:
            NotImplemented
        try:
            self.mainPanel.delete(self.bboxId3)
        except Exception, e:
            NotImplemented
        try:
            self.mainPanel.delete(self.bboxId_3)
        except Exception, e:
            NotImplemented
        try:
            self.mainPanel.delete(self.slope1)
        except Exception, e:
            NotImplemented
        try:
            self.mainPanel.delete(self.slope2)
        except Exception, e:
            NotImplemented
        # try:
        #     self.mainPanel.delete(self.bboxId1)
        # except Exception, e:
        #     NotImplemented
        # try:
        #     self.mainPanel.delete(self.bboxId2)
        # except Exception, e:
        #     NotImplemented
        # try:
        #     self.mainPanel.delete(self.bboxId3)
        # except Exception, e:
        #     NotImplemented
        self.STATE['click'] = 0
        self.bboxId_1 = None
        self.bboxId_2 = None
        self.bboxId_3 = None
        self.bboxId1 = None
        self.bboxId2 = None
        self.bboxId3 = None
        self.count_emphasize = 0 
        self.rightCleanstate = 0
        # self.nextImage()
        # self.prevImage()

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.revokeBboxIdList = []
        self.revokeBboxList = []
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.textIdList = []
        self.bboxList = []
        self.count_emphasize =0 
        self.nextImage()
        self.prevImage()


    def clearALLBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
            try:
                self.mainPanel.delete(self.textIdList[idx])
            except Exception:
                NotImplemented
        self.listbox.delete(0, len(self.bboxList))
        self.revokeBboxIdList = []
        self.revokeBboxList = []
        self.bboxIdList = []
        self.textIdList = []
        self.bboxList = []   
        self.count_emphasize =0 
        # self.nextImage()
        # self.prevImage()

    def switchMode(self, event=None):
        global isUseRectangle
        isUseRectangle += 1
        if isUseRectangle > 2:
            isUseRectangle = 0
        self.selectEntry2.delete(0, END)
        # print('collect_image/'+labelname[:-3]+'jpg', 'collect_image_label/'+labelname)
        if isUseRectangle == 0:
            self.selectEntry2.insert(0, 'Quad')
        elif isUseRectangle == 1: 
            self.selectEntry2.insert(0, 'Rect')
        elif isUseRectangle == 2: 
            self.selectEntry2.insert(0, 'Rot.')
        else:
            assert(0)
        # if isUseRectangle:
            # print(isUseRectangle)

    def prevImage(self, event = None):
        self.bboxId_1 = None
        self.bboxId_2 = None
        self.bboxId_3 = None
        self.revokeBboxIdList = []
        self.revokeBboxList = []
        self.saveImage()
        self.cur_ncr = 0
        self.x_move = 0
        self.y_move = 0
        self.count_emphasize = 0 
        if self.cur > 1:
            self.cur -= 1
        self.loadImage()

    def nextImage(self, event = None):
        self.bboxId_1 = None
        self.bboxId_2 = None
        self.bboxId_3 = None
        self.revokeBboxIdList = []
        self.revokeBboxList = []
        self.saveImage()
        self.cur_ncr = 0
        self.x_move = 0
        self.y_move = 0
        self.count_emphasize = 0 
        if self.cur < self.total:
            self.cur += 1
        self.loadImage()

    def gotoImage(self, event = None):
        try:
            idx = int(self.idxEntry.get())
            if 1 <= idx and idx <= self.total:
                self.revokeBboxIdList = []
                self.revokeBboxList = []
                self.saveImage()
                self.cur_ncr = 0
                self.x_move = 0
                self.y_move = 0
                self.cur = idx
                self.loadImage()
        except Exception, e:
            NotImplemented
        # isinstance(lst, (int, str, list))  type(idx) == type(1)
        self.idxEntry.delete(0, END)
    
    def collectFile(self, event=None):
        self.saveImage()
        if not os.path.isdir('collect_image/'): os.mkdir('collect_image')
        if not os.path.isdir('collect_image_label/'): os.mkdir('collect_image_label')
        imagepath = self.imageList[self.cur-1]
        imagename = os.path.split(imagepath)[-1].split('.')[0]
        imageform = os.path.split(imagepath)[-1].split('.')[1]
        labelname = imagename + '.txt'
        labelfilename = os.path.join(self.outDir, labelname)
        # print(imagepath, imagename, labelname, labelfilename)
        # shutil.copy(imagepath, 'collect_image/'+imagename+'.'+imageform)
        # shutil.copy(labelfilename, 'collect_image_label/'+labelname)
        self.swCollectImage(imagepath, imagename, labelname, labelfilename, imageform)
        self.isCollectImage(labelname)
        # print 'yea?'

    def zoomDown(self, factor):
        # zoom in or out in increments
        self.count_emphasize =0 
        count = int(round(math.log(factor, 1.1)))
        self.cur_ncr = self.cur_ncr-count 
        imgpil = self.saveimage
        wide, high = imgpil.size
        # if self.cur_ncr < 0:
        #   filter = Image.ANTIALIAS
        # else:
        #   filter = Image.BICUBIC
        # new = imgpil.resize((int(wide*1.0/factor), int(high*1.0/factor)), filter)
        # self.saveImage()
        # self.drawImage(new)
        if self.cur_ncr < 0:
            # filter = Image.ANTIALIAS
            filter = cv2.INTER_CUBIC
        else:
            # filter = Image.BICUBIC
            filter = cv2.INTER_CUBIC

        ##### convert pil to openCV ######## 
        opencvImage = cv2.cvtColor(numpy.array(imgpil), cv2.COLOR_RGB2BGR) # optional
        ####################################
        # Because PIL library resize function is too slow, we use opencv instead.
        opencvImage = cv2.resize(opencvImage, (int(wide*1.0/factor), int(high*1.0/factor)), interpolation = filter)

        ##### convert openCV to pil ########
        opencvImage = cv2.cvtColor(opencvImage,cv2.COLOR_BGR2RGB)
        pil_im = Image.fromarray(opencvImage)
        ####################################

        # new = imgpil.resize((int(wide*1.0/factor), int(high*1.0/factor)), filter)

        self.saveImage()
        self.drawImage(pil_im)
        # self.drawImage(new)

    def zoomUp(self, factor):
        # zoom in or out in increments
        self.count_emphasize =0 
        count = int(round(math.log(factor, 1.1)))
        self.cur_ncr = self.cur_ncr+count 
        imgpil = self.saveimage
        wide, high = imgpil.size
        # if self.cur_ncr < 0:
        #   filter = Image.ANTIALIAS
        # else:
        #   filter = Image.BICUBIC
        # new = imgpil.resize((int(wide*factor),int(high* factor)), filter)
        # self.saveImage()
        # self.drawImage(new)
        if self.cur_ncr < 0:
            # filter = Image.ANTIALIAS
            filter = cv2.INTER_CUBIC
        else:
            # filter = Image.BICUBIC
            # INTER_NEAREST  INTER_AREA INTER_CUBIC INTER_LANCZOS4
            filter = cv2.INTER_CUBIC

        ##### convert pil to openCV ######## 
        opencvImage = cv2.cvtColor(numpy.array(imgpil), cv2.COLOR_RGB2BGR) # optional
        ####################################
        # Because PIL library resize function is too slow, we use opencv instead.
        opencvImage = cv2.resize(opencvImage, (int(wide*factor),int(high* factor)), interpolation = filter)

        ##### convert openCV to pil ########
        opencvImage = cv2.cvtColor(opencvImage,cv2.COLOR_BGR2RGB)
        pil_im = Image.fromarray(opencvImage)
        ####################################

        # new = imgpil.resize((int(wide*factor),int(high* factor)), filter)
        self.saveImage()
        self.drawImage(pil_im)
        # self.drawImage(new)

    def typeText(self, event=None):
        sel = self.listbox.curselection()
        if len(sel) is 1: # whether
            # print('debug', self.bboxList[int(sel[0])][0])
            self.typeTextWindow = ttk.Toplevel(root, width = 500, height = 120)
            self.typeTextWindow.title('Input text.')

            self.typeTextWindowLabel = Label(self.typeTextWindow, text = '输入: ', font = ('Helvetica', '18', 'bold'))
            self.typeCurrentTextWindowLabel = Label(self.typeTextWindow, text = '当前: ', font = ('Helvetica', '18', 'bold'))
            self.typeTextWindowLabel.grid(row = 1, column = 1)
            self.typeCurrentTextWindowLabel.grid(row = 2, column = 1)
            # self.typeCurrentTextWindowLabel.pack(side)
            # self.typeTextWindowlabel.pack(side = LEFT, padx= 5)
            # self.typeTextWindowLabel.pack(side = LEFT, padx =2, pady=5)
            content = StringVar()
            content.set(self.tempCnt)
            curContent = StringVar()
            if len(self.bboxList[int(sel[0])]) is 9:
                curContent.set(self.bboxList[int(sel[0])][8])
            self.typeTextWindowEntry = Entry(self.typeTextWindow, width = 28, font = ('Helvetica', '18', 'bold'), foreground = 'red', textvariable = content)
            # self.typeTextWindowEntry.pack(side = LEFT, padx =5, pady=5)
            self.typeTextWindowEntry.grid(row = 1, column = 2)
            self.typeCurrentTextWindowEntry = Entry(self.typeTextWindow, width = 28, font = ('Helvetica', '18', 'bold'), foreground = 'red', background = 'grey',  state ='readonly',\
                                 relief ='groove', textvariable = curContent)
            # self.typeCurrentTextWindowEntry.pack(side = LEFT, padx =5, pady=5)
            self.typeCurrentTextWindowEntry.grid(row = 2, column = 2)
            self.typeTextWindowEntry.focus_force() 
            self.typeTextWindowEntry.icursor(1)
            def sendTypeText(curSel):
                typeLabel = self.typeTextWindowEntry.get()
                self.bboxList[int(curSel)] = self.bboxList[int(curSel)]+(typeLabel, )
                # print('debug label:', int(curSel), str(typeLabel))
                self.listbox.delete(int(sel[0]))
                self.listbox.insert(int(sel[0]), '(%d, %d)-> %s' %(self.bboxList[int(sel[0])][0], self.bboxList[int(sel[0])][1], typeLabel))
                self.bboxList[int(sel[0])] = self.bboxList[int(sel[0])][:8]+(typeLabel,)
                self.listbox.itemconfig(int(sel[0]), fg = COLORS[(int(sel[0])) % len(COLORS)])
                self.typeTextWindow.destroy()

            self.typeTextWindow.bind('<Return>', lambda _: sendTypeText(int(sel[0])))
            self.typeTextWindow.bind('<Escape>', lambda _: self.typeTextWindow.destroy())
            # self.top_update.destroy() 
            centerToplevel(self.typeTextWindow)
            root.wait_window(self.typeTextWindow)

        self.saveImage()
        # self.nextImage()
        # self.prevImage()

    ### Attention Mode ##
    def adjust(self, event = None):
        sel = self.listbox.curselection()
        # initialize attention mode 
        self.STATE['attFirst'] = 0  
        self.STATE['attNext'] = 3
        self.p1_bboxIdtemp = None 
        self.p1_bboxIdtemp3 = None
        self.p2_bboxIdtemp = None
        self.p2_bboxIdtemp3 = None
        self.p3_bboxIdtemp = None
        self.p3_bboxIdtemp3 = None
        self.p4_bboxIdtemp = None
        self.p4_bboxIdtemp3 = None
        # self.end_bboxIdtemp = None
        # self.end_bboxIdtemp3 = None
        # self.end_bboxIdIndex = 0
        self.firstEnterAttention =  True
        self.attx = 0
        self.atty = 0
        if len(sel) is 1:
            if self.STATE['attention'] == 0:
                self.STATE['attention'] = 1-self.STATE['attention'] 
            else:
                self.STATE['attention'] = 1-self.STATE['attention'] 
                self.bboxIdList[int(self.listbox.curselection()[0])][self.end_bboxIdIndex%4] = self.end_bboxIdtemp
                self.bboxIdList[int(self.listbox.curselection()[0])][(self.end_bboxIdIndex+1)%4] = self.end_bboxIdtemp3
                # # print(int(self.mouseMoveEventx), int(self.mouseMoveEventy))
                self.attx = int((self.mouseMoveEventx))
                self.atty = int((self.mouseMoveEventy))
                print(self.end_bboxIdIndex)
                if self.end_bboxIdIndex%4 == 1:
                    self.bboxList[int(self.listbox.curselection()[0])] = tuple(self.bboxList[int(self.listbox.curselection()[0])][:6]+(self.attx, self.atty)+self.bboxList[int(self.listbox.curselection()[0])][8:])
                if self.end_bboxIdIndex%4 == 2:
                    self.bboxList[int(self.listbox.curselection()[0])] = tuple((self.attx, self.atty) + self.bboxList[int(self.listbox.curselection()[0])][2:])
                if self.end_bboxIdIndex%4 == 3:
                    self.bboxList[int(self.listbox.curselection()[0])] = tuple(self.bboxList[int(self.listbox.curselection()[0])][:2]+(self.attx, self.atty)+self.bboxList[int(self.listbox.curselection()[0])][4:])
                if self.end_bboxIdIndex%4 == 0:
                    self.bboxList[int(self.listbox.curselection()[0])] = tuple(self.bboxList[int(self.listbox.curselection()[0])][:4]+(self.attx, self.atty)+self.bboxList[int(self.listbox.curselection()[0])][6:])
                self.saveImage()
                tempSel = int(self.listbox.curselection()[0])
                self.listbox.delete(int(self.listbox.curselection()[0]))
                if len(self.bboxList[tempSel]) == 9:
                    self.listbox.insert(tempSel, '(%d, %d)-> %s' %(self.bboxList[tempSel][0],\
                                                             self.bboxList[tempSel][1], self.bboxList[tempSel][8]))
                else:
                    self.listbox.insert(tempSel, '(%d, %d)-> ' %(self.bboxList[tempSel][0],\
                                                             self.bboxList[tempSel][1]))
                self.listbox.itemconfig(tempSel, fg = COLORS[(tempSel) % len(COLORS)])

    def attentionTab(self, event = None):
        print("yes")
        if self.STATE['attention'] == 1:
            self.STATE['attFirst'] = (self.STATE['attFirst'] + 1)%4


if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.mainloop()
