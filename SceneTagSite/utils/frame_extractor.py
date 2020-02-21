import cv2
import os

from django.conf import settings


Extracting_URL = u'/static/res/extracting.png'


def get_frame_url(video_pk, video_path, frame_num):
    frame_name = u"_frame" + str(frame_num) + u".jpg"
    frame_path = os.path.join(settings.MEDIA_ROOT, str(video_pk), u"output", frame_name)
    frame_url = os.path.join(settings.MEDIA_URL, str(video_pk), u"output", frame_name)

    if not os.path.isfile(frame_path):
        frame_url = Extracting_URL
        _extract_new_frame(video_path, frame_path, frame_num)

    return frame_url


def _extract_new_frame(video_path, frame_path, frame_num):
    if not os.path.isfile(frame_path):
        extract_new_frame(video_path, frame_path, frame_num)
    else:
        print("skip request (already done).")


def extract_new_frame(video_path, frame_path, frame_num):
    print("extract_new_frame: " + frame_path)
    vidcap = cv2.VideoCapture(video_path)
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)  # cv2.CAP_PROP_POS_FRAMES는 현재 프레임 위치를 의미합니다.
    success, image = vidcap.read()
    if success:
        print("make new capture frame: " + frame_path)
        width = vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        imS = cv2.resize(image, (int(width * 0.5), int(height * 0.5)))
        cv2.imwrite(frame_path, imS)
    else:
        print("!!!FAILURE!!! capture frame" + frame_path)
