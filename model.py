# 统计学习理论导论大实验,古籍竖排汉字识别
# conda activate ngp-wyf
# pip install cnocr
# fc-list :lang=zh
# apt-get install libfreetype6-dev libharfbuzz-dev libfribidi-dev meson gtk-doc-tools
# pip install zhconv
from PIL import Image,ImageDraw,ImageFont
from cnocr import CnOcr
import numpy as np
import zhconv
import json
import cv2
import re
import os
def imgDrawRect(img,in1,in2,color,size,type): # 图像绘制方框函数
    if type == '1pos': # in1->pos,in2->h
        draw = cv2.rectangle(img,(int(in1[0]-in2),int(in1[1]-in2)),(int(in1[0]+in2),int(in1[1]+in2)),color,size) # pos中心,h半边长
    elif type == '2pos': # in1->pos1,in2->pos2
        draw = cv2.rectangle(img,(int(in1[0]),int(in1[1])),(int(in2[0]),int(in2[1])),color,size) # pos1左上角,pos2右下角
    else:
        print('error in DrawRect type')
    return draw
def imgAddText(img,text,pos,color,size): # 图像绘制中文函数
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
    draw.text(xy=(int(pos[0]),int(pos[1])),text=text,fill=color,font=font) # 绘制竖排中文
    return cv2.cvtColor(np.asarray(img),cv2.COLOR_RGB2BGR) # PIL转OpenCV
def drawImg(out,pic_name): # 绘制单张图像的识别结果
    # print(out[0]['position'][0]) # 打印一个点的xy坐标
    img = cv2.imread(pic_name)
    for i in range(len(out)):
        img = imgDrawRect(img=img,in1=out[i]['position'][0],in2=out[i]['position'][2],color=(255,0,0),size=4,type='2pos') # 绘制矩形框
        img = imgAddText(img=img,text=out[i]['text'],pos=out[i]['position'][0],color=(255,0,0),size=25) # 绘制文本
    cv2.imwrite('hanzi.jpg',img)
    return img
def fan2jian(fan): # 繁体转简体函数
    jian = zhconv.convert(fan,'zh-cn')
    return jian
data_path = './DATA/'
pic_path = 'phase1_text_img'
json_name = 'result.json'
pic_name = [] # 图像文件名列表
all_dict = [] # 识别结果字典列表
for home,dirs,files in os.walk(data_path+pic_path): # 遍历全部图像文件
    for filename in files:
        pic_name.append(os.path.join(home,filename)) # 保存全部图像文件名
for i in range(len(pic_name)):
    print(f'读取中---第{i}个图像',pic_name[i])
    one_dict = {'id':pic_name[i],'text':''}
    ocr = CnOcr(rec_model_name='ch_PP-OCRv3') # 竖排汉字识别
    out = ocr.ocr(pic_name[i])
    for i in range(len(out)):
        one_dict['text'] += fan2jian(fan=out[i]['text']) # 繁体转简体添加字典
    print(f'结果为---',one_dict)
    if False: # 绘制单张图像的识别结果
        drawImg(out=out,pic_name=pic_name[i])
    all_dict.append(one_dict)
with open(data_path+json_name,'w') as result_json:
    json.dump(all_dict,result_json,indent=4,ensure_ascii=False)

