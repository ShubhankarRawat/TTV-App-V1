import edge_tts
import settings

def creating_narration_text(text_list):
    narration_text = ""
    narration_text_list = [x + ' \n' for x in text_list]
    narration_text = narration_text.join(narration_text_list)
    return narration_text


def synthesize_narration(text, folder_name, voice):
    comm = edge_tts.Communicate(text, voice)
    out_mp3 = settings.NARRATION_AUDIO_FILENAME_MP3
    comm.save_sync(folder_name + out_mp3)
    print("Narration Done")
    return out_mp3
