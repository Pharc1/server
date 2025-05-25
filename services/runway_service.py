import logging
import os
import time
from typing import List
from runwayml import RunwayML


logger = logging.getLogger(__name__)

class RunwayService:
    "servicr for generating with runway "
    def __init__(self):
        self.api_key = os.getenv("RUNWAY_APi_KEY")
        if self.api_key:
            logger.info("Runway API key founded")
        else:
            logger.info("no Runway api key founded")
        self.client = RunwayML(api_key=self.api_key)

    async def generate_image(self, prompt: str, ref: List, size: str = "1080:1920") -> str:
        print(f"Generating image with prompt: {prompt}, size: {size}, reference images: {ref}")
        
        task_params = {
            'model': 'gen4_image',
            'ratio': size,
            'prompt_text': prompt[1000:] if len(prompt) > 1000 else prompt,
        }

        if ref:
            task_params['reference_images'] = ref

        task = self.client.text_to_image.create(**task_params)
        task_id = task.id

        # Poll the task until it's complete
        time.sleep(1)  # Wait for a second before polling
        task = self.client.tasks.retrieve(task_id)
        while task.status not in ['SUCCEEDED', 'FAILED']:
            time.sleep(1)  # Wait for a second before polling
            task = self.client.tasks.retrieve(task_id)

        logger.info('Task complete:', task)
        if not task.output:
            raise ValueError(f"Task failed or returned no output! Status: {task.status}, ID: {task.id}")

        print(f'Image URL for prompt {prompt}: ', task.output[0])
        return task.output[0]