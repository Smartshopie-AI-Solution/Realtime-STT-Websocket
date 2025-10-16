'''
The setup.py file is essential part of the packaging and
distributing python projects. It is used by setuptools
(or distutils in older Python versions) to define the configuration
of your poject, such as its metadata, dependencies and more.
'''

from setuptools import setup, find_packages
from typing import List

def get_requirements()->List[str]:
    '''
    This function will return a list of requirements
    
    '''
    requirement_lst:List[str] = []
    try:
        with open('requirements.txt', 'r') as file:
            # Read lines from the file
            lines = file.readlines()
            # Process each line
            for line in lines:
                requirement = line.strip()
                # Ignore only lines and -e .
                if requirement and requirement!= '-e .':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print('No requirements.txt file found.')

    return requirement_lst

setup(
    name="realtime-stt-websocket",
    description="Real-time Speech-to-Text system with WebSocket streaming support",
    long_description="A real-time Speech-to-Text (STT) system that converts spoken language into written text instantly using WebSocket communication. Supports both Vosk and Hugging Face Whisper models for flexible speech recognition.",
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=get_requirements(),
    keywords="speech-to-text, real-time, websocket, vosk, whisper, transcription",
)