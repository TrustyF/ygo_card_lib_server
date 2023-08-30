import cv2
import numpy as np
import PIL


def auto_white_balance(img):
    result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    avg_a = np.average(result[:, :, 1])
    avg_b = np.average(result[:, :, 2])
    result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
    return result


def convertScale(img, alpha, beta):
    """Add bias and gain to an image with saturation arithmetics. Unlike
    cv2.convertScaleAbs, it does not take an absolute value, which would lead to
    nonsensical results (e.g., a pixel at 44 with alpha = 3 and beta = -210
    becomes 78 with OpenCV, when in fact it should become 0).
    """

    new_img = img * alpha + beta
    new_img[new_img < 0] = 0
    new_img[new_img > 255] = 255
    return new_img.astype(np.uint8)


def automatic_brightness_and_contrast(image, clip_hist_percent):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate grayscale histogram
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist_size = len(hist)

    # Calculate cumulative distribution from the histogram
    accumulator = [float(hist[0])]
    for index in range(1, hist_size):
        accumulator.append(accumulator[index - 1] + float(hist[index]))

    # Locate points to clip
    maximum = accumulator[-1]
    clip_hist_percent *= (maximum / 100.0)
    clip_hist_percent /= 2.0

    # Locate left cut
    minimum_gray = 0
    while accumulator[minimum_gray] < clip_hist_percent:
        minimum_gray += 1

    # Locate right cut
    maximum_gray = hist_size - 1
    while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
        maximum_gray -= 1

    # Calculate alpha and beta values
    if maximum_gray - minimum_gray != 0:
        alpha = 255 / (maximum_gray - minimum_gray)
    else:
        alpha = 255

    beta = -minimum_gray * alpha

    '''
    # Calculate new histogram with desired range and show histogram 
    new_hist = cv2.calcHist([gray],[0],None,[256],[minimum_gray,maximum_gray])
    plt.plot(hist)
    plt.plot(new_hist)
    plt.xlim([0,256])
    plt.show()
    '''

    auto_result = convertScale(image, alpha=alpha, beta=beta)
    return auto_result, alpha, beta


def contrast_and_exposure(img, exposure, contrast):
    return cv2.addWeighted(img, exposure, np.zeros(img.shape, img.dtype), 0, -contrast)


def custom_blur(img, basic_blur, gauss_blur):
    median = cv2.medianBlur(img, basic_blur)
    gauss = cv2.GaussianBlur(median, (11, 11), gauss_blur)
    return gauss


def modulo_2(value):
    if value % 2 == 0:
        value += 1
    return value


def canny(img, val0, val1):
    return cv2.Canny(img, val0, val1)


def resize_with_aspect_ratio(image, width=None, height=None, inter=cv2.INTER_AREA):
    # dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    if len(image.shape) < 3:
        formatted = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        formatted = image

    return cv2.resize(formatted, dim, interpolation=inter)


def dilate(image, val):
    dilate_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(val, val))
    dilated = cv2.dilate(image, dilate_kernel)
    return dilated


def straighten_crop_image(f_rect, image, f_margin):
    shape = (image.shape[1], image.shape[0])  # cv2.warpAffine expects shape in (length, height)
    center, size, theta = f_rect
    width, height = tuple(map(int, size))
    center = tuple(map(int, center))
    if width < height:
        theta += 90
        width, height = height, width

    matrix = cv2.getRotationMatrix2D(center=center, angle=theta, scale=1)
    image = cv2.warpAffine(src=image, M=matrix, dsize=shape)

    x = abs(int(center[0] - width // 2)) - f_margin
    y = abs(int(center[1] - height // 2)) - f_margin
    height += f_margin * 2
    width += f_margin * 2

    # image = image[y - f_margin: y + height + f_margin, x - f_margin: x + width + f_margin]
    image = image[y: y + height, x: x + width]

    # safety
    if image.shape[0] < 1 or image.shape[1] < 1:
        temp = list(image.shape)
        temp[0] += 100
        temp[1] += 100
        image = tuple(temp)

    return image


def easy_crop_cv(f_image, f_crop):
    h, w, _ = f_image.shape

    top = int((f_crop[1][0] / 100) * h)
    bot = int((f_crop[1][1] / 100) * h)
    left = int((f_crop[0][0] / 100) * w)
    right = int((f_crop[0][1] / 100) * w)

    return f_image[top:bot, left:right]


def easy_crop_pil(f_image, f_crop):
    w, h = f_image.size

    top = int((f_crop[1][0] / 100) * h)
    bot = int((f_crop[1][1] / 100) * h)
    left = int((f_crop[0][0] / 100) * w)
    right = int((f_crop[0][1] / 100) * w)

    return f_image.crop((left, top, right, bot))


def crop_white(f_image, f_threshold):
    th = f_image.copy()

    y0 = 0
    y1 = 0
    x0 = 0
    x1 = 0

    bbox = np.where(th < f_threshold)
    if bbox[0].any() or bbox[1].any():
        y0 = bbox[0].min()
        y1 = bbox[0].max()
        x0 = bbox[1].min()
        x1 = bbox[1].max()

    return f_image[y0:y1, x0:x1]


def convert_to_lab(f_image):
    lab = cv2.cvtColor(f_image, cv2.COLOR_BGR2LAB)
    ret, binary = cv2.threshold(lab[:, :, 1], 0, 255, cv2.THRESH_OTSU)
    return binary
