import time
from runwayml import RunwayML

client = RunwayML()

task = client.text_to_image.create(
  model='gen4_image',
  ratio='1080:1920',
  prompt_text='@EiffelTower painted in the style of @StarryNight',
  reference_images=[{
    'uri': 'https://upload.wikimedia.org/wikipedia/commons/8/85/Tour_Eiffel_Wikimedia_Commons_(cropped).jpg',
    'tag': 'EiffelTower',
  },
  {
    'uri': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1513px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg',
    'tag': 'StarryNight',
  }],
)
task_id = task.id

# Poll the task until it's complete
time.sleep(1)  # Wait for a second before polling
task = client.tasks.retrieve(task_id)
while task.status not in ['SUCCEEDED', 'FAILED']:
  time.sleep(1)  # Wait for a second before polling
  task = client.tasks.retrieve(task_id)

print('Task complete:', task)
print('Image URL': task.output[0])