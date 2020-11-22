#coding=utf-8
#
# 切分图片
# 做一个裁剪的小案例
import logging
import os
import time
import PIL.Image as pil_image
import yaml
logging.basicConfig(format='[%(levelname)s](%(name)s) %(asctime)s : %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

def getAllImages(path):
   return [os.path.join(path,f) for f in os.listdir(path) if f.endswith('.jpg')|f.endswith('.jpeg')|f.endswith('.png')]

def splitImage(dir_in, dir_out, direction, blocks):
    for path in getAllImages(dir_in):
        _, file = os.path.split(path)
        name, ext = os.path.splitext(file)
        im = pil_image.open(path)
        imgwidth, imgheight = im.size

        if direction == "水平":
            step = int(imgwidth / blocks)
            stop = imgwidth
        else:
            step = int(imgheight / blocks)
            stop = imgheight

        k = 0
        for j in range(0, stop, step):
            if direction == "水平":
                box = (imgwidth-(k+1)*step, 0, imgwidth-j, imgheight)
            else:
                box = (0, imgheight-(k+1)*step, 0, imgwidth, imgheight-j)

            logging.info("rect box {0}".format(box))

            newimg = dir_out + "\\" + name + "_{0:03d}".format(k) + ext
            logging.info("{0} => {1}".format(path, newimg))
            
            with open(newimg, 'wb') as img_file:
                
                if ext.lower() == ".jpg" or ext.lower() == ".jpeg":
                    im.crop(box).save(img_file, quality=95)
                else:
                    im.crop(box).save(img_file, optimize=True)
            k += 1

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    with open('config.yml', encoding='utf-8', mode='r') as conffile:
        conf = yaml.load(conffile, Loader=FullLoader)

        if not os.path.isdir(conf["imgdir_out"]):
            os.mkdir(conf["imgdir_out"])

        logging.info("Image folder {0}".format(conf["imgdir_in"]))
        splitImage(conf["imgdir_in"], conf["imgdir_out"], conf["split_direction"], conf["split_to"])
