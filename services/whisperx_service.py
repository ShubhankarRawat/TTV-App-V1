import os
import math
import cv2
import torch



import whisperx  # pip install git+https://github.com/m-bain/whisperX.git
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import settings
import time



def load_whisperx_models():
    print("Started to Load WhisperX model")
    start_whisperx_model_load_time = time.time()
    model = whisperx.load_model(settings.WHISPERX_MODEL, device = settings.WHISPERX_DEVICE, compute_type = settings.COMPUTE_TYPE)
    print(f"Time taken to load WhisperX model = {(time.time()-start_whisperx_model_load_time)/60} mins")

    print("Started to Load WhisperX Align model")
    start_whisperx_align_model_load_time = time.time()
    align_model, metadata = whisperx.load_align_model(language_code=settings.WHISPERX_LANGUAGE, device=settings.WHISPERX_DEVICE)
    print(f"Time taken to load WhisperX model = {(time.time()-start_whisperx_align_model_load_time)/60} mins")
    return model, align_model, metadata

def get_subtitles_from_whisperx(model, align_model, metadata, audio_path, words_group: int = settings.WORDS_GROUP):
    """
    Run WhisperX to align transcript to audio and chunk into word groups.
    Returns:
      subtitle_timestamp_list: List[float]
      subtitle_text_word_split: List[List[str]]
    """
    # 1) Transcribe
    result = model.transcribe(audio_path)

    # 2) Forced alignment
    result_aligned = whisperx.align(result["segments"], align_model, metadata, audio_path, settings.WHISPERX_DEVICE)
    print("Timestamps obtained")

    word_segments = result_aligned["word_segments"]

    # 3) Chunk into groups of words
    subtitle_timestamp_list = []
    subtitle_text_word_split = []
    total = len(word_segments)
    for i in range(0, total, words_group):
        chunk = word_segments[i: i + words_group]
        if not chunk:
            break
        subtitle_timestamp_list.append(chunk[0]["start"])  # start time of first word
        subtitle_text_word_split.append([w["word"].upper() for w in chunk])

    print("subtitle_timestamp_list = ", subtitle_timestamp_list)
    print("subtitle_text_word_split = ", subtitle_text_word_split)
    return subtitle_timestamp_list, subtitle_text_word_split


# styling parameters
def render_line(fontpath, draw, text, width, y_offset, fill, font_size):
    font = ImageFont.truetype(fontpath, font_size)
    # measure
    _, _, w, h = draw.textbbox((0,0), text, font=font)
    # shrink until fits
    while w + 30 > width:
        font_size -= 2
        font = ImageFont.truetype(fontpath, font_size)
        _, _, w, h = draw.textbbox((0,0), text, font=font)
    x = (width - w) // 2
    y = y_offset
    # draw semi-transparent box
    box = (x-15, y-15, x+w+15, y+h+15)
    draw.rectangle(box, fill=(0,0,0,int(255*settings.TEXT_BOX_OPACITY)))
    # draw text with stroke
    draw.text((x,y), text, font=font, fill=fill, stroke_width=settings.STROKE_WIDTH, stroke_fill=settings.STROKE_COLOR)


def pre_render_overlays(width, height, subtitle_text_word_split: list[list[str]], words_group: int=settings.WORDS_GROUP):
    """
    Pre-render each subtitle group onto a transparent RGBA image.
    Returns a list of numpy arrays (BGR with alpha channel merged).
    """
    print("Pre-rendering Overlays Started")
    overlays = []
    fontpath = settings.FONT_PATH + settings.FONT_STYLE

    for i in range(0, len(subtitle_text_word_split), 2):
        # join into two lines
        first_line = " ".join(subtitle_text_word_split[i]).upper()
        print(f"First line = {first_line}")
        if i+1 < len(subtitle_text_word_split):
            second_line = " ".join(subtitle_text_word_split[i+1]).upper()
        else:
            second_line = None
        print(f"Second line = {second_line}")

        # create blank transparent canvas same size as video resolution
        # swap if necessary: if resolution is landscape
        canvas = Image.new("RGBA", (width, height), (0,0,0,0))
        draw = ImageDraw.Draw(canvas)

        # position lines vertically in center
        # estimate height of two lines
        test_font = ImageFont.truetype(fontpath, 100)
        _, _, fw, fh = draw.textbbox((0,0), first_line, font=test_font)

        if second_line:
            _, _, sw, sh = draw.textbbox((0,0), second_line, font=test_font)
            total_h = fh + sh + 30
        else:
            total_h = fh
        start_y = (height - total_h) // 2

        ## render 1st line
        render_line(fontpath, draw, first_line, width, start_y, fill=settings.FIRST_LINE_SUBS_COLOR, font_size=settings.FONT_SIZE)
        
        # Render second line if exists (blue)
        if second_line:
            render_line(fontpath, draw, second_line, width, start_y + fh + 30, fill=settings.SECOND_LINE_SUBS_COLOR, font_size=settings.FONT_SIZE)
        
        #### Converting PIL image back to cv2 image
        # convert to BGR
        rgba = np.array(canvas)
        # alpha composite onto black background
        bgr = cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA)
        overlays.append(bgr)
    
    print("Pre-rendering Overlays Completed")
    return overlays


def video_generation2_with_overlays(
    cap, out, words_group,
    subtitle_timestamp_list, subtitle_text_word_split,
    overlays, savepath: str
    ):
    """
    Writes frames by compositing pre-rendered overlays at correct times.
    """
    frame_idx = 0
    cue_idx   = 0
    num_cues  = len(subtitle_timestamp_list)
    num_ol    = len(overlays)

    fps = settings.FPS #cap.get(cv2.CAP_PROP_FPS)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        time_s = frame_idx / fps
        # advance cue_idx if needed
        if cue_idx+1 < num_cues and time_s >= subtitle_timestamp_list[cue_idx+1]:
            cue_idx += 1
        # overlay image with alpha channel
        # Compute which overlay to use (two timestamps per overlay)
        overlay_idx = min(cue_idx // 2, num_ol - 1)
        #overlay = overlays[cue_idx]
        overlay = overlays[overlay_idx]

        # assume overlay has 4th channel alpha
        alpha = overlay[:, :, 3:] / 255.0
        fg = overlay[:, :, :3]
        bg = frame.astype(float)
        frame = (fg * alpha + bg * (1 - alpha)).astype(np.uint8)
        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"video saved as = {savepath}")
    return cue_idx
