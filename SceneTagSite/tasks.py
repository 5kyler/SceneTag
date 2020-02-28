import json
import requests
import os
from django.conf import settings


def communicator(server_url, frame, modules=None):
    start_frame = frame.start_frame
    video_id = frame.video.pk
    image_path = os.path.join(settings.MEDIA_ROOT, str(video_id), u"_frame" + str(start_frame) + u".jpg")

    if modules is not None :
        json_data = {'modules' : modules}
    else:
        json_data = {}
    print(json_data)

    json_image = open(image_path, 'rb')
    json_files = {'image': json_image}

    result_response = requests.post(url=server_url, data=json_data, files=json_files)
    result_data = json.loads(result_response.content)

    result = result_data['results']
    json_image.close()

    return result