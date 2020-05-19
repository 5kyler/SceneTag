import os

from cv2 import CAP_PROP_FRAME_COUNT, CAP_PROP_POS_FRAMES
import math

from django.db import models

import scenedetect
from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.stats_manager import StatsManager
from scenedetect.detectors import ContentDetector

from background_task import background
from django.contrib import admin


class SBDVideo(models.Model):
    file_path = models.CharField(max_length=255)
    processed_frames = models.IntegerField(default=0)
    total_frames = models.IntegerField(default=0)
    is_complete = models.BooleanField(default=False)


admin.site.register(SBDVideo)


def get_sbd_video(video_filepath):
    video = SBDVideo.objects.filter(file_path=video_filepath)
    if len(video) == 0:
        return None
    else:
        return video[0]


def request_detect(video_filepath):
    # check video model existance
    video = get_sbd_video(video_filepath)
    if not video:
        # make new video model
        video = SBDVideo()
        video.file_path = video_filepath
        video.save()
        _detect(video_filepath)


@background(schedule=5)
def _detect(video_filepath):
    video = get_sbd_video(video_filepath)

    print("task" + video.file_path + "\tstart<<<<")

    detector = SBDetector(video_filepath=video.file_path)
    cur_frames, total_frames = detector.get_progress()

    video.processed_frames = cur_frames
    video.total_frames = total_frames
    video.save()

    video.is_complete = True
    video.save()

    print("task" + video.file_path + "\t>>>end")


class SceneManagerMod(SceneManager):
    def detect_scenes(self, frame_source, end_time=None, frame_skip=0,
                      show_progress=True):

        #        Optional[Union[int, FrameTimecode]], Optional[bool]) -> int
        """ Perform scene detection on the given frame_source using the added SceneDetectors.

        Blocks until all frames in the frame_source have been processed. Results can
        be obtained by calling either the get_scene_list() or get_cut_list() methods.

        Arguments:
            frame_source (scenedetect.video_manager.VideoManager or cv2.VideoCapture):
                A source of frames to process (using frame_source.read() as in VideoCapture).
                VideoManager is preferred as it allows concatenation of multiple videos
                as well as seeking, by defining start time and end time/duration.
            end_time (int or FrameTimecode): Maximum number of frames to detect
                (set to None to detect all available frames). Only needed for OpenCV
                VideoCapture objects; for VideoManager objects, use set_duration() instead.
            frame_skip (int): Not recommended except for extremely high framerate videos.
                Number of frames to skip (i.e. process every 1 in N+1 frames,
                where N is frame_skip, processing only 1/N+1 percent of the video,
                speeding up the detection time at the expense of accuracy).
                `frame_skip` **must** be 0 (the default) when using a StatsManager.
            show_progress (bool): If True, and the ``tqdm`` module is available, displays
                a progress bar with the progress, framerate, and expected time to
                complete processing the video frame source.
        Returns:
            int: Number of frames read and processed from the frame source.
        Raises:
            ValueError: `frame_skip` **must** be 0 (the default) if the SceneManager
                was constructed with a StatsManager object.
        """

        if frame_skip > 0 and self._stats_manager is not None:
            raise ValueError('frame_skip must be 0 when using a StatsManager.')

        start_frame = 0
        curr_frame = 0
        end_frame = None

        total_frames = math.trunc(frame_source.get(CAP_PROP_FRAME_COUNT))

        start_time = frame_source.get(CAP_PROP_POS_FRAMES)
        if isinstance(start_time, FrameTimecode):
            start_frame = start_time.get_frames()
        elif start_time is not None:
            start_frame = int(start_time)
        self._start_frame = start_frame

        curr_frame = start_frame

        if isinstance(end_time, FrameTimecode):
            end_frame = end_time.get_frames()
        elif end_time is not None:
            end_frame = int(end_time)

        if end_frame is not None:
            total_frames = end_frame

        if start_frame is not None and not isinstance(start_time, FrameTimecode):
            total_frames -= start_frame

        if total_frames < 0:
            total_frames = 0

        progress_bar = None

        '''
        if tqdm and show_progress:
            progress_bar = tqdm(
                total=total_frames, unit='frames')
       '''
        try:

            while True:
                if end_frame is not None and curr_frame >= end_frame:
                    break
                # We don't compensate for frame_skip here as the frame_skip option
                # is not allowed when using a StatsManager - thus, processing is
                # *always* required for *all* frames when frame_skip > 0.
                if (self._is_processing_required(self._num_frames + start_frame)
                        or self._is_processing_required(self._num_frames + start_frame + 1)):
                    ret_val, frame_im = frame_source.read()
                else:
                    ret_val = frame_source.grab()
                    frame_im = None

                if not ret_val:
                    break
                self._process_frame(self._num_frames + start_frame, frame_im)

                curr_frame += 1
                self._num_frames += 1
                if progress_bar:
                    # print self._num_frames
                    # self.progress_num_frames = self._num_frames
                    progress_bar.update(1)

                if frame_skip > 0:
                    for _ in range(frame_skip):
                        if not frame_source.grab():
                            break
                        curr_frame += 1
                        self._num_frames += 1
                        if progress_bar:
                            progress_bar.update(1)

            self._post_process(curr_frame)

            num_frames = curr_frame - start_frame

        finally:

            if progress_bar:
                progress_bar.close()

        return num_frames


class SBDetector():
    def __init__(self, video_filepath):
        # Create a video_manager point to video file testvideo.mp4. Note that multiple
        # videos can be appended by simply specifying more file paths in the list
        # passed to the VideoManager constructor. Note that appending multiple videos
        # requires that they all have the same frame size, and optionally, framerate.

        self.stats_file_path = video_filepath + '.csv'
        self.video_manager = VideoManager([video_filepath])
        self.stats_manager = StatsManager()
        self.scene_manager = SceneManagerMod(self.stats_manager)

        # Add ContentDetector algorithm (constructor takes detector options like threshold).
        self.scene_manager.add_detector(ContentDetector())
        self.base_timecode = self.video_manager.get_base_timecode()

        # If stats file exists, load it.
        if os.path.exists(self.stats_file_path):
            # Read stats from CSV file opened in read mode:
            with open(self.stats_file_path, 'r') as stats_file:
                self.stats_manager.load_from_csv(stats_file, self.base_timecode)

        start_time = self.base_timecode + 20  # 00:00:00.667
        end_time = self.base_timecode + 20.0  # 00:00:20.000
        # Set video_manager duration to read frames from 00:00:00 to 00:00:20.
        # video_manager.set_duration(start_time=start_time, end_time=end_time)

        # Set downscale factor to improve processing speed.
        self.video_manager.set_downscale_factor()

        # Start video_manager.
        self.video_manager.start()

    def __del__(self):
        self.video_manager.release()

    def get_progress(self):
        cur_timecode = self.scene_manager._num_frames
        total_frames = self.video_manager.get(CAP_PROP_FRAME_COUNT)
        return cur_timecode, total_frames

    def detect(self, inner_margin=5):
        # Perform scene detection on video_manager.
        #        scene_manager.detect_scenes(frame_source=video_manager,
        #                                    start_time=start_time)
        self.scene_manager.detect_scenes(frame_source=self.video_manager, show_progress=True)

        # Obtain list of detected scenes.
        scene_list = self.scene_manager.get_scene_list(self.base_timecode)
        # Like FrameTimecodes, each scene in the scene_list can be sorted if the
        # list of scenes becomes unsorted.

        return_list = []
        print('List of scenes obtained:')
        for i, scene in enumerate(scene_list):
            print('    Scene %2d: Start %s / Frame %d, End %s / Frame %d' % (
                i + 1,
                scene[0].get_timecode(), scene[0].get_frames(),
                scene[1].get_timecode(), scene[1].get_frames(),))
            start_frame = scene[0].get_frames() + inner_margin
            end_frame = scene[1].get_frames() - inner_margin
            if start_frame < end_frame:
                shot = [start_frame, end_frame]
                return_list.append(shot)

        # We only write to the stats file if a save is required:
        if self.stats_manager.is_save_required():
            with open(self.stats_file_path, 'w') as stats_file:
                self.stats_manager.save_to_csv(stats_file, self.base_timecode)

        return return_list
