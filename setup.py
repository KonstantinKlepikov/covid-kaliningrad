from setuptools import setup
from os.path import join, dirname
import main

with open(join(dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='covid-kaliningrad',
      version = main.__version__,
      description = 'Covid-kaliningrad',
      long_description = long_description,
      ong_description_content_type='text/markdown',
      packages = ['covid-kaliningrad'],
      author = 'Konstantin Klepikov',
      author_email = 'oformleno@gmail.com',
      download_url = 'https://github.com/KonstantinKlepikov/covid-kaliningrad',
      license = 'MIT',
      zip_safe = False)
