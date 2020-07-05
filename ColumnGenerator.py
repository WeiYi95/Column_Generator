# -*- coding:utf-8 -*-
# @Author: Wei Yi

import cv2
import numpy as np
import re
import math
import random
import os


class ColumnGenerator:
    def __init__(self, load=False):
        self.height = 1000  # 图片高度
        self.width = 60  # 图片宽度
        self.channel = 3  # 图片通道数
        self.big = 36  # 单行字的大小
        self.small = 18  # 双行字的大小
        self.top_margin = 20  # 上边距
        self.bottom_margin = 20  # 下边距，未用到
        self.left_margin = 10  # 左边距
        self.right_margin = 10  # 右边距，未用到
        self.gap = 5  # 字间距（包括双行字间的间距）
        self.info = {}  # 记录信息
        """
        key：图片名
        value： 图片中的字位置信息（left，top，right，bottom，类别）单行：0，双行：1
                字体类型
                图片内容
       """
        if load:
            pkl_file = open('Info.pkl', 'rb')
            self.info = pickle.load(pkl_file)
        self.path = "Text/"
        self.img_path = "Img/"
        self.character_path = "./Character/"
        self.tot = len(self.info)

    def generate(self):
        files = os.listdir(self.path)
        for f in files:
            if f.find(".txt") != -1:
                path = self.path + f
                self.colunmuGenerator(path)

    def colunmuGenerator(self, file):
        with open(file, 'r', encoding="utf-8") as file:
            content = file.read()
            content = content.split('\n')[0]
            content = content.split('-')
        for col in content:
            if col.find('{') == -1:
                self.generateImg(col)

    def generateImg(self, col):
        blank_img = np.zeros((self.height, self.width, self.channel), np.uint8)
        blank_img += 255
        left_mar, size_mar, top_mar, add_noise, ch_noise = self.overall_noise()
        st_xmin = self.left_margin + left_mar
        st_ymin = self.top_margin + top_mar
        is_small = False
        pos_info = []
        start_right = False
        small_cnt = 0
        style = None
        for c in col:
            if c == '/':
                start_right = True
                continue
            if c == '[':
                is_small = True
                small_cnt = 0
                continue
            if c == ']':
                is_small = False
                start_right = False
                continue
            if style == None:
                style = self.getStyle(c)
            img, size = self.getChImg(c, ch_noise, is_small, size_mar, style)
            if is_small:
                if start_right:
                    temp = pos_info[-small_cnt]
                    blank_img[temp[1]:temp[3], st_xmin:st_xmin + size] *= img
                    small_cnt -= 1
                    continue
                else:
                    small_cnt += 1
                    blank_img[st_ymin:st_ymin + size, st_xmin + size + self.gap:st_xmin + size + self.gap + size] *= img
                    pos = (st_xmin, st_ymin, st_xmin + self.gap + (size * 2), st_ymin + size, int(is_small))
            else:
                blank_img[st_ymin:st_ymin + size, st_xmin:st_xmin + size] *= img
                pos = (st_xmin, st_ymin, st_xmin + size, st_ymin + size, int(is_small))
            gap = random.randint(-2, 2)
            gap = self.gap + gap
            st_ymin = st_ymin + size + gap
            pos_info.append(pos)
        name = str(self.tot) + '.jpg'
        if add_noise:
            st = random.randint(0, 400)
            per = random.randint(3, 7)
            blank_img = self.addGaussianNoise(blank_img, per / 10, 0)
        # cv2.imshow('img-p1', blank_img)
        # cv2.waitKey(0)
        self.info[name] = [pos_info, style, col]
        save_path = self.img_path + name
        cv2.imencode('.jpg', blank_img)[1].tofile(save_path)
        self.tot += 1

    def getStyle(self, ch):
        path = self.character_path + ch + "/"
        files = os.listdir(path)
        pos = random.randint(0, len(files) - 1)
        style = files[pos].split('_')[0]
        return style

    def overall_noise(self):
        left_mar = random.randint(-2, +2)
        size_mar = random.randint(-3, +3)
        top_mar = random.randint(-10, 10)
        add_noise = False
        if random.randint(0, 20) == 0:
            add_noise = True
        ch_noise = False
        if random.randint(0, 20) == 0:
            ch_noise = True
        return left_mar, size_mar, top_mar, add_noise, ch_noise

    def addGaussianNoise(self, image, percentage, color=255, region=None):
        G_Noiseimg = image
        if region == None:
            s = image.shape
        else:
            s = region
        G_NoiseNum = int(percentage * image.shape[0] * image.shape[1])
        for i in range(G_NoiseNum):
            temp_x = np.random.randint(0, s[0])
            temp_y = np.random.randint(0, s[1])
            G_Noiseimg[temp_x][temp_y] = color
        return G_Noiseimg

    def getChImg(self, ch, ch_noise, is_small, size_mar, style):
        path = self.character_path + ch + "/"
        files = os.listdir(path)
        name = ""
        for f in files:
            if f.find != -1:
                name = f
        if name == "":
            pos = random.randint(0, len(files) - 1)
            name = files[pos]
        path = path + "//" + name
        ch = cv2.imdecode(np.fromfile(path, dtype=np.uint8), -1)
        size = self.big
        if is_small:
            size = self.small
        size += size_mar
        ch = cv2.resize(ch, (size, size), interpolation=cv2.INTER_NEAREST)
        if ch_noise:
            per = random.randint(5, 7)
            ch = self.addGaussianNoise(ch, per / 10)
        ch = ch // 255
        return ch, size

    def save(self):
        output = open('Info.pkl', 'wb')
        pickle.dump(self.info, output)


cg = ColumnGenerator()
cg.generate()
