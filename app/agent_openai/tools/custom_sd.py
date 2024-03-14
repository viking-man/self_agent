from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from app.agent_openai.agent.agent_config import STABLE_DIFFUSION_MODEL_PATH
from langchain.agents import tool
from torch import torch
import time
from pathlib import Path
from app.common.utils import string_utils
from translatepy import Translate


class CustomStableDiffusion:

    def __init__(self) -> None:
        self.pipeline = StableDiffusionPipeline.from_single_file(STABLE_DIFFUSION_MODEL_PATH)
        self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(self.pipeline.scheduler.config)
        # self.pipeline.safety_checker = None
        # self.pipeline.requires_safety_checker = False
        DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        self.pipeline = self.pipeline.to(DEVICE)


sd = CustomStableDiffusion()

'''该方法用于用户绘画相关的需求，提供根据文本生成图片的能力，用户输入图片相关的指令描述，该方法返回对应的图片输出'''


def translate_text(image_text, target_language='zh-CN'):
    translator = Translate()
    translated_text = translator.translate(image_text, target_language).result
    return translated_text


@tool
def sculpture(prompt: str = ""):
    '''This method is used for user drawing-related needs, providing the ability to generate images based on the text, the user inputs a description of the image-related instructions, the method returns the corresponding image output'''

    if string_utils.contains_chinese(prompt):
        prompt = translate_text(prompt, target_language="en")

    image = sd.pipeline(prompt).images[0]

    image_file = str(Path("app/files/image",
                          "image_" + str(int(time.time())) + ".png").absolute())
    image.save(image_file)
    return image_file


if __name__ == '__main__':
    image = sculpture("A cat standing on the groud,watching the star river over his head.")
    image.save("test.png")
