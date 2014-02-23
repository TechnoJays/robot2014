"""This module contains class for identifying vision targets.

NOTE: THIS RUNS ON THE DRIVER STATION, NOT ON THE ROBOT.

DO NOT UPLOAD TO THE ROBOT!!

"""

import cv2
import math
import numpy as np
import target


class ContourInfo(object):
    """Data structure to store details of a contour."""
    contour = None
    bounding_rect = None
    actual_width = None
    actual_height = None
    contour_area = None
    bounding_area = None
    is_vertical = None
    rectangularity = None
    center_mass = None
    aspect_ratio = None
    paired_horizontal_contour_data = None
    pairing_distance = None
    pairing_score = None
    pairing_vertical_score = None


class Targeting(object):
    """."""
    # TODO: convert to read these from a parameter file
    # TODO: search the rest of the code for constants

    # Camera view angle (49 for 1013)
    CAMERA_URL = "http://10.0.94.11/axis-cgi/mjpg/video.cgi?resolution=640x480"
    CAMERA_VIEW_ANGLE = 49
    CAMERA_RES_HEIGHT = 640
    CAMERA_RES_WIDTH = 480
    GREEN_MIN = np.array([75, 160, 65], np.uint8)
    GREEN_MAX = np.array([92, 255, 180], np.uint8)
    RECTANGULARITY_THRESHOLD = 40
    ASPECT_RATIO_THRESHOLD = 55

    _vcap = None

    def __init__(self):
        self._vcap = cv2.VideoCapture()

    def open(self):
        """."""
        return self._vcap.open(self.CAMERA_URL)

    def close(self):
        """."""
        self._vcap.release()

    def get_image(self):
        """."""
        if self._vcap:
            return self._vcap.read()
        else:
            return None
        #return cv2.imread('input.jpg')

    def score_aspect_ratio(self, contour_data):
        """."""
        rect_x, rect_y, rect_w, rect_h = contour_data.bounding_rect
        ideal_ratio = (4.0 / 32.0) if contour_data.is_vertical else (23.5 / 4.0)

        rect_long = rect_w if rect_w > rect_h else rect_h
        rect_short = rect_w if rect_w < rect_h else rect_h

        ratio = None
        if rect_w > rect_h:
            ratio = (rect_long * 1.0 / rect_short) / ideal_ratio
        else:
            ratio = (rect_short * 1.0 / rect_long) / ideal_ratio

        return max(0, min(100 * (1 - math.fabs(1 - ratio)), 100))

    def calculate_pairing_score(self, ratio):
        """."""
        if ratio <= 0 or ratio > 2:
            return 0.0
        return 100.0 - (math.fabs(1.0 - ratio) * 100.0)

    def calculate_distance(self, v_contour_data):
        """."""
        distance = 0
        try:
            rect_x, rect_y, rect_w, rect_h = v_contour_data.bounding_rect
            rect_long = rect_w if rect_w > rect_h else rect_h
            height = min(rect_h, rect_long)
            target_height = 32
            distance = self.CAMERA_RES_WIDTH * target_height / (height * 12 * 2 * math.tan(self.CAMERA_VIEW_ANGLE * math.pi / (180 * 2)))
        except Exception as excep:
            print(str(excep))
        return distance

    def calculate_angle(self, v_contour_data):
        """."""
        v_center_x, v_center_y = v_contour_data.center_mass
        degrees_per_pixel = 85 / math.sqrt((self.CAMERA_RES_HEIGHT ** 2) + (self.CAMERA_RES_WIDTH ** 2))
        pixels_off_center = v_center_x - (self.CAMERA_RES_WIDTH / 2)
        return pixels_off_center * degrees_per_pixel

    def is_valid_target(self, contour_data):
        """."""
        return contour_data.rectangularity > self.RECTANGULARITY_THRESHOLD and contour_data.aspect_ratio > self.ASPECT_RATIO_THRESHOLD

    def get_targets(self):
        """."""
        img = self.get_image()
        if not img:
            return []

        # Convert to HSV
        hsv = cv2.cvtColor(img, cv2.cv.CV_BGR2HSV)

        threshold = cv2.inRange(hsv, self.GREEN_MIN, self.GREEN_MAX)
        #cv2.imwrite("threshold.png", threshold)

        # Dilate
        element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilate = cv2.dilate(threshold, element, iterations=1)
        #cv2.imwrite("dilate.png", dilate)

        # Erode
        erode = cv2.erode(dilate, element, iterations=1)
        #cv2.imwrite("erode.png", erode)

        # Fill in the gaps
        #kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2), anchor=(1,1))
        #morphed = cv2.morphologyEx(erode, cv2.MORPH_CLOSE, kernel, iterations=9)
        #cv2.imwrite("morphed.png", morphed)

        # Find contours
        contours, hierarchy = cv2.findContours(erode.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)

        #color_img = cv2.cvtColor(erode, cv2.cv.CV_GRAY2BGR)

        # Calculate basic information about each contour
        contours_data = []
        for contour in contours:
            current_contour = ContourInfo()
            current_contour.contour = contour
            current_contour.contour_area = cv2.contourArea(contour)
            ((center_x, center_y), (width, height), angle) = cv2.minAreaRect(contour)
            current_contour.actual_width = width
            current_contour.actual_height = height
            rect_x, rect_y, rect_w, rect_h = cv2.boundingRect(contour)
            current_contour.bounding_rect = (rect_x, rect_y, rect_w, rect_h)
            current_contour.bounding_area = rect_w * rect_h
            center_x = rect_x + (rect_w / 2)
            center_y = rect_y + (rect_h / 2)
            current_contour.center_mass = (center_x, center_y)
            ratio = math.fabs(1.0 - ((rect_w * 1.0) / rect_h))
            if ratio > 1.0:
                current_contour.is_vertical = False
            else:
                current_contour.is_vertical = True
            current_contour.rectangularity = (current_contour.contour_area / current_contour.bounding_area) * 100.0
            current_contour.aspect_ratio = self.score_aspect_ratio(current_contour)
            contours_data.append(current_contour)

        # Split contours by vertical/horizontal and remove invalid targets
        vertical_contours = []
        horizontal_contours = []
        for contour_data in contours_data:
            if self.is_valid_target(contour_data):
                if contour_data.is_vertical:
                    vertical_contours.append(contour_data)
                else:
                    horizontal_contours.append(contour_data)

        # Draw each contour
        #for contour_data in vertical_contours:
        #    cv2.drawContours(color_img, contour_data.contour, -1, (0,0,255), thickness=2)

        #for contour_data in horizontal_contours:
        #    cv2.drawContours(color_img, contour_data.contour, -1, (0,0,255), thickness=2)

        matched_contours_data = []
        for v_contour_data in vertical_contours:
            v_rect_x, v_rect_y, v_rect_w, v_rect_h = v_contour_data.bounding_rect
            pair_found = False
            for h_contour_data in horizontal_contours:
                h_rect_x, h_rect_y, h_rect_w, h_rect_h = h_contour_data.bounding_rect
                h_center_x, h_center_y = h_contour_data.center_mass
                dist = cv2.pointPolygonTest(v_contour_data.contour, h_contour_data.center_mass, True)
                pairing_ratio = (math.fabs(dist) / h_rect_w)
                pairing_score = self.calculate_pairing_score(pairing_ratio)
                vertical_score = 1.0 - (math.fabs(v_rect_y - h_center_y) / (4.0 * h_rect_h))
                if vertical_score > 0.8 and pairing_score > 50:
                    v_contour_data.paired_horizontal_contour_data = h_contour_data
                    v_contour_data.pairing_distance = dist
                    v_contour_data.pairing_score = pairing_score
                    v_contour_data.pairing_vertical_score = vertical_score
                    matched_contours_data.append(v_contour_data)
                    pair_found = True
                    break
            if not pair_found:
                matched_contours_data.append(v_contour_data)

        targets = []
        for v_contour_data in matched_contours_data:
            current_target = target.Target()
            current_target.angle = self.calculate_angle(v_contour_data)
            current_target.distance = self.calculate_distance(v_contour_data)
            if v_contour_data.paired_horizontal_contour_data:
                current_target.is_hot = True
                current_target.confidence = v_contour_data.pairing_vertical_score * 50.0 + v_contour_data.pairing_score / 2.0
                side = v_contour_data.bounding_rect[0] - v_contour_data.paired_horizontal_contour_data.bounding_rect[0]
                if side < 0:
                    current_target.side = target.Side.RIGHT
                else:
                    current_target.side = target.Side.LEFT
            else:
                current_target.confidence = 0.0
                current_target.is_hot = False
                current_target.side = target.Side.UNKNOWN
            targets.append(current_target)

        #cv2.imwrite("result.png", color_img)
        return targets
