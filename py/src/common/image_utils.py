from typing import Tuple
import cv2
import numpy as np

from .viz import viz_rotated_rectangle


def rotate_bound(image: np.ndarray, angle: float):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w / 2, h / 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))


def im_resize(img: np.ndarray, max_dim: int) -> np.ndarray:
    h, w = img.shape[:2]
    scale_factor = max_dim / max(img.shape)
    desired_size = (int(w * scale_factor), int(h * scale_factor))
    return cv2.resize(
        src=img,
        dsize=desired_size,
        interpolation=cv2.INTER_AREA if scale_factor < 1 else cv2.INTER_CUBIC,
    )


def to_rgb_img(depth_grid: np.ndarray) -> np.ndarray:
    return np.stack(((255.0 * depth_grid).astype(np.uint8),) * 3, axis=-1)


def crop_box(img: np.ndarray, box: Tuple) -> np.ndarray:
    angle = box[2]
    rows, cols = img.shape[0], img.shape[1]
    m = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
    img_rot = cv2.warpAffine(img, m, (cols, rows))

    # rotate bounding box
    rect_no_rot = (box[0], box[1], 0.0)
    box = cv2.boxPoints(rect_no_rot)

    pts = np.int0(box)
    pts[pts < 0] = 0

    # crop
    return img_rot[pts[1][1] : pts[0][1], pts[1][0] : pts[2][0]]
