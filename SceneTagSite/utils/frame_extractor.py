import cv2
import os

from django.conf import settings


def get_frame_url(video_pk, video_path, frame_num):
    frame_name = u"_frame" + str(frame_num) + u".jpg"
    frame_path = os.path.join(settings.MEDIA_ROOT, str(video_pk), frame_name)
    frame_url = os.path.join(settings.MEDIA_URL, str(video_pk), frame_name)

    if not os.path.isfile(frame_path):
        vidcap = cv2.VideoCapture(video_path)
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        success, image = vidcap.read()
        if success:
            print: "make new capture frame :" + frame_path
            width = vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            imS = cv2.resize(image, (int(width * 0.5), int(height * 0.5)))
            cv2.imwrite(frame_path, imS)
        else:
            print: "!!FAILURE!! capture frame" + frame_path

    return frame_url
