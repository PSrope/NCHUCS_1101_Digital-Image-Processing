from PIL import Image
import numpy as np
import cv2

# 本程式只適用於 mask 為 3 x 3 的情況

# 把要被捲積的原圖做 padding，因 mask 為 3 x 3，padding 寬度為 1 (上下左右各加 1)
def padding(img_name, img_w, img_h):
    img = Image.open(img_name)
    new_img = Image.new("RGB", (img_w + 2, img_h + 2), "White")
    new_img.paste(img, (1, 1))

    return cv2.cvtColor(np.asarray(new_img), cv2.COLOR_RGB2GRAY)

# 實作捲積
def convolution(image_name, mask, img_w, img_h, out_name):
    out_p = padding(image_name, img_w, img_h)
    out_img = cv2.imread(image_name, 0)        # 要輸出的圖，用 imread 只是為了取出影像格式

    # 用 padding 後的圖跟 mask 做捲積，把每個 pixel 運算結果傳給輸出影像的對應位置
    for i in range(1, img_h + 1):
        for j in range(1, img_w + 1):
            # cur 紀錄該 pixel 的捲積結果
            cur = 0
            cur += out_p[i - 1, j - 1] * mask[0][0] # 左上
            cur += out_p[i - 1, j] * mask[0][1]     # 中上
            cur += out_p[i - 1, j + 1] * mask[0][2] # 右上
            cur += out_p[i, j - 1] * mask[1][0]     # 中左
            cur += out_p[i, j] * mask[1][1]         # 正中
            cur += out_p[i, j + 1] * mask[1][2]     # 中右
            cur += out_p[i + 1, j - 1] * mask[2][0] # 左下
            cur += out_p[i + 1, j] * mask[2][1]     # 中下
            cur += out_p[i + 1, j + 1] * mask[2][2] # 右下

            # 因為灰階是在 0 ~ 255 之間，超過的要把他們抓回來
            if cur > 255:
                out_img[i - 1, j - 1] = 255
            elif cur < 0:
                out_img[i - 1, j - 1] = 0
            else:
                out_img[i - 1, j - 1] = int(cur)    # 這邊要把數值轉回整數
    # 輸出影像
    cv2.imwrite(out_name, out_img)
    return out_img

# 用 gradient equation 公式計算邊緣
def find_edge(image_name, img_w, img_h, out_name):
    out_image = cv2.imread(image_name, 0)
    out_p = padding(image_name, img_w, img_h)

    for i in range(1, img_h + 1):
        for j in range(1, img_w + 1):
            out_image[i - 1, j - 1] = (abs((out_p[i + 1, j - 1] + 2 * out_p[i + 1, j] + out_p[i + 1, j + 1]) - 
                                           (out_p[i - 1, j - 1] + 2 * out_p[i - 1, j] + out_p[i - 1, j + 1])) +
                                       abs((out_p[i - 1, j + 1] + 2 * out_p[i, j + 1] + out_p[i + 1, j + 1]) - 
                                           (out_p[i - 1, j - 1] + 2 * out_p[i, j - 1] + out_p[i + 1, j - 1])))
    
    cv2.imwrite(out_name, out_image)
    return out_image

# 做影像正規化 ex: 灰階影像的 0 ~ 255 轉成 0 ~ 1
# num 表示原來的區間大小
def normalization(img, num, img_w, img_h):
    out = []

    for i in range(img_h):
        out.append([])
        for j in range(img_w):
            out[i].append(float(img[i, j] / num))

    return out

# 做影像"相加"
def add(img1, img2, img_w, img_h, out_name):
    out_image = img1.copy()
    # 相加時，要把大於 255 的變回 255，小於 0 的變回 0
    for i in range(img_h):
        for j in range(img_w):
            if int(img1[i, j]) + int(img2[i, j]) >= 255:
                    out_image[i, j] = 255
            elif int(img1[i, j]) + int(img2[i, j]) <= 0:
                    out_image[i, j] = 0
            else:
                out_image[i, j] = int(img1[i, j]) + int(img2[i, j])

    cv2.imwrite(out_name, out_image)
    return out_image

# 做影像 和 正規化影像 "相乘"   
def multipy(img, img_normal, img_w, img_h, out_name):
    out_image = img.copy()

    for i in range(img_h):
        for j in range(img_w):
            if int(img[i, j] * img_normal[i][j]) >= 255:
                out_image[i, j] = 255
            elif int(img[i, j] * img_normal[i][j]) <= 0:
                out_image[i, j] = 0
            else:
                out_image[i, j] = int(img[i, j] * img_normal[i][j])

    cv2.imwrite(out_name, out_image)
    return out_image

# 以 Sobel Mask 取影像邊緣
def sobel(img_name, img_w, img_h, out_name):
    sh_pic = convolution(img_name, sobel_hor_mask, pic_w, pic_h, out_name + "_hor.jpg") # 水平
    sv_pic = convolution(img_name, sobel_ver_mask, pic_w, pic_h, out_name + "_ver.jpg") # 垂直
    add(sh_pic, sv_pic, img_w, img_h, out_name + ".jpg")                                # 兩者相加
    return sh_pic


Laplacian_mask = [[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]] 
sobel_hor_mask = [[1, 0, -1], [2, 0, -2], [1, 0, -1]]
sobel_ver_mask = [[1, 2, 1], [0, 0, 0], [-1, -2, -1]]
GaussianBlur_mask = [[1 / 16, 2 / 16, 1 / 16], [2 / 16, 4 / 16, 2 / 16], [1 / 16, 2 / 16, 1 / 16]]

pic = cv2.imread("NICO.jpg", 0)
pic_h, pic_w = pic.shape[0], pic.shape[1]

laplacian_pic = convolution("NICO.jpg", Laplacian_mask, pic_w, pic_h, "out_NICO/NICO_laplacian.jpg")
ori_lap_pic = add(pic, laplacian_pic, pic_w, pic_h, "out_NICO/NICO_ori+lap_pic.jpg")

edge_pic = find_edge("NICO.jpg", pic_w, pic_h, "out_NICO/NICO_edge.jpg")
sobel_pic = sobel("NICO.jpg", pic_w, pic_h, "out_NICO/NICO_sobel")
blur_pic = convolution("out_NICO/NICO_edge.jpg", GaussianBlur_mask, pic_w, pic_h, "out_NICO/NICO_blur.jpg")
pic_normal = normalization(blur_pic, 255, pic_w, pic_h)
lap_nor_pic = multipy(laplacian_pic, pic_normal, pic_w, pic_h, "out_NICO/NICO_lap_multi_nor.jpg")
final_pic = add(pic, lap_nor_pic, pic_w, pic_h, "out_NICO/NICO_final.jpg")

# 課本的實作方法 (第四步差異)
lap_nor_pic2 = multipy(ori_lap_pic, pic_normal, pic_w, pic_h, "out_NICO/NICO_lap_multi_nor2.jpg")
final_pic2 = add(pic, lap_nor_pic2, pic_w, pic_h, "out_NICO/NICO_final2.jpg")
