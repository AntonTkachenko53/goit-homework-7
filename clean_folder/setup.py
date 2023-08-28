from setuptools import setup, find_packages

setup(name='clean_folder',
      version='0.0.1',
      packages=find_packages(),
      author='AntonTkachenko',
      description='clean your folder by sorting files',
      entry_points={
          'console_scripts': ['clean-folder = clean_folder.clean:main']


      }


)