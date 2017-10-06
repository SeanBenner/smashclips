import numpy as np
import cv2
from moviepy.editor import VideoFileClip
import pytesseract
import PIL
import matplotlib.image as mpimg

def trackTemplate(frame, templ):

    # convert frame to grayscale
    grayFrame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # match template
    res = cv2.matchTemplate(grayFrame,templ,cv2.TM_CCOEFF_NORMED)

    # draw box around matches
    threshold = 0.8
    loc = np.where( res >= threshold)
    th, tw = templ.shape[:2]
    for pt in zip(*loc[::-1]):
        cv2.rectangle(frame, pt, (pt[0] + tw, pt[1] + th), (255,255,0), 2)

    # draw box around template location
    # th, tw = templ.shape[:2] # for the height and width of the box we're drawing
    # x, y = minLoc # minLoc is a point (x, y)
    # cv2.rectangle(frame, (x, y), (x+tw, y+th), color=[255,255,0], thickness=1) # draw rectangle

    return frame


if __name__ == '__main__':
    outFile2 = "test.mp4"
    vid = VideoFileClip("Smash Con 2017 SSBM - C9  Mang0 (Falco Mario) Vs Tempo  Axe (Pikachu YLink) Smash Melee WQ.mp4")
    percent = mpimg.imread("percent_template.jpg")

    outVid1 = vid.fl_image(lambda frame: trackTemplate(frame, percent))
    outVid1.write_videofile(outFile1, audio=False)
