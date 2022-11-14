# 统计学习理论导论大实验,古籍竖排汉字识别
# conda activate ngp-wyf
# pip install cnocr
# fc-list :lang=zh
# apt-get install libfreetype6-dev libharfbuzz-dev libfribidi-dev meson gtk-doc-tools
from PIL import Image,ImageDraw,ImageFont
from cnocr import CnOcr
import numpy as np
import cv2
import re
def DrawRect(img,in1,in2,color,size,type): # 图像绘制方框函数
    if type == '1pos': # in1->pos,in2->h
        draw = cv2.rectangle(img,(int(in1[0]-in2),int(in1[1]-in2)),(int(in1[0]+in2),int(in1[1]+in2)),color,size) # pos中心,h半边长
    elif type == '2pos': # in1->pos1,in2->pos2
        draw = cv2.rectangle(img,(int(in1[0]),int(in1[1])),(int(in2[0]),int(in2[1])),color,size) # pos1左上角,pos2右下角
    else:
        print('error in DrawRect type')
    return draw
def ImgAddText(img,text,pos,color,size): # 图像绘制中文函数
    if isinstance(img,np.ndarray): # 判断是否OpenCV图像格式
        img = Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB)) # OpenCV转PIL
    else:
        print('error in ImgAddText img')
        return
    text = re.sub(r"(.{1})","\\1\r\n",text) # 正则表达式每隔1个字符添加换行符
    draw = ImageDraw.Draw(img) # 创建一个可以在给定图像上绘制中文的对象
    if True: # Linux字体地址
        font_path = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'
    else: # Windows字体地址
        font_path = 'C:/Windows/Fonts/SIMLI.TTF'
    font = ImageFont.truetype(font_path,size,encoding='utf-8') # 设置字体格式
    draw.text(xy=(int(pos[0]),int(pos[1])),text=text,fill=color,font=font) # 绘制中文
    return cv2.cvtColor(np.asarray(img),cv2.COLOR_RGB2BGR) # PIL转OpenCV
pic_path = './DATA/'
# data_name = '401206800-J0001-3-000367-003-00011.jpg'
pic_name = '401206800-J0001-3-000448-001-00002.jpg'
ocr = CnOcr(rec_model_name='ch_PP-OCRv3') # 竖排汉字识别
out = ocr.ocr(pic_path+pic_name)
# print(out[0]['position'][0]) # 打印一个点的xy坐标
img = cv2.imread(pic_path+pic_name)
for i in range(len(out)): # 绘制单张图像的识别结果
    img = DrawRect(img=img,in1=out[i]['position'][0],in2=out[i]['position'][2],color=(255,0,0),size=4,type='2pos') # 绘制矩形框
    img = ImgAddText(img=img,text=out[i]['text'],pos=out[i]['position'][0],color=(255,0,0),size=25) # 绘制文本
cv2.imwrite('./OUTPUT/hanzi.jpg',img)
