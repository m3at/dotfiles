from __future__ import print_function
import re
import subprocess
import argparse
#import platform
import socket
import time
import numpy as np
from sklearn.cluster import KMeans
from sklearn.utils import shuffle
from scipy import misc
import os
import cv2

s_epilog = ""

parser = argparse.ArgumentParser(
        prog='get_gif',
        usage='%(prog)s [options] adress',
        epilog=s_epilog,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
parser.add_argument('adress', nargs=1, help='web adress of the gif to process')
parser.add_argument('-n', '--name', default="tmp_gif",
        help='specify a name to save the command')
parser.add_argument('--height', default=40,
        help='limit the gif height')
parser.add_argument('--width', default=100,
        help='limit the gif width')
parser.add_argument('--sleep', default=0.05,
        help='define the delay between each frame')
parser.add_argument('-v', '--version', action='version',
        version='%(prog)s version 0.1, build 56231')
args = parser.parse_args()



### 1


def _make_exist(name, max_rec=1):
    if max_rec > 100:
        print("Too much folders with the same name already exists!\nYou may have downloaded this gif multiple times")
        raise UserWarning
    if not os.path.exists("/Users/meat/Documents/tmp/%s_%d" % (name, max_rec)):
        os.makedirs("/Users/meat/Documents/tmp/%s_%d" % (name, max_rec))
        return "/Users/meat/Documents/tmp/%s_%d" % (name, max_rec)
    else:
        return _make_exist(name, max_rec + 1)


def _make_dir(name, max_rec=0):
    if not os.path.exists("/Users/meat/Documents/tmp/%s" % name):
        os.makedirs("/Users/meat/Documents/tmp/%s" % name)
        return "/Users/meat/Documents/tmp/%s" % name
    else:
        return _make_exist(name, max_rec + 1)

def img_to_ascii(img):
    txt = ""
    for j in img:
        for i in j:
            try:
                if i[3] < 0.01:
                    txt+="\033[48;2;5;5;5m "
                else:
                    txt+="\033[48;2;%d;%d;%dm "%(int(i[0]*255),
                                            int(i[1]*255),
                                            int(i[2]*255))
            except IndexError:
                txt+="\033[48;2;%d;%d;%dm "%(int(i[0]*255),
                                            int(i[1]*255),
                                            int(i[2]*255))
        txt+="\n"
    return txt

def pixelate(img, (pixel_width, pixel_height), codebook, labels):
    width, height, dim = img.shape
    d = codebook.shape[1]
    imgg = np.zeros((len(range(0, width, pixel_width)),
        len(range(0, height, pixel_height)),
        d))
    labels_matrix = np.reshape(labels,[img.shape[0],img.shape[1]])

    for idxw,w in enumerate(range(0, width, pixel_width)):

        minx, maxx = w, min(width, w + pixel_width)

        for idxh,h in enumerate(range(0, height, pixel_height)):

            miny, maxy = h, min(height, h + pixel_height)

            l = []
            for x in xrange(minx, maxx):
                for y in xrange(miny, maxy):
                    l.append(labels_matrix[x,y])
            color = max(set(l), key=l.count)
            imgg[idxw,idxh] = codebook[color]

    return imgg


### 2

gif_name = ".".join(args.adress[0].split('/')[-1].split('.')[:-1])
cmd_name = args.name
# gif_name = "tumblr_nw1869xqEx1so9b4uo1_500_7"
# cmd_name = args.name

new_path = _make_dir(gif_name)
# new_path = "/Users/meat/Documents/tmp/tumblr_nw1869xqEx1so9b4uo1_500_7"
res = subprocess.call(["wget", "-q", "-P", new_path, args.adress[0]])
res = subprocess.call(["convert", "-coalesce",
    "%s/%s.gif" % (new_path, gif_name), "%s/%s.png" % (new_path, gif_name)])
res = subprocess.call(["rm", "%s/%s.gif" % (new_path, gif_name)])

# path = "/Users/meat/Documents/tmp/test1337/"
num_files = len([f for f in os.listdir(new_path) if os.path.isfile(os.path.join(new_path, f))])


### 3


print(new_path)
print("nb files=",num_files)

### 4


image_all = []
for s in range(0,num_files):


    f = "%s/%s-%d.png"%(new_path,gif_name,s)
    try:
        ima = cv2.imread(f,-1)[:,:, [2,1,0,3]]
    except IndexError:
        ima = cv2.imread(f,-1)[:,:, [2,1,0]]
    img = np.array(ima, dtype=np.float64) / 255

    image_all.append(img)
image_all = np.array(image_all)
x, w, h, d = image_all.shape

image_array = np.reshape(image_all, (x * w * h, d))

res = subprocess.call("rm %s/*.png"%(new_path), shell=True)



### 5


n_colors = 24
image_array_sample = shuffle(image_array, random_state=0)[:2000]

kmeans = KMeans(n_clusters=n_colors, random_state=0).fit(image_array_sample)
labels = kmeans.predict(image_array)


### 6


hauteur = int(args.height)
largeur = int(args.width)
height = int(img.shape[1]/largeur) #largeur
width = int(img.shape[0]/hauteur) #hauteur

unfold = np.reshape(labels, (x, w*h))
outt= []
for s in range(0,num_files):

    out = pixelate(image_all[s],(width,height),kmeans.cluster_centers_, unfold[s])
    outt.append(out)
    with open("%s/%s-%d.anim"%(new_path,gif_name,s),"w+") as f:
        f.write(img_to_ascii(out))


### 7


with open("/Users/meat/.zshrc.gifs", "a+") as conf:
    conf.write("%sfunction %s() {\n\t(cd %s ; clear; echo '\033[s' ; for D in `ls *.anim | gsort -V`; do [ '${D}' ] && echo '\033[u' && cat ${D} && sleep %f; done)\n}\n"
               % ( "#Added by 'get_gif.py'\n",
                  cmd_name,
                  new_path,
                  float(args.sleep)
                 ))
    conf.close()
print("'%s' is ready." % cmd_name)

