#@title Helper functions
### HELPER FUNCTIONS
from google.genai import types
import gradio_client

import requests
from PIL import Image, ImageDraw, ImageFont

import pathlib
import textwrap
import os

import numpy as np
from moviepy.editor import *

import re
import cv2
import random
import shutil, time
from google.genai import types

import settings
from utils.file_utils import create_folder
### function to resize images
def resize_image(image_name):
    img = Image.open(image_name)
    img2 = img.crop((6, 0, img.size[0] - 6, img.size[1]))
    img2 = img2.resize((1080, 1920))
    img2.save(image_name)


### function to get response from GenAI model with title, description, etc
def get_response_from_genai_model(client, system_instruction, prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction = system_instruction, # gemini context instructions
            thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
        ),
    )
    return response


def get_details_of_video_from_genai_model_response(response_text):
    text_list = []
    image_list = []
    lines = response_text.split("\n")
    for line in lines:
        if line.startswith('Narrator: '):
            text = line.replace('Narrator: ', '')
            text_list.append(text.strip('"'))

        elif line.startswith('['):
            background = line.strip('[]')
            image_list.append(background)
        elif line.startswith('Title: '):
            title = line.replace('Title: ', '')
        elif line.startswith('Description: '):
            description = line.replace('Description: ', '')
        elif line.startswith('Tags: '):
            tags = line.replace('Tags: ', '')
        elif line.startswith('Bg_music: '):
            bg_music_genre = line.replace('Bg_music: ', '')
    
    
    #print("title: ", title)
    #print("description: ", description)
    #print("tags: ", tags)
    #print("bg_music_genre: ", bg_music_genre)
    print("Text_list: ")
    for i, i_text_list in enumerate(text_list):
        print(f"{str(i)}. {i_text_list}")
    print("Image_list: ")
    for i, i_image_list in enumerate(image_list):
        print(f"{str(i)}. {i_image_list}")
    
    return text_list, image_list, title, description, tags, bg_music_genre





def video_generation1_fast(
    folder_name: str,
    output_name: str = "final_video1.mp4",
    fps: int = settings.FPS,
    preset: str = settings.MOVIEPY_PRESET,
    codec: str = settings.CODEC,
    bitrate: str = settings.BITRATE,
    crf: int = settings.CRF,
    audio_codec: str = settings.AUDIO_CODEC,
    audio_bitrate: str = settings.AUDIO_BITRATE,
    threads: int = None,
    fade_duration: float = settings.FADE_DURATION,
    zoom_rate: float = settings.ZOOM_RATE
    ):
    start_time_video_generation1_fast = time.time()
    """
    Creates a video with images zooming centered and crossfading, matching narration length.

    The total video duration is set so that final video length equals exactly the audio duration.

    Parameters:
    - folder_name: path to images and 'audio.mp3'
    - output_name: filename for the generated video
    - fps, preset, codec, bitrate, crf, audio_codec, audio_bitrate, threads: encoding options
    - fade_duration: seconds to crossfade between images
    - zoom_rate: zoom scale per second

    Returns:
    - output_name
    """
    # Gather & sort images
    image_names = sorted(
        f for f in os.listdir(folder_name)
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    )
    if not image_names:
        raise FileNotFoundError("No images found in folder.")

    # Video canvas size from first image
    first = ImageClip(os.path.join(folder_name, image_names[0]))
    video_size = first.size
    first.close()

    # Load audio narration
    audio_path = os.path.join(folder_name, settings.NARRATION_AUDIO_FILENAME_MP3)
    audio_clip = AudioFileClip(audio_path)
    audio_duration = audio_clip.duration

    # Compute image display duration to match audio length after overlap
    n = len(image_names)
    # Total video length L = n*d - fade*(n-1), want L = audio_duration => d = (audio_duration + fade*(n-1))/n
    image_duration = (audio_duration + fade_duration * (n - 1)) / n
    print(f"1 image duration = {image_duration}")

    # Build clips
    clips = []
    for img in image_names:
        path = os.path.join(folder_name, img)
        base = ImageClip(path).set_duration(image_duration).set_fps(fps)
        zoomed = base.resize(lambda t: 1 + zoom_rate * t)
        # Center on canvas
        comp = CompositeVideoClip([zoomed.set_position('center')], size=video_size)
        # fade in/out at boundaries
        clip = comp.crossfadein(fade_duration).crossfadeout(fade_duration)
        clips.append(clip)

    # Concatenate with negative padding for overlap
    final = concatenate_videoclips(clips, method='compose', padding=-fade_duration)
    # CRUCIAL FIX → force exact match to audio length
    final = final.set_duration(audio_duration)
    # Attach narration (no trimming or looping)
    final = final.set_audio(audio_clip)

    # Prepare threads count
    total_th = threads or (os.cpu_count() or 1)
    print("Number of threads detected = ", total_th)
    th = int(total_th/3)
    if th == 0:
        th = 1
    print(f"Using {th}/{total_th} threads")
    # Export with quality/speed params
    final.write_videofile(
        os.path.join(folder_name, output_name),
        fps=fps,
        codec=codec,
        preset=preset,
        bitrate=bitrate,
        ffmpeg_params=['-crf', str(crf), '-movflags', 'faststart'],
        audio_codec=audio_codec,
        audio_bitrate=audio_bitrate,
        threads=th
    )

    print("Time taken in video_generation1_fast = ", (time.time()-start_time_video_generation1_fast)/60, " mins")
    return output_name


### function tp check whether duration is present in video generated after putting text
def check_video_duration(savepath_temp, savepath):
    cap = cv2.VideoCapture(savepath)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    print(f'Checking Video: Frames = {frames} fps: {fps}')

    if frames == 0:
        print(f'No frames data in video, trying to convert this video..')
        writer = cv2.VideoWriter(savepath_temp, cv2.VideoWriter_fourcc(*'DIVX'), int(cap.get(cv2.CAP_PROP_FPS)),(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
        while True:
            ret, frame = cap.read()
            if ret is True:
                writer.write(frame)
            else:
                cap.release()
                print("Stopping video writer")
                writer.release()
                writer = None
                break
    else:
      shutil.copyfile(savepath, savepath_temp)


#####
def adding_audio_to_puttext_video(savepath_temp, folder_name, bg_music_genre, savepath_with_audio, title):
    #### Adding audio back using moviepy
    videoclip = VideoFileClip(savepath_temp)
    audio_clip = AudioFileClip(folder_name + settings.NARRATION_AUDIO_FILENAME_MP3).set_duration(videoclip.duration)

    bg_music_path = settings.BG_MUSIC_PATH + bg_music_genre + "/"
    bg_music_names = os.listdir(bg_music_path)

    random_index_bg_music = random.randint(0, len(bg_music_names) - 1)
    bg_music_selected = bg_music_names[random_index_bg_music]
    print("Background music name = ", bg_music_selected)

    start_point_bg_music = 0
    if bg_music_selected == 'Thinking Of Us.mp3':
      start_point_bg_music = 2
    if bg_music_selected == 'Oceans, Rivers, Canyons - ELPHNT.mp3':
      start_point_bg_music = 13
    if bg_music_selected == 'Please - Wayne Jones.mp3':
      start_point_bg_music = 15
    if bg_music_selected == 'Øneheart - apathy.mp3':
      start_point_bg_music = 11
    if bg_music_selected == 'stellar.mp3':
      start_point_bg_music = 1.2

    background_music = AudioFileClip(bg_music_path + bg_music_selected).subclip(start_point_bg_music, start_point_bg_music + videoclip.duration).volumex(0.1)
    new_audioclip = CompositeAudioClip([audio_clip, background_music])

    videoclip.audio = new_audioclip
    videoclip.write_videofile(savepath_with_audio, fps = settings.FPS)
    print("Final video saved at = ", savepath_with_audio)
