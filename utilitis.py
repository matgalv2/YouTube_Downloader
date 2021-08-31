import os
import urllib.error
from pytube import YouTube, Stream, StreamQuery
from urllib import request
import re
from PIL import Image, ImageTk


path = os.curdir
image_name = "video_thumbnail.jpg"


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

def get_video(audio, video, resolution, abr):
    pass
