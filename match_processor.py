import pandas as pd
import numpy as np
import cv2
import matplotlib.image as mpimg
from moviepy.editor import VideoFileClip, ImageClip
import datetime
from scipy.stats import mode
import pytesseract
import PIL
import sqlalchemy

def load_percent_template():
    """Loads the % template in black and white"""
    TEMPLATE = mpimg.imread('percent_template.jpg')
    TEMPLATE = cv2.cvtColor(TEMPLATE, cv2.COLOR_RGB2GRAY)
    return TEMPLATE

TEMPLATE = load_percent_template()


def find_health_areas(frame):
    """Find the area to search for players' health.  Use average, gray
    image of video as input frame.  Returns bounding points for P1 and P2
    Returns:  y_top, y_bottom, p1_x_left, p1_x_right, p2_x_left, p2_x_right"""
    res = cv2.matchTemplate(frame, TEMPLATE, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= .7)

    y_top = mode(loc[0])[0][0] - int(TEMPLATE.shape[0]/2)
    y_bottom = y_top + int(3/2 * TEMPLATE.shape[0]) + 5
    p1_x_right = loc[1].min() + 1
    p1_x_left = p1_x_right - 150
    p2_x_right = loc[1].max() - 1
    p2_x_left = p2_x_right - 150

    P1_health = frame[y_top:y_bottom, p1_x_left:p1_x_right]
    P2_health = frame[y_top:y_bottom, p2_x_left:p2_x_right]

    return y_top, y_bottom, p1_x_left, p1_x_right, p2_x_left, p2_x_right

def extract_health_area(frame):
    """Get the area of health"""
    P1_health = frame[y_top:y_bottom, p1_x_left:p1_x_right]
    P2_health = frame[y_top:y_bottom, p2_x_left:p2_x_right]

    return P1_health, P2_health

# Using tesseract to OCR.
def ocr_health(h1, h2):
    """Input binarized health images.  Returns the health of the players as a string."""

    P1H = PIL.Image.fromarray(h1)
    P2H = PIL.Image.fromarray(h2)

    p1h = pytesseract.image_to_string(P1H, config='outputbase digits')
    p2h = pytesseract.image_to_string(P2H, config='outputbase digits')

    return p1h, p2h

# Template matching with probabilities of numbers for greater accuracy
def binarize_blurred_healths(p1h, p2h):
    """Takes in the blurred image and performs binarization and flood fill"""

    t1bin = np.where(p1h > 180, 255, 0)
    t1bin = t1bin.astype('uint8')
    t2bin = np.where(p2h > 180, 255, 0)
    t2bin = t2bin.astype('uint8')

    for row in range(t1bin.shape[0]):
        cv2.floodFill(t1bin, None, (0, row), 0)
        cv2.floodFill(t1bin, None, (149, row), 0)

    for col in range(t1bin.shape[1]):
        cv2.floodFill(t1bin, None, (col, 0), 0)
        cv2.floodFill(t1bin, None, (col, 64), 0)

    # Flood fill around perimeter of 2p health
    for row in range(t2bin.shape[0]):
        cv2.floodFill(t2bin, None, (0, row), 0)
        cv2.floodFill(t2bin, None, (149, row), 0)

    for col in range(t2bin.shape[1]):
        cv2.floodFill(t2bin, None, (col, 0), 0)
        cv2.floodFill(t2bin, None, (col, 64), 0)

    return t1bin, t2bin

def clean_ocr(ocr_result):
    """Takes the result of OCR and strips junk characters.  Also converts result to int"""
    health = "".join(num for num in ocr_result if num in '0123456789')
    if health == '':
        return None
    health = int(health)
    return health

def convert_to_seconds(frame, fps):
    """Given the frame number and fps of a video, this function returns which second the frame occured"""
    second = int(frame/fps)
    return second

def convert_seconds_to_timestamp(seconds):
    """Converts time in seconds to string 'H:MM:SS'"""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    stamp = '%d:%02d:%02d' % (h, m, s)
    return stamp

def get_average_image(clip):
    """Takes an .mp4 video and returns the average frame of the video, used for template matching the %
    and getting the search area of the health"""
    fps= 1.0 # take one frame per second
    nframes = clip.duration*fps # total number of frames used
    total_image = sum(clip.iter_frames(fps,dtype=float, progress_bar=True))
    img = ImageClip(total_image/ nframes)
    # Convert to gray
    img = img.img
    img = cv2.cvtColor(img.astype('uint8'), cv2.COLOR_RGB2GRAY)
    return img

def find_combos(df):
    """Takes a cleaned dataframe of points in match and extracts combos/highlights.
    Returns (p1_combos, p2_combos), where p_combos = (start_time, stop_time, deltas)"""
    p1_combos = []
    i = 1
    while i < len(df)-1:
        i += 1
        if df.loc[i, 'p1_delta'] > 2 and df.loc[i, 'p1_delta'] < 30:
            p1_time = df.loc[i, 'frame']
            deltas = [df.loc[i, 'p1_delta']]
            start_sec = df.loc[i, 'second'] - 2
            start_time = convert_seconds_to_timestamp(start_sec)
            for j in range(i+1, len(df)):
                if df.loc[j, 'p1_delta'] > 2 and df.loc[j, 'p1_delta'] < 30 and ((df.loc[j, 'frame'] - p1_time) <= 75):
                    deltas.append(df.loc[j, 'p1_delta'])
                    p1_time = df.loc[j, 'frame']
                    stop_sec = df.loc[j, 'second'] + 2
                    stop_time = convert_seconds_to_timestamp(stop_sec)
                if ((df.loc[j, 'frame'] - p1_time) > 75):
                    i = j + 1
                    break
            # If combo is at least 4 hits and greater than 10%, append it to combos list
            if len(deltas) >= 3 and sum(deltas) >= 10:
                p1_combos.append((start_time, stop_time, deltas))

    # Find combos for player 2
    p2_combos = []
    i = 1
    while i < len(df)-1:
        i += 1
        if df.loc[i, 'p2_delta'] > 2 and df.loc[i, 'p2_delta'] < 30:
            p2_time = df.loc[i, 'frame']
            deltas = [df.loc[i, 'p2_delta']]
            start_sec = df.loc[i, 'second'] - 2
            start_time = convert_seconds_to_timestamp(start_sec)
            for j in range(i+1, len(df)):
                if df.loc[j, 'p2_delta'] > 2 and df.loc[j, 'p2_delta'] < 30 and ((df.loc[j, 'frame'] - p2_time) <= 75):
                    deltas.append(df.loc[j, 'p2_delta'])
                    p2_time = df.loc[j, 'frame']
                    stop_sec = df.loc[j, 'second'] + 2
                    stop_time = convert_seconds_to_timestamp(stop_sec)
                if ((df.loc[j, 'frame'] - p2_time) > 75):
                    i = j + 1
                    break
            # If combo is at least 4 hits and greater than 10%, append it to combos list
            if len(deltas) >= 3 and sum(deltas) >= 10:
                p2_combos.append((start_time, stop_time, deltas))

    # We have actually found the combos that happened TO player 1 and 2.
    return (p2_combos, p1_combos)

def extract_clips(combos, player, match_name):
    """Takes an array of the combos found and creates highlight clips"""
    clip_array = []
    for num, C in enumerate(combos):
        filename = "{}_clip_{}:  {}".format(player, num, match_name)
        clip = vid.subclip(C[0], C[1])
        clip.write_videofile(filename, progress_bar=False)
        clip_array.append(filename)
        return clip_array

def raw_data_pipeline(raw_data):
    """Takes the raw data of health over frames and converts it to a useable dataframe.  Returns pandas dataframe"""

    #  Load data to DF, label and clean OCR
    df = pd.DataFrame.from_dict(raw_data, orient='index')
    df.columns = ['p1_health', 'p2_health']
    df.p1_health = df.p1_health.apply(clean_ocr)
    df.p2_health = df.p2_health.apply(clean_ocr)

    # Drop Nans and unrealistic values
    df.dropna(axis='index', how='all', inplace=True)
    df = df[(df.p1_health < 250) & (df.p2_health < 250)]

    # Create frames column
    df['frame'] = df.index

    # Reset index
    df = df.set_index([list(range(len(df)))])

    # Add seconds, timestamps, and health deltas to dataframe
    df['second'] = df.frame.apply(lambda frame: convert_to_seconds(frame, 30))
    df['timestamp'] = df.second.apply(convert_seconds_to_timestamp)

    # Add damage deltas
    for i in range(1, len(df)):
        df.loc[i, 'p1_delta'] = df.loc[i, 'p1_health'] - df.loc[i-1, 'p1_health']
        df.loc[i, 'p2_delta'] = df.loc[i, 'p2_health'] - df.loc[i-1, 'p2_health']

    return df

def connect(user, password, db, host='localhost', port=5432):
    '''Returns a connection and a metadata object'''
    # We connect with the help of the PostgreSQL URL
    # postgresql://federer:grandestslam@localhost:5432/tennis
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)

    # The return value of create_engine() is our connection object
    con = sqlalchemy.create_engine(url, client_encoding='utf8')

    # We then bind the connection to MetaData()
    meta = sqlalchemy.MetaData(bind=con, reflect=True)

    return con, meta
