import logging
import os
import random
import shutil
def getRandomImgName():
        # 获取文件夹内所有的文件
        all_files = os.listdir("/www/server/nginx/html/image")

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
