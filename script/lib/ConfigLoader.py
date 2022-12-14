import json
import os


class ConfigLoader:
  def __init__(self, dir, filenames):
    self.config = {}
    for filename in filenames:
      filename_path = os.path.join(dir, filename)
      if not os.path.exists(filename_path):
        try:
          print(filename, 'does not exist')
          with open(filename_path, 'w'): pass
          print(filename, 'created in', dir)
        except Exception as e:
          print('Config error:', e)
          continue

      with open(filename_path, 'r') as config_file:
        try:
          self.config[os.path.splitext(os.path.basename(filename))[0]] = json.load(config_file)
        except Exception as e:
          print('Config error on loading config:' , e)
