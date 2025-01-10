from setuptools import setup, find_packages
from audio_preprocessing._version import __version__

setup(
    name = 'audio_preprocessing.py',
    packages = find_packages(),
    author = 'HuthLab',
    python_requires='>=3.8',
    install_requires=[
        'numpy==1.26.4',
        'ipdb==0.13.13',
        'cottoncandy==0.2.0',
        'torchaudio==2.2.2',
        'torchvision==0.17.2',
        'torch==2.2.2',
        'tqdm==4.66.5'
    ],
    include_package_data=False,  
    version = __version__,
)