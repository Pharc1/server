import logging
import os
import time
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
        self.client = RunwayML()

    async def generate_image(prompt: str, ref: Dict[str, str], size: str = "1080:1920") -> str:

        task = self.client.text_to_image.create(
        model='gen4_image',
        ratio=size,
        prompt_text=prompt,
        reference_images=ref,
        )
        task_id = task.id

        # Poll the task until it's complete
        time.sleep(1)  # Wait for a second before polling
        task = self.client.tasks.retrieve(task_id)
        while task.status not in ['SUCCEEDED', 'FAILED']:
            time.sleep(1)  # Wait for a second before polling
            task = self.client.tasks.retrieve(task_id)

        logger.info('Task complete:', task)
        logger.info('Image URL: ', task.output[0])
        return task.output[0]