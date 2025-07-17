#!python
import os,sys
from xml.etree import ElementTree
from PIL import Image
import numpy as np
import cv2
from pathlib import Path
import json

def endWith(s,*endstring):
    array = map(s.endswith,endstring)
    if True in array:
        return True
    else:
        return False

def get_recursive_file_list(path):
    current_files = os.listdir(path)
    all_files=[]
    for file_name in current_files:
        full_file_name=os.path.join(path,file_name)
        if endWith(full_file_name,'.plist'):
            full_file_name=full_file_name.replace('.plist','')
            all_files.append(full_file_name)
        if os.path.isdir(full_file_name):
            next_level_files = get_recursive_file_list(full_file_name)
            all_files.extend(next_level_files)
    return all_files

def tree_to_dict(tree):
    d={}
    for index,item in enumerate(tree):
        if item.tag =='key':
            if tree[index+1].tag == 'string':
                d[item.text] = tree[index+1].text
            elif tree[index+1].tag == 'true':
                d[item.text]=True
            elif tree[index+1].tag == 'false':
                d[item.text]=False
            elif  tree[index+1].tag == "integer":
                d[item.text]=tree[index+1].text
            elif  tree[index+1].tag == "array":
                d[item.text]=tree[index+1].text
            elif tree[index+1].tag == 'dict':
                d[item.text] = tree_to_dict(tree[index+1])
    return d
def gen_png(plist_filename,png_filename):
    format = None
    root = ElementTree.fromstring(open(plist_filename,'r', encoding='utf-8').read())
    plist_dict = tree_to_dict(root[0])
    if "metadata" in plist_dict and "format" in plist_dict["metadata"]:
        format = int(plist_dict["metadata"]["format"])
    if format == 0:
        gen_plist_format_2(plist_dict,png_filename)
    elif format == 1 or format == 2:
        gen_plist_format_1(plist_dict,png_filename)
    elif format == 3:
        gen_plist_format_3(plist_dict,png_filename)

def gen_plist_format_1(plist_dict,png_filename):
    baseName = os.path.basename(png_filename)
    baseName = baseName[0:baseName.index('.')]
    file_path = os.path.join(os.path.dirname(png_filename),baseName)

    print("----------- start generating", baseName)

    big_image = Image.open(png_filename)
    to_list = lambda x:x.replace('{','').replace('}','').split(',')
    for k,v in plist_dict['frames'].items():
        rectlist = to_list(v['frame'])
        width = int(rectlist[3] if v['rotated'] else rectlist[2])
        height = int(rectlist[2] if v['rotated'] else rectlist[3])
        box = (
            int(rectlist[0]),
            int(rectlist[1]),
            int(rectlist[0])+width,
            int(rectlist[1])+height,
        )
        sizelist = [int(x)for x in to_list(v['sourceSize'])]
        rect_on_big = big_image.crop(box)
        if v['rotated']:
            rect_on_big = rect_on_big.transpose(Image.ROTATE_90)
        result_image = Image.new('RGBA',sizelist,(0,0,0,0))
        offset = [int(x)for x in to_list(v['offset'])]
        if v['rotated']:
            result_box=(
                (sizelist[0] - height) / 2 + offset[0],
                (sizelist[1] - width) / 2 + offset[1],
            )
        else:
            result_box=(
                (sizelist[0] - width)/2 + offset[0],
                (sizelist[1] - height)/2 + offset[1]
            )
        result_image.paste(rect_on_big,result_box)
        outfile = (file_path+'/'+k)
        outpath = os.path.dirname(outfile)
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        #outfile=outfile+'.png'
        print(k,"generated")
        result_image.save(outfile)

    print("-----------")

def gen_plist_format_2(plist_dict,png_filename):
    baseName = os.path.basename(png_filename)
    baseName = baseName[0:baseName.index('.')]
    file_path = os.path.join(os.path.dirname(png_filename),baseName)
    big_image = Image.open(png_filename)

    print("----------- start generating", baseName)

    to_list = lambda x:x.replace('{','').replace('}','').split(',')
    for k,v in plist_dict['frames'].items():

        x = int(v['x'])
        y = int(v['y'])
        width = int(v['width'])
        height = int(v['height'])
        box = (
            int(x),
            int(y),
            int(x + width),
            int(y + height)
        )
        rect_on_big = big_image.crop(box)
        # rect_on_big.show()
        result_box=(
                width,
                height
            )
        result_image = Image.new('RGBA',result_box,(0,0,0,0))
        outfile = (file_path+'/'+k)
        outpath = os.path.dirname(outfile)
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        #outfile=outfile+'.png'
        print(k,"generated")
        rect_on_big.save(outfile)

    print("-----------")

def gen_plist_format_3(plist_dict,png_filename):
    baseName = os.path.basename(png_filename)
    baseName = baseName[0:baseName.index('.')]
    file_path = os.path.join(os.path.dirname(png_filename),baseName)
    big_image = Image.open(png_filename)

    print("----------- start generating", baseName)

    to_list = lambda x:x.replace('{','').replace('}','').split(',')

    # 读取图像
    img = cv2.imread(png_filename, cv2.IMREAD_UNCHANGED)

    isPolygon = False

    for k,v in plist_dict['frames'].items():
        if v.get('triangles'):
            isPolygon = True
            break

    # 如果是polygon算法
    if isPolygon:
        print("parse polygon")
        for k,v in plist_dict['frames'].items():
            rectlist = to_list(v['textureRect'])

            outfile = (file_path+'/'+k)
            outpath = os.path.dirname(outfile)
            if not os.path.exists(outpath):
                os.makedirs(outpath)

            vertices = v['vertices'].split(" ")
            x = []
            y = []
            for i in range(0, len(vertices), 2):
                x.append(int(vertices[i]))
                y.append(int(vertices[i+1]))

            triangles = v['triangles'].split(" ")
            vertices_x = []
            vertices_y = []
            for i in range(0, len(triangles), 1):
                vertices_x.append(x[int(triangles[i])])
                vertices_y.append(y[int(triangles[i])])
            cropImg(img, outfile, vertices_x, vertices_y, int(rectlist[0]), int(rectlist[1]), int(rectlist[2]), int(rectlist[3]))
            print(k, "generated")
    else: 
        for k,v in plist_dict['frames'].items():
            rectlist = to_list(v['textureRect'])

            width = int(rectlist[3] if v['textureRotated'] else rectlist[2])
            height = int(rectlist[2] if v['textureRotated'] else rectlist[3])
            box = (
                int(rectlist[0]),
                int(rectlist[1]),
                int(rectlist[0]) + width,
                int(rectlist[1]) + height,
            )
            sizelist = [int(x)for x in to_list(v['spriteSize'])]
            rect_on_big = big_image.crop(box)
            if v['textureRotated']:
                rect_on_big = rect_on_big.transpose(Image.ROTATE_90)
            result_image = Image.new('RGBA',sizelist,(0,0,0,0))
            offset = [float(x)for x in to_list(v['spriteOffset'])]
            orsize = [int(x)for x in to_list(v['spriteSourceSize'])]
            width = orsize[0]
            height = orsize[1]
            result_box=(
                int(offset[0]),
                int(offset[1])
            )

            result_image.paste(rect_on_big,result_box)
            outfile = (file_path+'/'+k)
            outpath = os.path.dirname(outfile)
            if not os.path.exists(outpath):
                os.makedirs(outpath)
            #outfile=outfile+'.png'
            print(k,"generated")
            result_image.save(outfile)

    print("-----------")

def cropImg(img, outfile, vertices_x, vertices_y, x, y, w, h):
	# 坐标点points

	pts = []
	for i in range(0, len(vertices_x), 3):
		temp = np.array([[x + vertices_x[i], y + vertices_y[i]], [x + vertices_x[i+1], y + vertices_y[i+1]], [x + vertices_x[i+2], y + vertices_y[i+2]]])
		pts.append(temp)

	pts = np.array(pts)

	# 和原始图像一样大小的0矩阵，作为mask

	mask = np.zeros(img.shape[:2], np.uint8)

	# 在mask上将多边形区域填充为白色

	cv2.polylines(mask, pts, 1, 255) # 描绘边缘

	cv2.fillPoly(mask, pts, 255) # 填充

	# 逐位与，得到裁剪后图像，此时是黑色背景

	dst = cv2.bitwise_and(img, img, mask=mask)

	crop = dst[y:y+h, x:x+w]
    # 这个接口保存的路径不能有中文字符，否则会写入失败
	# cv2.imwrite(outfile, crop)
	cv2.imencode(Path(outfile).suffix, crop)[1].tofile(outfile)

def get_recursive_file_list(path):
    current_files = os.listdir(path)
    all_files=[]
    for file_name in current_files:
        full_file_name=os.path.join(path,file_name)
        if endWith(full_file_name,'.plist') or endWith(full_file_name, '.json'):
            full_file_name=full_file_name.rsplit('.', 1)[0]
            all_files.append(full_file_name)
        if os.path.isdir(full_file_name):
            next_level_files = get_recursive_file_list(full_file_name)
            all_files.extend(next_level_files)
    return all_files

def gen_json(json_filename, png_filename):
    baseName = os.path.basename(png_filename)
    baseName = baseName[0:baseName.index('.')]
    file_path = os.path.join(os.path.dirname(png_filename), baseName)

    print("----------- start generating", baseName)

    with open(json_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    big_image = Image.open(png_filename)
    
    frames = data.get('frames') or {}

    for k, v in frames.items():
        frame = v
        x = frame['x']
        y = frame['y']
        w = frame['w']
        h = frame['h']

        box = (x, y, x + w, y + h)
        rect_on_big = big_image.crop(box)

        rotated = v.get('rotated', False)
        if rotated:
            rect_on_big = rect_on_big.transpose(Image.ROTATE_90)

        sourceSize = v.get('sourceSize', {'w': w, 'h': h})
        offset = v.get('spriteSourceSize', {'x': 0, 'y': 0})

        result_image = Image.new('RGBA', (sourceSize['w'], sourceSize['h']), (0, 0, 0, 0))
        result_box = (
            offset['x'],
            offset['y']
        )
        result_image.paste(rect_on_big, result_box)

        k = k[0:k.rfind('_png')] + '.png'

        outfile = os.path.join(file_path, k)
        outpath = os.path.dirname(outfile)
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        print(k, "generated")
        result_image.save(outfile)

    print("-----------")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("USAGE: python plistUnpacker.py [Directory/xxx.plist|xxx.json]")
    else:
        pathOrFilename = sys.argv[1]
        if os.path.isdir(pathOrFilename):
            allFiles = get_recursive_file_list(pathOrFilename)
            for base in allFiles:
                plist_file = base + '.plist'
                json_file = base + '.json'
                png_file = base + '.png'

                if os.path.exists(plist_file) and os.path.exists(png_file):
                    gen_png(plist_file, png_file)
                elif os.path.exists(json_file) and os.path.exists(png_file):
                    gen_json(json_file, png_file)
                else:
                    print(f"Missing .png or descriptor for {base}")
        else:
            if endWith(pathOrFilename, '.plist'):
                base = pathOrFilename[0:pathOrFilename.find('.plist')]
                gen_png(base + '.plist', base + '.png')
            elif endWith(pathOrFilename, '.json'):
                base = pathOrFilename[0:pathOrFilename.find('.json')]
                gen_json(base + '.json', base + '.png')
            else:
                print("USAGE: python plistUnpacker.py [Directory/***.plist|***.json]")

