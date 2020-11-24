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

#切割图片
def splitImage(dir_in, dir_out, direction, blocks):
    for path in getAllImages(dir_in):
        _, file = os.path.split(path)
        name, ext = os.path.splitext(file)
        im = pil_image.open(path)
        imgwidth, imgheight = im.size

        if direction == 'H':
            step = int(imgwidth / blocks)
            stop = imgwidth
        else:
            step = int(imgheight / blocks)
            stop = imgheight

        k = 0
        for j in range(0, stop, step):
            if direction == 'H':
                box = (imgwidth-(k+1)*step, 0, imgwidth-j, imgheight)
            else:
                box = (0, imgheight-(k+1)*step, 0, imgwidth, imgheight-j)

            # logging.info("rect box {0}".format(box))

            newimg = dir_out + "\\" + name + "_{0:03d}".format(k) + ext
            logging.info("{0} => {1}".format(path, newimg))
            
            with open(newimg, 'wb') as img_file:
                
                if ext.lower() == ".jpg" or ext.lower() == ".jpeg":
                    im.crop(box).save(img_file, quality=95)
                else:
                    im.crop(box).save(img_file, optimize=True)
            k += 1

#合并图片
def mergeImage(dir_in, dir_out, direction, from_cnt, by, prefix):
    pathlist = getAllImages(dir_in)
    # group per from_cnt
    groups = [pathlist[i:i + from_cnt] for i in range(0, len(pathlist), from_cnt)]
    k = 0

    for group in groups:
        imglist = []
        width = 0
        height = 0

        if by == 'reverse':
            group = group[::-1]

        for path in group:
            im = pil_image.open(path)
            iw, ih = im.size
            if direction == 'H':
                width += iw
                height = height if height > ih else ih
            else:
                width = width if width > iw else iw
                height += ih
            imglist.append(im) 

        target = pil_image.new('RGB', (width, height))

        coord1 = 0
        coord2 = 0

        for img in imglist:
            iw, ih = img.size

            if direction == 'H':
                if coord2 == 0:
                    coord2 = iw
                box = (coord1, 0, coord2, height)
                coord1 += iw
                coord2 += iw
            else:
                if coord2 == 0:
                    coord2 = ih
                box = (0, coord1, width, coord2)
                coord1 += ih
                coord2 += ih
            # logging.info("rect box {0}".format(box))
            target.paste(img, box)

        newimg = dir_out+'\\'+prefix+'{0:03d}'.format(k)+'.jpg'

        logging.info("=> {0}".format(newimg))
        
        target.save(newimg, quality=95)
        imglist = []
        k += 1

#裁剪图片
def cropImage(dir_in, dir_out, suffix, cut):
    left, upper, right, lower = cut
    for path in getAllImages(dir_in):
        _, file = os.path.split(path)
        name, ext = os.path.splitext(file)
        newimg = dir_out+"\\"+name+suffix+ext
        logging.info("{0} => {1}".format(path, newimg))
        with open(newimg, 'wb') as img_file:
            org_img = pil_image.open(path)
            width, height = org_img.size
            if ext.lower() == ".jpg" or ext.lower() == ".jpeg":
                org_img.crop(
                    (left, upper, width - right, height - lower)).save(img_file, quality=95)
            else:
                org_img.crop(
                    (left, upper, width - right, height - lower)).save(img_file, optimize=True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    with open('config.yml', encoding='utf-8', mode='r') as conffile:
        conf = yaml.load(conffile, Loader=yaml.FullLoader)

        if 'imgdir_out' not in conf.keys():
            conf['imgdir_out'] = conf['imgdir_in']

        if not os.path.isdir(conf["imgdir_out"]):
            os.mkdir(conf["imgdir_out"])

        method = conf["method"]
        logging.info("Method {1} | Image folder {0}".format(conf["imgdir_in"], method))

        if method == 'split':
            splitImage(conf['imgdir_in'], conf['imgdir_out'], conf['split']["direction"], conf['split']['to'])
        elif method == 'crop':
            cropImage(conf['imgdir_in'], conf['imgdir_out'], conf['crop']['suffix'], conf['crop']['cut'])
        elif method == 'merge':
            mergeImage(conf['imgdir_in'], conf['imgdir_out'], conf['merge']['direction'], conf['merge']['from'], conf['merge']['by'], conf['merge']['prefix'])
        else:
            pass
