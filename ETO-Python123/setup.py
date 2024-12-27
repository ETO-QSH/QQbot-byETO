from distutils.core import setup
from setuptools import find_packages

with open("README.rst", "r", encoding='utf-8') as f:
  long_description = f.read()

setup(name='Python123ETO',  # 包名
      version='1.0.5',  # 版本号
      description='A small example package',
      long_description_content_type='text/markdown',
      long_description=long_description,
      author='ETO',
      author_email='2373204754@qq.com',
      url='https://github.com/ETO-QSH',
      install_requires=[],
      license='AGPL-3.0 License',
      packages=find_packages(),
      platforms=["all"],
      classifiers=[
        'Development Status :: 1 - Planning '
      ])
