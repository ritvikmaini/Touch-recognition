"""Blob detection: background subtraction -> contours -> ellipse centers."""

import cv2

from .touch import Touch


class Detector:
    """Detects touch blobs in a grayscale frame against a reference frame."""

    def __init__(self, reference, threshold=10, min_area=30, blur_ksize=20):
        self.reference = reference
        self.threshold = threshold
        self.min_area = min_area
        self.blur_ksize = blur_ksize

    def binarize(self, frame):
        dframe = cv2.absdiff(frame, self.reference)
        blurred = cv2.blur(dframe, (self.blur_ksize, self.blur_ksize))
        highpass = cv2.absdiff(dframe, blurred)
        _, binarized = cv2.threshold(highpass, self.threshold, 255, cv2.THRESH_BINARY)
        return binarized

    def detect(self, frame, frame_no):
        binarized = self.binarize(frame)
        contours, hierarchy = cv2.findContours(
            binarized, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE
        )
        touches = []
        if hierarchy is not None and len(hierarchy) > 0:
            hierarchy = hierarchy[0]
            for idx in range(len(hierarchy)):
                if cv2.contourArea(contours[idx]) > self.min_area and len(contours[idx]) > 4:
                    ellipse = cv2.fitEllipse(contours[idx])
                    cx, cy = ellipse[0][0], ellipse[0][1]
                    touches.append(Touch(cx, cy, frame_no))
        return touches
