import logging
import os
import random
from urllib.parse import urlparse

import requests
from PIL import Image
from io import BytesIO
import shutil

path = "D:\\tp\\"

view_url = "http://8.138.16.124:8083/upload/"
def getRandomImgName():
        # 获取文件夹内所有的文件
        all_files = os.listdir("/www/server/nginx/html/image")
        # all_files = os.listdir("C://Users//Administrator//PycharmProjects//crawl//downloaded_images")
        # 筛选出所有的图片文件（可以根据需要增加其他图片格式）
        image_files = [f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

        # 如果没有图片文件
        if not image_files:
            print("文件夹中没有图片")
            return ""

        # 随机选择一个图片文件
        random_image = random.choice(image_files)
        logging.info(f"获取到的图片名: {random_image}")
        return random_image


def zipImg(png_image_path ,jpg_image_path):
    # 打开图片并转换为 RGB（因为 JPG 不支持透明通道）
    image = Image.open(png_image_path).convert('RGB')
    # 保存为 JPG 格式
    image.save(jpg_image_path, 'JPEG')

def download_image_to_jpg(url):
    response = requests.get(url)
    if response.status_code == 200:
        # 打开图片并转换为 RGB（因为 JPG 不支持透明通道）
        image = Image.open(BytesIO(response.content)).convert('RGB')
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        # 保存为 JPG 格式
        image.save(path+filename, 'JPEG')
    else:
        logging.info("图片下载失败",url)
    ## 返回图片访问路径
    return view_url+filename;
