from google import genai
from google.genai import types
import settings
from utils.media_utils import resize_and_pad
from utils.helper_functions import (
    get_response_from_genai_model,
    get_details_of_video_from_genai_model_response
)

def generate_script_and_metadata(user_prompt, num_images_for_video_length):
    """
    Calls the GenAI client to generate the narration script, image descriptions,
    and metadata (title, description, tags, bg_music) for a YouTube video.

    Returns:
      - text_list: List[str], narration sentences
      - image_prompts: List[str], prompts for images
      - title: str
      - description: str
      - tags: str
      - bg_music: str
    """
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    print()
    print("PROCESS STARTED FOR INPUT PROMPT = ", user_prompt)

    system_instruction = (
        """
            You are a video narration generator. The videos you create have a background that fades from image to image as the narration is going on.
            You will have to start the narration with "Did you know" so that it hooks the viewer and makes them watch the complete video. Also make the narration engaging and knowledgeful such that the viewer gains knowledge like interesting facts and figures. Try to end the video with a question to the audience related to the topic for their opinion in the comment box wherever relevant.
            You will need to generate in-depth well detailed descriptions of images for each of the sentences in the video. They will be passed to an AI image generator. DO NOT IN ANY CIRCUMSTANCES use names of celebrities or people in the image descriptions. It is illegal to generate images of celebrities. Only describe persons without their names. Do not reference any real person or group in the image descriptions. Don't mention the female figure or other sexual content in the images because they are not allowed.
            You are however allowed to use any content, including real names in the narration. Only image descriptions are restricted.
        """
    )

    prompt = """
    using above knowledge, generate a script for the video in the above format with exactly {} text/image pairs and each text being exactly {} words long, on the topic: {}
    """.format(num_images_for_video_length, settings.NUMBER_OF_WORDS_IN_ONE_TEXT_FOR_VIDEO_LENGTH, user_prompt)


    num_text_image_pairs = settings.NUM_TEXT_IMAGE_PAIRS
    print("Number of Image-text pairs in video = ", num_text_image_pairs)
    final_prompt = """
    You are a video narration generator. The videos you create have a background that fades from image to image as the narration is going on.
    You will have to start the narration with "Did you know" so that it hooks the viewer and makes them watch the complete video. Also make the narration engaging and knowledgeful such that the viewer gains knowledge like interesting facts and figures. Try to end the video with a question to the audience related to the topic for their opinion in the comment box wherever relevant.
    You will need to generate in-depth well detailed descriptions of images for each of the sentences in the video. They will be passed to an AI image generator. DO NOT IN ANY CIRCUMSTANCES use names of celebrities or people in the image descriptions. It is illegal to generate images of celebrities. Only describe persons without their names. Do not reference any real person or group in the image descriptions. Don't mention the female figure or other sexual content in the images because they are not allowed.
    You are however allowed to use any content, including real names in the narration. Only image descriptions are restricted.

    Note that the narration will be fed into a text-to-speech engine, so don't use special characters.
    Respond with a pair of an image description in square brackets and a narration below it. Both of them should be on their own lines, as follows:

    ###

    [Description of a background image]

    Narrator: "One sentence of narration"

    [Description of a background image]

    Narrator: "One sentence of narration"

    [Description of a background image]

    Narrator: "One sentence of narration"

    ###
    note that in the above format the lines should begin with either [ or Narrator: and not any other character (not even a space)
    there should be exactly a total of {} pairs of image descriptions and narration for the video.
    You should add a description of a fitting backround image in between all of the narrations. It will later be used to generate an image with AI.
    also give a video and interesting title, description, tags, best suiting background music genre from the following choices: [chill, inspirational, peace] (also if the video is related to outer space make the bg_music as peace)
    in the following format, strictly follow the following format:

    ###

    Title: "title of the video"

    Description: "description of the video" (write a long description of about 400 words which will be search engine optimized so that new users can search it properly)

    Tags: "tags for the video" (only words no hashtags, generate about 20 tags)

    Bg_music: "background music genre for the video which can only be one of the three: chill, inspirational or peace"

    ###
    note that the above format should not contain any special character (not even space) or number in the beginning, it should always start with the text
    {}
    """.format(num_text_image_pairs, prompt)

    response = get_response_from_genai_model(client, system_instruction, final_prompt)
    print()
    print("GenAI model's response obtained")
    # Parse the response into components
    text_list, image_prompts, title, description, tags, bg_music_genre = get_details_of_video_from_genai_model_response(response.text)

    title = title.replace('"', '').replace("'", "")
    description = description.replace('"', '').replace("'", "")
    tags = tags.replace('"', '').replace("'", "")
    bg_music_genre = bg_music_genre.replace('"', '').replace("'", "")

    return text_list, image_prompts, title, description, tags, bg_music_genre
