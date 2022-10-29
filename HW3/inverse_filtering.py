import numpy as np
import cv2
import cmath
import matplotlib.pyplot as plt

plt.figure(figsize=(25,17))     # 調整圖表大小

pic = cv2.imread("input.jpg", 0)    # 讀取圖片
pic_shift = pic.copy()

# 程式中，變數名稱成為大寫字母表示經傅立葉轉換之結果
# 原圖乘上 (-1) ^ (x+ y)，傅立葉轉換出來的結果相當於原圖做傅立葉後再 shift
for x in range(pic_shift.shape[0]):
    for y in range(pic_shift.shape[1]):
        pic_shift[x, y] = pic_shift[x, y] * ((-1) ** (x + y))
       
# 將剛剛的結果作傅立葉轉換
F = cv2.dft(np.float32(pic_shift),flags = cv2.DFT_COMPLEX_OUTPUT)
# 原圖做傅立葉轉換
F_origion = cv2.dft(np.float32(pic),flags = cv2.DFT_COMPLEX_OUTPUT)
# 把轉換結果轉成二接圖示(?
magnitude_spectrum = np.log(cv2.magnitude(F[:,:,0],F[:,:,1]))

# 分別秀出 原圖、傅立葉轉換(shift後)的圖
plt.subplot(2,3,1),plt.imshow(pic, cmap = 'gray')
plt.title('Input Image'), plt.axis('off')
plt.subplot(2,3,2),plt.imshow(magnitude_spectrum, cmap = 'gray')
plt.title('Magnitude Spectrum of input Image'), plt.axis('off')

# H: 破壞函式，這邊做的破壞式 motion blur
H = np.zeros(F.shape)
for u in range(-int(H.shape[0] / 2), int(H.shape[0] / 2)):
    for v in range(-int(H.shape[1] / 2), int(H.shape[1] / 2)):
        if u == 0 and v == 0:
            H[u + 256, v + 256] = 1
        else:
            H[u + 256, v + 256] = abs((1 / cmath.pi * (u * 0.1 + v * 0.1)) * \
                                      cmath.sin(cmath.pi * (u * 0.1 + v * 0.1)) * \
                                      cmath.e ** - (cmath.sqrt(-1) * cmath.pi * (u * 0.1 + v * 0.1)))

# G: 表示被破壞的影像(做法: 原圖 * 破壞函式)
G = np.zeros(F.shape)
G = H * F_origion
ifft_G = cv2.idft(G)

# 分別秀出 破壞函式圖形取log(有用絕對值 / 沒用絕對值)、被破壞之影像(用ifft逆傅立葉函式還原)
plt.subplot(2,3,3),plt.imshow(np.log(cv2.magnitude(H[:,:,0],H[:,:,1])), cmap = 'gray')
plt.title('H'), plt.axis('off')
plt.subplot(2,3,4),plt.imshow(np.abs(np.log(cv2.magnitude(H[:,:,0],H[:,:,1]))), cmap = 'gray')
plt.title('H_abs'), plt.axis('off')
plt.subplot(2,3,5),plt.imshow(cv2.magnitude(ifft_G[:, :, 0], ifft_G[:, :, 1]), cmap = 'gray')
plt.title('Motion Blur Result'), plt.axis('off')

# F_hat: 表示經過 Wiener filtering 試圖還原影像的結果
F_hat = np.zeros(F.shape)
for u in range(-int(H.shape[0] / 2), int(H.shape[0] / 2)):
    for v in range(-int(H.shape[1] / 2), int(H.shape[1] / 2)):
        if (H[u + 256, v + 256] == [0, 0]).all():           # 避免 divided by zero
            continue
        F_hat[u + 256, v + 256] = (1 / H[u + 256, v + 256]) * G[u + 256, v+ 256]
# 用 cv2.idft 逆傅立葉函示將其轉回影像     
ifft_ans = cv2.idft(F_hat)

# 秀出 還原影像
plt.subplot(2,3,6),plt.imshow(cv2.magnitude(ifft_ans[:, :, 0], ifft_ans[:, :, 1]), cmap = 'gray')
plt.title('F_hat'), plt.axis('off')
plt.show()