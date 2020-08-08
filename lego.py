# -*-coding:utf-8 -*-
#
# Created by Renjie on 2020/05/20.
# Copyright © 2020 Renjie. All rights reserved.
#
from PIL import ImageDraw, ImageFont
import PIL.Image as PImg
import numpy as np
import os
from tkinter import *
import tkinter.filedialog
from tkinter.messagebox import showinfo,askokcancel

img_path = ''
block_size = 10

cwd = '/Users/renjie/Documents/LEGO/Images'
text = ['','Designed by Renjie.','Copyright © 2020 Renjie. All rights reserved.']

def set():
    global img_path,block_size,text
    img_path, block_size = '',10
    text = ['','Designed by Renjie.','Copyright © 2020 Renjie. All rights reserved.']

def changeImg2Np(img,h,w):
    data = img.getdata()
    #print("data is :{}".format(data))
    data = np.asarray(data, dtype='float') / 255.0
    #print("data2 is :{}".format(data))
    new_data = np.reshape(data, (h, w, 3))
    #print(new_data.shape)
    return new_data

def load_img(img_path,block):
    """
    读取图片
    :param img_path:输入图片路径
    :param block:一个模块像素大小
    :return:new_data = np数组格式的图片数据\
            size = 图片的尺寸\
            num = 每一行/列的模块个数
    """
    img = PImg.open(img_path)
    img = img.convert('RGB')
    #print('IMG size is', img.size)
    w,h = img.size
    if 1080 > w:
        h = int((1080/w)*h)
        w = 1080
    num_h,num_w = int(h//block),int(w//block)
    size_h,size_w = num_h*block,num_w*block
    img = img.resize((size_w,size_h),PImg.ANTIALIAS)
    #print('IMG size is',img.size)
    new_data = changeImg2Np(img,size_w,size_h)

    text.insert(0,'Image Size is {}x{}.'.format(size_h,size_w))
    text.insert(1,'Block Number of each row(col) is {}({}).'.format(num_w,num_h))
    text.insert(2,'You need {} lego.'.format(num_h*num_w))

    return new_data,size_h,size_w,num_h,num_w

def divide_RGB(img,size_h,size_w):
    """
    分离图片RGB三层
    :param img:np格式图片数组
    :param size:图片的尺寸
    :return:图片RGB单通道层
    """
    img_R, img_G, img_B = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    img_R = np.reshape(img_R, (size_h,size_w, 1))
    img_G = np.reshape(img_G, (size_h,size_w, 1))
    img_B = np.reshape(img_B, (size_h,size_w, 1))

    return img_R,img_G,img_B

def save_color(colors,img_path):
    """
    存储图片中不同色块的个数以及对应位置
    :param colors: 包含色块及对应位置的dict
    :param img_path:原始图片路径
    :return:
    """
    color_path = os.path.join(cwd,img_path.split('/')[-1].split('.')[0]+'.txt')
    color = ['COLOR TABLE']
    color_cnt = []
    for i in colors:
        color.append(str(i)+' x{}'.format(len(colors[i])))
        color_cnt.append(str(i)+' x{}'.format(len(colors[i])))
        color.append(','.join(colors[i]))
    color = '\n'.join(color)
    with open(color_path,'w') as wf:
        wf.write(color)

    return color_cnt

def add_text(size):
    """
    添加文本
    :param size:图片尺寸
    :return:
    """
    global text
    describe = PImg.new('RGB', (size, 224))
    draw = ImageDraw.Draw(describe)
    font = ImageFont.truetype("Arial.ttf", 20)
    text = '\n'.join(text)
    draw.text((40, 40), text, fill=(255, 255, 255), font=font)
    describe = changeImg2Np(describe, 224, size)

    return describe

def divide_block(img_path,block):
    global text
    img,size_h,size_w,num_h,num_w = load_img(img_path,block)
    #print(img.shape)

    img_R, img_G, img_B = divide_RGB(img,size_h,size_w)
    imgs = [img_R, img_G, img_B]

    colors = {}
    for tmp_img in imgs:
        for r in range(num_h):
            for c in range(num_w):
                block_max = np.average(tmp_img[r*block:(r+1)*block,c*block:(c+1)*block])
                tmp_img[r * block:(r + 1) * block, c * block:(c + 1) * block] = block_max
                tmp_img[r*block,c*block:(c + 1) * block] = 0.7
                tmp_img[r * block:(r + 1) * block, c * block] = 0.7
    img_RGB = np.concatenate((img_R, img_G, img_B), axis=2)

    for r in range(num_h):
        for c in range(num_w):
            tmp_color = tuple((img_RGB[r*block+1,c*block+1]*255).astype(np.uint8))
            if tmp_color not in colors:
                colors[tmp_color] = []
            colors[tmp_color].append(str((r,c)))

    color_cnt = save_color(colors,img_path)

    describe = add_text(size_w)

    img_des = np.concatenate((img_RGB,describe), axis=0)
    img_des = img_des * 255
    img_des = PImg.fromarray(img_des.astype(np.uint8)).convert('RGB')
    img_des.show()
    return img_des

def choose_file():
    global img_path
    img_path = tkinter.filedialog.askopenfilename(title='Choose Image...')
    if img_path == '':
        showinfo(title='Warning',message='No image has been found.')
        #window()

#def window():
    #global img_path,block_size
window = Tk()
window.geometry('300x200')
window.title('Change Images to LEGO')

v1 = StringVar()
Label(window,text='Block Size:').pack()
Entry(window,textvariable=v1).pack()

def get_user_input():
    global block_size
    block_size = v1.get()

def on_closing():
    if askokcancel("Quit", "Do you want to quit?"):
        window.destroy()

def change():
    global img_path,block_size
    get_user_input()
    if block_size == '':
        block_size = 10
    else:
        block_size = int(block_size)
    if img_path != '':
        print('Change:\nimg_path is {}\nblock size is {}'.format(img_path,block_size))
        output_path = os.path.join(cwd, img_path.split('/')[-1])
        img = divide_block(str(img_path), block_size)
        img.save(output_path)
        set()
    else:
        showinfo(title='Warning', message='No image has been found.')

Button(window,text='Choose Image...',command=choose_file).pack()
Button(window,text='CONVERT',command=change).pack()
#Button(window,text='Quit',command=window.quit).pack()
window.protocol('WM_DELETE_WINDOW', lambda: sys.exit(0))
window.mainloop()


"""
def main():
    img_path = '/Users/renjie/Pictures/pap.er/Wallpaper1.PNG'

    output_path = os.path.join(cwd,img_path.split('/')[-1])
    block=20
    img = divide_block(img_path,block)
    img.save(output_path)
"""

#if __name__ == '__main__':
    #main()
    #window()