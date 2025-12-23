import os

# =======================================================================
#  settings.py - config file
# =======================================================================

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
POLLINATIONS_API_TOKEN = os.getenv("POLLINATIONS_API_TOKEN")

VOSK_MODEL_PATH = "vosk-model-en-us-0.22-lgraph"
FOLDER_NAME = "project_0/"
NARRATION_AUDIO_FILENAME_MP3 = "audio.mp3"
NARRATION_AUDIO_FILENAME_WAV = "audio.wav"
VIDEO_OUT_NAME = "output.mp4"
TTS_VOICE = "en-GB-SoniaNeural"

NUMBER_OF_WORDS_IN_ONE_TEXT_FOR_VIDEO_LENGTH = 10

# Image
ORIENTATION_LANDSCAPE = "Landscape"
ORIENTATION_SQUARE = "Square"
ORIENTATION_PORTRAIT = "Portrait"
DEFAULT_ORIENTATION = ORIENTATION_LANDSCAPE
NEGATIVE_IMAGE_PROMPT = ""#"poor quality, low quality, deformation" 

## perchance
#PERCHANCE_URL = "https://perchance.org/ai-girl-image-generator"
#BATCH_TIMEOUT = 60
DOWNLOAD_DIR = "downloaded_files/"
AVAILABLE_STYLES = ['Painted Anime', 'Casual Photo', 'Cinematic', 'Digital Painting', 'Concept Art', 'No Style']
DEFAULT_STYLE = "Cinematic"
AVAILABLE_SHAPES = ['Landscape', 'Portrait', 'Square']
DEFAULT_SHAPE = "Landscape"


## SDXL
SDXL_IMAGE_DIM_768 = 768
SDXL_IMAGE_DIM_1344 = 1344
SDXL_IMAGE_DIM_1024 = 1024
GUIDANCE_SCALE = 4
NUM_INFERENCE_STEPS = 20
RANDOMIZE_SEED = True

## Pollination
POLLINATION_URL = "https://image.pollinations.ai/prompt"
POLLINATION_MODEL = "flux"

FPS = 24
MOVIEPY_PRESET = 'ultrafast'
CODEC = 'libx264'
BITRATE = '3000k'
CRF = 23
AUDIO_CODEC = 'aac'
AUDIO_BITRATE = '192k'
FADE_DURATION = 2.0
ZOOM_RATE = 0.04

BG_MUSIC_PATH = 'bg_music/'
FONT_PATH = "fonts/"
FONT_STYLE = "BurbankBigCondensed-Black.otf" #"LuckiestGuy-Regular.ttf"
FONT_SIZE = 100
FIRST_LINE_SUBS_COLOR = (255,100,0)
SECOND_LINE_SUBS_COLOR = (0,0,255)
TEXT_BOX_OPACITY = 0.6
STROKE_WIDTH = 4
STROKE_COLOR = (255,255,255)
NUM_TEXT_IMAGE_PAIRS = 1
FOLDER_FOR_DOWNLOADED_IMAGES_FROM_API = "generated_images_from_api"

# New: allow user choose model and resolution
IMAGE_BACKEND_SDXL_FLASH = "SDXL Flash"
IMAGE_BACKEND_PERCHANCE = "Perchance"
IMAGE_BACKEND_POLLINATION = "Pollination"
IMAGE_BACKEND_POLLINATION_FLUX = "flux"
IMAGE_BACKEND_POLLINATION_TURBO = "turbo"
IMAGE_BACKEND_POLLINATION_KONTEXT = "kontext"
DEFAULT_BACKEND = IMAGE_BACKEND_POLLINATION_FLUX


# Whisperx
WORDS_GROUP = 3
WHISPERX_MODEL = "small.en"
WHISPERX_DEVICE = "cpu"
COMPUTE_TYPE = "float32" #"float16" for gpu
WHISPERX_LANGUAGE = "en" 
