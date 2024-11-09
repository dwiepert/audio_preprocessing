# Audio Preprocessing
Package to perform preprocessing on audio stimuli.

## Setup
To install, use

```
$ git clone https://github.com/dwiepert/audio_preprocessing.git
$ cd audio_preprocessing
$ pip install . 
```

Additionally install ffmpeg=6.1.1.

The dependency environment is also specified in environment.yml (excluding local dependencies)


A major dependency of this package is the local package 'database_utils'. This can be found at [database_utils][https://github.com/dwiepert/database_utils]. Install this and ensure that it is either run on a computer with access to corral (through cotton candy) or use an ssh tunnel by running the following in your local terminal ```ssh -L 5000:127.0.0.1:5000 USERNAME@COMPUTER.biosci/cs.utexas.edu```

## Functions
### audio_preprocessing.io
`load_stimuli(stim_bucket:str, sessions:List[str]=None, stories:List[str]=None,recursive:bool=False, in_dir:str=None)`
Load stimulus from corral bucket or local directory
    :param stim_bucket: str, name of corral bucket containing stimulus
    :param sessions: List[str], list of session numbers to load in string format (e.g. '1')
    :param stories: List[str], list of stories to load (e.g. 'legacy')
    :param recursive: bool, boolean indicating whether to recursively find wav paths in a local directory
    :param in_dir: str, path to local dir with stimulus files. stim_bucket must be None to use this. Otherwise defaults to loading from corral
    :return stories: list of stories to process
    :return story_paths: list of story paths (None if loading from corral)

`process_stimuli(out_dir:str, stim_bucket:str, transforms:Dict, stories: List[str], story_paths: List[str] = None)`
Process stimuli

    :param out_dir: str, directory to save processed stimuli to
    :param stim_bucket: str, name of corral bucket containing stimulus
    :param transforms: Dict containing transforms to run and the required arguments
    :param stories: list of stories to process
    :param story_paths: list of story paths (None if loading from corral)
    :return None: saves processed files to out_dir

`select_stimuli(stim_dir:str, stim_bucket:str, sessions:List[str]=None, stories:List[str]=None,recursive:bool=False, custom_stimuli:str=None)`
Select stimulus from corral bucket or local directory

    :param stim_dir: str, directory with processed stimulus
    :param stim_bucket: str, name of corral bucket containing stimulus
    :param sessions: List[str], list of session numbers to load in string format (e.g. '1')
    :param stories: List[str], list of stories to load (e.g. 'legacy')
    :param recursive: bool, boolean indicating whether to recursively find wav paths in a local directory
    :return: paths to selected stories as a Dict

### audio_preprocessing.transforms
Includes a number of transform classes for processing audio. These can be used in combination with `torchvision.transforms.Compose` that takes in a list of initialized transforms and takes in an audio sample stored in a dictionary. 

See each class to see what is expected in the sample dictionary. Common:
* path: path to waveform to load
* waveform: loaded waveform
* sample_rate

These transforms can convert to monochannel, pad audio, load a waveform from a pat, resample audio, trim silence with torchaudio VAD, truncate audio, perform wav mean, generate windows on the audio, and save the waveform to a file. 
* ToMonophonic: convert to monochannel. Takes in a function used to reduce (see example of reduce_fn in `_process_stimuli`). Call requires a sample with 'waveform'. 
* PadSilence: pad silence based on context size (in seconds). Call requires a smple with 'waveform' and 'sample_rate'. If you want to remove padding, the sample must include a list of 'times'.
* Path2Wave: No initialization parameters. Will load a waveform if given a sample with 'path' specified 
* Resample: Initialize with target sample rate. Takes in a sample that has 'waveform' and 'sample_rate' specified
* TrimSilence: Initialize with silence threshold (trigger level). Call requires a sample with 'waveform' and 'sample_rate'.
* Truncate: Initialize with target clip length and offset. Call requires a sample with 'waveform' and 'sample_rate'.
* Wave2File: Initialize with desired output format. Sample should have a specified 'out_path', 'waveform', and 'sample_rate'.
* WaveMean: Perform wave mean normalization on a sample with 'waveform'.
* Window: See audio_preprocessng.transforms._window.py for initialization details. This will generate windows based on a context size and chunk size. 

## Using this package
See `run_initial_preprocessing.py` for using these functions to process stimuli. You can set what preprocessing transforms in a config.json (see `audio_preprocessing.configs` for example). This config should include the initialization parameters for each processing step you want run. 