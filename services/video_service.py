import os
import cv2
import shutil
import re
import settings
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    CompositeAudioClip,
    concatenate_videoclips
)
from utils.helper_functions import (
    video_generation1_fast,
    adding_audio_to_puttext_video,
    check_video_duration
)
from services.whisperx_service import (
    video_generation2_with_overlays,
    pre_render_overlays
)

def video_generation(text_list, folder_name, subtitle_timestamp_list, subtitle_text_word_split, bg_music_genre, title, width, height):
    print('Video Generation Started')

    output_video_name1 = video_generation1_fast(folder_name) #video_generation1(folder_name)

    # subtitle text
    #subtitle_text = " ".join(text_list)
    #re.sub(r"[^\w\s]", "", subtitle_text)
    # removing -,?,.,, from text to be displayed on video - now not using this as it removes minus sign, decimals etc
    #subtitle_text_word_split = subtitle_text.split(" ")

    # Define the codec and create VideoWriter object.
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    savepath = folder_name + "output_" + output_video_name1.split(".")[0] + ".avi"
    savepath_with_audio = folder_name + "output_0.mp4"
    savepath_temp = folder_name + "temp_output_" + output_video_name1.split(".")[0] + ".avi"
    #savepath_no_frames_temp = folder_name + "temp_no_frames_output_" + output_video_name1.split(".")[0] + ".avi"

    # writing text on each video frame
    out = cv2.VideoWriter(savepath, fourcc, settings.FPS, (width, height))
    # reading the video of images
    cap = cv2.VideoCapture(folder_name + output_video_name1)
 
    # Syncing Audio and Subtitles
    print('Syncing Audio and Subtitles')
    overlays = pre_render_overlays(width, height, subtitle_text_word_split, settings.WORDS_GROUP)
    video_generation2_with_overlays(cap, out, settings.WORDS_GROUP, subtitle_timestamp_list, subtitle_text_word_split, overlays, savepath)
    #video_generation2_with_timestamps_from_vosk_model(cap, out, settings.WORDS_GROUP, subtitle_timestamp_list, subtitle_text_word_split, savepath)

    # checking whether puttext video is generated without duration
    check_video_duration(savepath_temp, savepath)

    # adding audio to puttext video
    adding_audio_to_puttext_video(savepath_temp, folder_name, bg_music_genre, savepath_with_audio, title)

    return savepath_with_audio