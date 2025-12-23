import torch


import gradio as gr
import settings
from services.genai_service import generate_script_and_metadata
from services.speech_service import synthesize_narration, creating_narration_text
from services.whisperx_service import get_subtitles_from_whisperx, load_whisperx_models
from services.image_service import generate_images
from services.video_service import video_generation
from utils.file_utils import create_folder
import time
import os

# Load WhisperX model
model, align_model, metadata = load_whisperx_models()

# Single unified function
def start_code(prompt, negative_prompt, backend, shape, num_images_for_video_length, style, request: gr.Request):
    print("Current directory contains: ", os.listdir())
    #folder_name = settings.FOLDER_NAME + str(request.session_hash) + "/"
    folder_name = str(request.session_hash) + "/"
    #folder_name = os.path.join(base_output_dir, str(request.session_hash))
    start_time = time.time()
    # 1. Prepare workspace
    create_folder(folder_name)
    print("Using directory = ", folder_name)

    # 2. Generate script + metadata
    text_list, img_prompts, title, desc, tags, bg_music_genre = generate_script_and_metadata(prompt, num_images_for_video_length)
    narration_text = creating_narration_text(text_list)

    # 3. Synthesize speech
    mp3 = synthesize_narration(narration_text, folder_name, settings.TTS_VOICE)

    # 4. Transcribe timestamps
    audio_path = folder_name + settings.NARRATION_AUDIO_FILENAME_MP3
    #audio_path = os.path.join(folder_name, settings.NARRATION_AUDIO_FILENAME_MP3)
    print("audio_path = ", audio_path)
    subtitle_timestamp_list, subtitle_text_word_split = get_subtitles_from_whisperx(model, align_model, metadata, audio_path, settings.WORDS_GROUP)

    # 5. Generate AI images
    image_paths, width, height = generate_images(img_prompts, folder_name, negative_prompt, backend, style, shape)

    # 6. Build video
    video_out = f"{folder_name}output.mp4"
    relative_video_path = video_generation(text_list, folder_name, subtitle_timestamp_list, subtitle_text_word_split, bg_music_genre, title, width, height)
    savepath_with_audio = os.path.join(os.getcwd(), relative_video_path)

    end_time = time.time()
    print(f"Total time taken = {(end_time-start_time)/60} mins")

    time.sleep(5)
    print("savepath_with_audio = ", savepath_with_audio)
    print("type of savepath_with_audio = ", type(savepath_with_audio))
    return title, desc, tags, bg_music_genre, savepath_with_audio


def delete_directory(req: gr.Request):
    if not req.username:
        return
    folder_name = settings.FOLDER_NAME + str(request.session_hash)
    shutil.rmtree(folder_name)


# Gradio Interface
iface = gr.Interface(
    fn=start_code,
    inputs=[
            # input prompt
            gr.Textbox(lines=5, label="Input Prompt"),
            # negative prompt
            gr.Textbox(lines=5, label="Negative Prompt"),
            # backend
            gr.Dropdown(
                choices=[settings.IMAGE_BACKEND_SDXL_FLASH, settings.IMAGE_BACKEND_POLLINATION_FLUX,
                        settings.IMAGE_BACKEND_POLLINATION_TURBO, settings.IMAGE_BACKEND_POLLINATION_KONTEXT],
                label="Select Image Generation Model",
                value=settings.DEFAULT_BACKEND
            ),
            # shape
            gr.Dropdown(
                choices=[settings.ORIENTATION_LANDSCAPE, settings.ORIENTATION_SQUARE, settings.ORIENTATION_PORTRAIT],
                label="Select Video Orientation",
                value=settings.DEFAULT_ORIENTATION
            ),
            # number of images in video - determines video length
            gr.Slider(
                minimum=1,
                maximum=10,
                step=1,
                value=5,
                label="Select the number of images in the video. Note: This determines the video length, more images = longer video."
            ),
            # Dropdown for image styles
            gr.Dropdown(
                choices=settings.AVAILABLE_STYLES,
                label="Select Video Style",
                value=settings.DEFAULT_STYLE # You can set a default value, or leave it None
            )
            ],
    outputs=[
            gr.Textbox(label="Title"),
            gr.Textbox(label="Description"),
            gr.Textbox(label="Tags"),
            gr.Textbox(label="Background Music Type"), 
            gr.Video(label="Video")],
    title="TTV App",
    description="Turn prompts into short videos",
    concurrency_limit=20,
    delete_cache=(60*10, 60*10) # delete temp files created by gradio, params = (frequency, age) in seconds
)

iface.unload(delete_directory)

iface.queue(default_concurrency_limit = 4, max_size = 6)
iface.launch(debug=True, server_name="0.0.0.0", server_port=7860) #share=True