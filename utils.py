import os
import urllib.error
from pytube import YouTube, Stream, StreamQuery
from urllib import request
import re
from PIL import Image, ImageTk
import ffmpeg
from shutil import disk_usage


path = os.curdir
image_name = "video_thumbnail.jpg"


class NotEnoughSpaceError(Exception):
    def __init__(self):
        super().__init__()

class DownloadingError(Exception):
    def __init__(self):
        super().__init__()

def site_exists(link: str) -> bool:
    try:
        request.urlopen(link)
    except (ConnectionError, ValueError):
        return False
    else:
        return True


def is_youtube_link(link: str) -> bool:
    return bool(re.search('www.youtube.com', link))


def network_connection_is_valid() -> bool:
    from socket import gethostname, gethostbyname
    loopback_address = "127.0.0.1"

    if gethostbyname(gethostname()) == loopback_address:
        return False
    else:
        return True


def check_config_file(pathToConfig:str = os.getcwd() + "config.JSON") -> bool:
    if os.path.isfile(pathToConfig):
        return True
    else:
        return False


def get_progressive_resolutions(video: YouTube):
    # return [resolution for resolution in video.streams.filter(custom_filter_functions=[lambda x: x.includes_audio_track and x.includes_video_track])]
    try:
        return {stream.resolution for stream in video.streams.filter(progressive=True)}
    except Exception:
        return []


def get_dash_resolutions(video: YouTube):
    try:
        streams = {stream.resolution for stream in video.streams.filter(is_dash=True)}
        if None in streams:
            streams.remove(None)
        # return [resolution for resolution in streams]
        # return [resolution for resolution in streams].sort()
        return streams

    except Exception:
        return []


def get_audio_bit_rates(video: YouTube):
    try:
        return {stream.abr for stream in video.streams.filter(only_audio=True)}
    except Exception:
        return []


def prepare_video(video: YouTube):
    try:
        request.urlretrieve(video.thumbnail_url, path + "\\" + image_name)
    except Exception:
        pass


def loadImage(path1, dimensions=(160, 160)):
    image: Image = Image.open(path1)
    resized_image = image.resize(dimensions)
    img = ImageTk.PhotoImage(resized_image)
    return img


def delete_video_thumbnail():
    if os.path.isfile(path + "\\" + image_name):
        os.remove(path + "\\" + image_name)


def sort_quality(test_list):
    res = sorted(test_list, key=lambda x: (len(x), x), reverse=True)
    return res


def normalise_filename(filename: str) -> str:
    new_filename = ""
    for char in filename:
        if char in ['"','/','\\','|','*','?',':','<','>']:
            new_filename = new_filename + '_'
        else:
            new_filename = new_filename + char
    return new_filename

def get_video_title(video: YouTube) -> str:
    try:
        title = video.title
    except (urllib.error.URLError, Exception):
        return ""
    else:
        return title

def download_video(video: YouTube, filePath: str, contains_audio, contains_video, resolution, abr):
    if contains_audio and contains_video:
        # dash or progressive
        if int(resolution.replace('p', '')) <= 720:
            # progressive
            video.streams.filter(res=resolution, is_dash=False).first().download(filename=filePath)
        else:
            # dash
            audioPath = filePath[:-4] + "_audio.mp4"
            videoPath = filePath[:-4] + "_video.mp4"

            download_only_audio(video, audioPath)
            download_only_video(video, resolution, videoPath)

            merge_audio_and_video(audioPath, videoPath, filePath)

    elif contains_audio and not contains_video :
        # converting mp4 -> mp3 is redundant because the file contains only audio, so renaming extension is sufficient
        download_only_audio(video, filePath, abr=abr)
    elif contains_video and not contains_audio:
        download_only_video(video, resolution, filePath)
    else:
        return -1

def download_only_audio(video, filePath, abr=None):
    if abr is not None:
        video.streams.filter(abr=abr, only_audio=True).first().download(filename=filePath)
    else:
        video.streams.filter(only_audio=True).first().download(filename=filePath)


def download_only_video(video, resolution, filePath):
    video.streams.filter(res=resolution, only_video=True).first().download(filename=filePath)


def merge_audio_and_video(audioPath, videoPath, outputPath):
    audio_stream = ffmpeg.input(audioPath)
    video_stream = ffmpeg.input(videoPath)
    ffmpeg.output(audio_stream, video_stream, outputPath).run()

def willFit(size, disk):
    return True if disk_usage(disk).free >= 1.01 * size else False