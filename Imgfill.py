"""
@author: zengjx
@date: 2022/4/25
@description: 瓦特曼面试
"""
import json
import cv2

class imgFill(object):
    def __init__(self,json_path):
        self.get_box = self.get_box_b(json_path)

    @staticmethod
    def get_box_b(json_path):
        """""
        获取json文件中box_b的的坐标
        Args:
            json_path:json文件路径
        Return:
            result:box_b坐标,格式为[left, top, right, bottom]
        """""
        with open(json_path, 'r') as f:
            fr = json.load(f)
            rect_dic = fr['boxes'][1]['rectangle']
            #print(rect_dic)
            left = rect_dic['left_top']
            right = rect_dic['right_bottom']
            result = left + right
        return result

    def is_box_avaliable(self,img):
        """""
          判断box_b指定的区域是否超出img的边界
          Args:
              img:目标图像
          Return:
              result: True or False
        """""
        left_x,left_y = self.get_box[:2]
        h = self.get_box[3] - self.get_box[1]
        w = self.get_box[2] - self.get_box[0]
        h_img, w_img = img.shape[:2]
        result1 = left_x >= 0 and (left_x + w) <= w_img #判断宽是否在图片的宽以内
        result2 = left_y >= 0 and (left_y + h) <= h_img #判断高是否在图片的高以内
        return result1 and result2

    def fillimg(self,src_img,dst_img,mode='A'):
        """
        图片填充
        Args:
            src_img: 原始图像
            dst_img: 目标图像
            mode (str): 填充模式, "A"指拉伸填充, "B"指保持比例填充
        Returns:
            dst_img: 填充后的图像
        """
        ok = self.is_box_avaliable(dst_img)
        if not ok:
            return
        #获取box_b的坐标以及w，h
        left_x,left_y,right_x,right_y = self.get_box[:4]
        box_b_w = right_x - left_x
        box_b_h = right_y - left_y

        assert mode in ["A", "B"], "'A'指拉伸填充, 'B'指保持比例填充"

        if mode == "A":
            src_img_new = cv2.resize(src_img, dsize=(box_b_h, box_b_w))
            dst_img[left_y:right_y,left_x:right_x] = src_img_new

        if mode == "B":
            #等比例缩放，先获取原图的w、h，获取缩放比例
            h_src_img, w_src_img = src_img.shape[:2]
            ratio_w=  box_b_w / w_src_img
            ratio_h = box_b_h / h_src_img
            ratio = min(ratio_w, ratio_h)
            src_img = cv2.resize(src_img, (0, 0), fx=ratio, fy=ratio)
            src_h_new, src_w_new, _ = src_img.shape
            if box_b_h >= src_h_new:
                # 沿y轴进行padding
                padding = (box_b_h - src_h_new) // 2
                # 填充
                dst_img[left_y + padding:left_y + padding + src_h_new, left_x:right_x] = src_img
            else:
                # 沿x轴进行padding
                padding = (box_b_w - src_w_new) // 2
                # 填充
                dst_img[left_y:right_y, left_x + padding:left_x + padding + src_w_new] = src_img
        return dst_img

if __name__ == '__main__':
    json_path = './boxes.json'
    imgfill = imgFill(json_path)
    src_img = cv2.imread('./vlcsnap-2022-03-18-15h05m03s416.jpg')
    dst_img = cv2.imread('./vlcsnap-2022-04-24-10h33m33s236.jpg')
    imgfill.fillimg(src_img=src_img,dst_img=dst_img,mode="B")
    cv2.imshow('res',dst_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
