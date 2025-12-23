import gradio_client
import settings
from utils.file_utils import create_folder

def get_image_sdxl_flash(image_list, width, height, negative_prompt=settings.NEGATIVE_IMAGE_PROMPT):
    """
    Generates images using the SDXL-Flash Gradio API and saves them to a specified local directory.

    Args:
        image_list (list): A list of image prompts (strings).
        negative_prompt (str): Negative prompt for image generation.
    Returns:
        list: A list of results from the Gradio API, where each result contains
              information about the generated image, including its local path.
    """
    # Ensure the base output directory exists
    output_base_dir=settings.FOLDER_FOR_DOWNLOADED_IMAGES_FROM_API
    create_folder(output_base_dir)

    print("In get_image_sdxl_flash function")

    results = []
    i = 1
    for prompt in image_list:
        # Create a unique subdirectory for each prediction if needed,
        # or just use the output_base_dir directly.
        # For simplicity, let's just use the output_base_dir for all images
        # generated in this function call.
        # If you need a *new* folder for *each* image, you'd need more complex logic here
        # For now, all images from this function call will go into output_base_dir.

        # Initialize the client, specifying the download_files directory
        client = gradio_client.Client(
            "KingNish/SDXL-Flash",
            download_files=output_base_dir # <--- This is the key change!
        )

        result = client.predict(
            prompt=prompt,
            negative_prompt="nsfw, naked, nude, penis, nipples, naked body, groin area naked, naked breasts, uncovered breasts, vagina, cunt" + negative_prompt,
            use_negative_prompt=True,
            seed=1231713621,
            width=width,
            height=height,
            guidance_scale=settings.GUIDANCE_SCALE,
            num_inference_steps=settings.NUM_INFERENCE_STEPS,
            randomize_seed=settings.RANDOMIZE_SEED,
            api_name="/run"
        )
        results.append(result)
        print(result) # This will now show paths within your specified output_base_dir
        print('Generating {}/{} image'.format(str(i), len(image_list)))
        i = i + 1
    return results 