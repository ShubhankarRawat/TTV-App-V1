import os
from utils.media_utils import resize_and_pad, resize_and_crop
from services.ai_image_generator.sdxl_flash_hf import get_image_sdxl_flash
from services.ai_image_generator.pollination import get_pollinationAI
import shutil
import settings

def get_width_height_from_shape(shape):
    if shape == settings.ORIENTATION_LANDSCAPE:
        width = settings.SDXL_IMAGE_DIM_1344
        height = settings.SDXL_IMAGE_DIM_768
    elif shape == settings.ORIENTATION_PORTRAIT:
        width = settings.SDXL_IMAGE_DIM_768
        height = settings.SDXL_IMAGE_DIM_1344
    elif shape == settings.ORIENTATION_SQUARE:
        width = settings.SDXL_IMAGE_DIM_1024
        height = settings.SDXL_IMAGE_DIM_1024
    else:
        raise ValueError("shape selected is not in {settings.ORIENTATION_LANDSCAPE}, {settings.ORIENTATION_PORTRAIT}, and {settings.ORIENTATION_SQUARE}")
    return width, height



def generate_images(prompts, folder_name, negative_prompt, backend, style=None, shape=settings.DEFAULT_ORIENTATION):
    """
    Unified interface: choose between SDXL Flash and Perchance.
    """
    ### shape is used for perchance since it takes str values: "landscape", "portrait", "square"
    ### width, height are used by sdxl and pollination
    width, height = get_width_height_from_shape(shape)
    pollination_model = ""
    if backend in [settings.IMAGE_BACKEND_POLLINATION_FLUX, settings.IMAGE_BACKEND_POLLINATION_TURBO, settings.IMAGE_BACKEND_POLLINATION_KONTEXT]:
        pollination_model = backend
        backend = settings.IMAGE_BACKEND_POLLINATION
    
    print(f"backend = {backend}")
    print(f"pollination_model = {pollination_model}")

    if backend == settings.IMAGE_BACKEND_SDXL_FLASH:
        # incorporate style/shape into prompt prefix
        prefixed = [f"(style: {style}), {p}" if style else p for p in prompts]
        print("PROMPTs Fed to SDXL:")
        i = 1
        for aux_prompt in prefixed:
            print(f"{str(i)}. {aux_prompt}")
            i = i + 1

        results = get_image_sdxl_flash(prefixed, width, height, negative_prompt)
        paths = []
        for idx, entry in enumerate(results):
            src = entry[0][0]['image']
            ext = os.path.splitext(src)[1]
            dest = os.path.join(folder_name, f"image_{idx}{ext}")
            shutil.move(src, dest)
            width, height = resize_and_crop(dest, shape)
            paths.append(dest)
        return paths, width, height
           
    elif backend == settings.IMAGE_BACKEND_POLLINATION:
        prefixed = [f"(style: {style}), {p}" if style else p for p in prompts]
        print("PROMPTs Fed to Pollination:")
        for i, aux_prompt in enumerate(prefixed):
            print(f"{str(i+1)}. {aux_prompt}")
        results = get_pollinationAI(prompts, width, height, pollination_model, folder_name, negative_prompt)

        for entry in results:
            width, height = resize_and_crop(entry, shape)
        return results, width, height
    else:
        raise ValueError(f"Unknown backend {backend}")

