# 统计学习理论导论大实验,古籍竖排汉字识别
# conda activate ngp-wyf
# pip install cnocr
# pip install cnocr -i https://pypi.doubanio.com/simple
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
def imgAddText(img,text,pos,color,size): # 图像绘制竖排中文函数
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
def percentBar(num): # 显示当前百分比进度条函数
    percent = int(100*i/num) # 显示当前百分比进度条
    print('\r'+'▇'*(percent//2)+str(percent)+'%',end='')
if False: # 识别单张图像
    data_path = './DATA/'
    pic_path = 'phase1_text_img/'
    pic_name = [] # 图像文件名列表
    pic_name.append(data_path+pic_path+'401206800-J0001-3-000448-001-00002.jpg')
    ocr = CnOcr(rec_model_name='ch_PP-OCRv3') # 竖排汉字识别
    out = ocr.ocr(pic_name[0])
    drawImg(out=out,pic_name=pic_name[0]) # 绘制单张图像的识别结果
else: # 识别全部图像
    data_path = './OUTPUT/'
    json_path = './DATA/'
    pic_path = 'phase1_test_img/'
    json_name = 'result.json'
    pic_name = [] # 图像文件名列表
    all_dict = [] # 全部图像识别结果的字典列表
    # for home,dirs,files in os.walk(data_path+pic_path): # 遍历全部图像文件
    #     for filename in files:
    #         pic_name.append(os.path.join(home,filename)) # 保存全部图像文件路径
    pic_name = os.listdir(data_path+pic_path) # 保存全部图像文件名
    for i in range(len(pic_name)):
        percentBar(len(pic_name)) # 显示当前百分比进度条
        one_dict = {'id':pic_name[i],'text':''} # 单张图像识别结果的字典
        ocr = CnOcr(rec_model_name='ch_PP-OCRv3') # 竖排汉字识别
        out = ocr.ocr(data_path+pic_path+pic_name[i])
        right_pos = [] # 识别框从右到左排序列表
        for i in range(len(out)):
            right_pos.append(out[i]['position'][0][0]) # OpenCV坐标原点在左上角
        # sorted_id = sorted(range(len(right_pos)),key=lambda k: right_pos[k],reverse=True) # 因此从右到左是x从大到小顺序
        # sorted_id = np.argsort(right_pos).tolist() # numpy排序后转list
        sorted_pos = np.sort(right_pos).tolist() # numpy排序后转list
        sorted_pos.reverse() # sort从小到大需要反向
        for i in range(len(out)):
            one_dict['text'] += fan2jian(fan=out[right_pos.index(sorted_pos[i])]['text']) # 繁体转简体从右到左添加字典
        all_dict.append(one_dict)
    with open(json_path+json_name,'w') as result_json: # 字典列表写入json文件
        json.dump(all_dict,result_json,indent=4,ensure_ascii=False)

