
# coding:utf-8
from lxml.etree import Element, SubElement, tostring
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import glob
import os
from PIL import Image
from tqdm import tqdm
import argparse
from test import test



classes = ["core","coreless"]


parser = argparse.ArgumentParser(
    description='Single Shot MultiBox Detector Evaluation')
parser.add_argument('--testsetfile',
                    default='data/1.txt', type=str,
                    #default="/media/trs2/Xray20190723/train_test_txt/battery_sub/battery_sub_test.txt", type=str,
                    help='imageset file path to open')
parser.add_argument('--imgsetfile',
                    default='data/images/', type=str,
                    #default="/media/trs2/Xray20190723/cut_Image_core_coreless_battery_sub_2000_500/", type=str,
                    help='imageset file path to open')

parser.add_argument('--annsetfile',
                    default='data/labeltxt/', type=str,
                    #default="/media/trs2/Xray20190723/Anno_core_coreless_battery_sub_2000_500/", type=str,
                    help='imageset file path to open')



opt = parser.parse_args()



filename = "data/rbc.data"
'''with open(filename,'w') as file_object:
	file_object.write("classes=2\n")
	file_object.write("train=data/train.txt\n")
	file_object.write("valid="+opt.testsetfile+'\n')
	file_object.write("names=data/rbc.names\n")'''
def txtfile():
    Imgname_file = opt.testsetfile		
    file = open(Imgname_file,'r',encoding = 'utf-8')
    lines = file.readlines()
    file.close()
    file = open('data/test.txt','w+',encoding = 'utf-8')
    for line_list in lines:
        line_new = opt.imgsetfile  + line_list[:-1] +'.jpg\n'
        file.write(line_new)
    file.close()




def txtToXml(image_path, txt_path):
    for txt_file in tqdm(glob.glob(txt_path + '/*.txt')):
        print(txt_file)
        txt_name_ = txt_file.split('\\')[-1][:-4]

        print(txt_name_)
    
        data = {"shapes": []}
        print()
        im = Image.open(image_path + '\\' + txt_name_ + '.jpg')
        #print(im)
        width = im.size[0]
        height = im.size[1]
        tree = open(txt_file, 'r', encoding='UTF-8')
        node_root = Element('annotation')
        node_folder = SubElement(node_root, 'folder')
        node_folder.text = 'JPEGImages'
        node_filename = SubElement(node_root, 'filename')
        node_filename.text = txt_name_ + '.jpg'
        node_path = SubElement(node_root, 'path')
        node_path.text = ' '
        node_source = SubElement(node_root,'source')
        node_database = SubElement(node_source,'database')
        node_database.text = 'Unknown'

        node_size = SubElement(node_root, 'size')
        node_width = SubElement(node_size, 'width')
        node_width.text = str(width)
        node_height = SubElement(node_size, 'height')
        node_height.text = str(height)
        node_depth = SubElement(node_size, 'depth')
        node_depth.text = '3'

        root = tree.readlines()
        for i, line in enumerate(root):
            column = line.split(' ')
            print(column)
            node_object = SubElement(node_root, 'object')
            node_name = SubElement(node_object, 'name')
            if column[1] == '带电芯充电宝':
                node_name.text = 'core'
            else:
                node_name.text = 'coreless'   
            node_pose = SubElement(node_object, 'pose')
            node_pose.text = 'Unspecified'
            node_truncated = SubElement(node_object, 'truncated')
            node_truncated.text = '0'
            node_difficult = SubElement(node_object, 'difficult')
            node_difficult.text = '0'
            node_bndbox = SubElement(node_object, 'bndbox')
            node_xmin = SubElement(node_bndbox, 'xmin')
            node_xmin.text = column[2]
            node_ymin = SubElement(node_bndbox, 'ymin')
            node_ymin.text = column[3]
            node_xmax = SubElement(node_bndbox, 'xmax')
            node_xmax.text = column[4]
            node_ymax = SubElement(node_bndbox, 'ymax')
            node_ymax.text = column[5]
      
           
            
        xml = tostring(node_root, pretty_print=True)  #格式化显示，该换行的换行
        dom = parseString(xml)
        with open('data/Annotations/' + txt_name_+'.xml', 'w') as f:
            dom.writexml(f, indent='\t', addindent='\t', newl='\n', encoding="utf-8")


def convert(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)
 
 
def convert_annotation(image_id):
    in_file = open('data/Annotations/%s.xml' % (image_id))
    out_file = open('data/labels/%s.txt' % (image_id), 'w')
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
 
    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult) == 1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text),
             float(xmlbox.find('ymax').text))
        bb = convert((w, h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')


def convert_annotations():
    for image_ids in tqdm(glob.glob(opt.imgsetfile + '/*.jpg')):
        image_id = image_ids.split('\\')[-1][:-4]
        if not os.path.exists('data/labels/'):
            os.makedirs('data/labels/')
        convert_annotation(image_id)



 
 
if __name__ == "__main__":
    txtfile()
    data_path = os.path.join(os.getcwd(), opt.annsetfile)
    pic_path = os.path.join(os.getcwd(), opt.imgsetfile)
    txtToXml(pic_path,data_path)
    convert_annotations()
    with open('test.py','r') as f:
        exec(f.read())
