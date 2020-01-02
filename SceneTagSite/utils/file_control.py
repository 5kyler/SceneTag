# -*- coding: utf-8 -*-

from django.conf import settings

import os


def get_unregistered_files():
    upload_root = os.path.join(settings.UPLOAD_ROOT)
    files = os.walk(upload_root).__next__()[2]

    return files


def move_file_to_pk_directory(filename, pk):
    upload_root = os.path.join(settings.UPLOAD_ROOT)
    upload_filepath = os.path.join(upload_root, filename)

    work_root = os.path.join(settings.MEDIA_ROOT)
    target_dir = os.path.join(work_root, str(pk))
    target_filepath = os.path.join(target_dir, filename)
    rel_path = os.path.join(str(pk), filename)

    os.makedirs(target_dir)
    os.chmod(target_dir, 0o777)

    os.rename(upload_filepath, target_filepath)

    return rel_path
