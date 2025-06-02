import asyncio
import base64
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List
import logging
from runwayml import RunwayML
import os

logger = logging.getLogger(__name__)

def get_base64_image(image_path: str) -> str:
        with open(image_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/png;base64,{base64_image}"

class RunwayService:

    def __init__(self, ):
        self.api_key = os.getenv("RUNWAY_APi_KEY")
        if self.api_key:
            logger.info("Runway API key founded")
        else:
            logger.info("no Runway api key founded")
        self.client = RunwayML(api_key=self.api_key)
        self.executor = ThreadPoolExecutor()

    async def generate_image(self, prompt: str, ref: List, size: str = "1080:1920") -> str:
        print(f"Generating image with prompt: {prompt}, size: {size}, reference images: {ref}")
        
        task_params = {
            'model': 'gen4_image',
            'ratio': size,
            'prompt_text': prompt[1000:] if len(prompt) > 1000 else prompt,
            'reference_images': [
                {
                    'uri': get_base64_image('static\\images\\style.png')
                }
            ]
        }

        if ref and "@" in prompt:
            task_params['reference_images'] = ref

        def blocking_runway_task():
            task = self.client.text_to_image.create(**task_params)
            task_id = task.id
            time.sleep(1)  # first pause
            task = self.client.tasks.retrieve(task_id)
            while task.status not in ['SUCCEEDED', 'FAILED']:
                time.sleep(1)
                task = self.client.tasks.retrieve(task_id)
            return task

        task = await asyncio.get_event_loop().run_in_executor(self.executor, blocking_runway_task)

        logger.info('Task complete: %s', task)
        if not task.output:
            raise ValueError(f"Task failed or returned no output! Status: {task.status}, ID: {task.id}")

        print(f'Image URL for prompt {prompt}: ', task.output[0])
        return task.output[0]