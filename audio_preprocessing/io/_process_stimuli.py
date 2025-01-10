"""
Process stimuli

Author(s): Aditya Vaidya, Daniela Wiepert
Last modified: 10/31/2024
"""
#IMPORTS
##built-in
import re
import shutil
import tempfile
import os
from pathlib import Path
from typing import List,Dict,Union

##third-party
import torch
import torchvision
from tqdm import tqdm

#local
from audio_preprocessing.transforms import *
from database_utils.functions import get_stimulus_interface, download_stimulus, get_stimulus_by_name

def process_stimuli(out_dir:Union[str,Path], stim_bucket:str, transforms:Dict, stories: List[str], story_paths: List[Union[str,Path]] = None):
    """
    Process stimuli

    :param out_dir: str, directory to save processed stimuli to
    :param stim_bucket: str, name of corral bucket containing stimulus
    :param transforms: Dict containing transforms to run and the required arguments
    :param stories: list of stories to process
    :param story_paths: list of story paths (None if loading from corral)
    :return None: saves processed files to out_dir
    """
    download_audio = stim_bucket is not None
    audio_transforms = _get_transforms(transforms)

    if download_audio:
        orig_stimulus_dir = Path(tempfile.mkdtemp())
        cci = get_stimulus_interface(stim_bucket)

    processed_stimulus_dir = Path(out_dir)
    processed_stimulus_dir.mkdir(exist_ok=True)
    print('dir', processed_stimulus_dir, 'exists?', processed_stimulus_dir.exists())


    for story in tqdm(stories, 'Processing stories'):
        if download_audio:
            orig_wav_path = _process_from_bucket(story, orig_stimulus_dir, cci)
        else:
            orig_wav_path = story_paths[story]
        
        out_wav_path = processed_stimulus_dir / f'{story}.flac'
        # Make the necessary dirs for the processed stimulus
        os.makedirs(out_wav_path.parent, exist_ok=True)
        #out_wav_path.parent.mkdir(exist_ok=True)
        
        sample = {'path': orig_wav_path, 'out_path': out_wav_path}
        
        audio_transforms(sample)

        if download_audio:
            orig_wav_path.unlink()

    if download_audio:
        shutil.rmtree(orig_stimulus_dir)
        
    return None

def _process_from_bucket(story:str, orig_stimulus_dir:Union[Path, str], cci):
    """
    Process stimuli from corral
    :param story: str, story to process
    :param orig_stimulus_dir: Path or str, directory for unprocessed stimuli
    :param cci: cotton candy interface for the stimulus bucket in corral
    :return orig_wav_path: Path, path to wav where stimulus has been downloaded to
    """
    part_regex_search = re.search('^(?P<base_story_name>.*)part(?P<part_num>[0-9]+)', story)
    if part_regex_search is None:
        part_idx = 0
        base_story_name = story
    else:
        part_idx = int(part_regex_search.groupdict()['part_num']) - 1
        base_story_name = part_regex_search.groupdict()['base_story_name']

    stimulus_data = get_stimulus_by_name(base_story_name)
    wav_remote_path = stimulus_data['segments'][part_idx]['formats']['wav']
    orig_wav_path = orig_stimulus_dir.absolute() / f'{story}.wav'

    download_stimulus(wav_remote_path, orig_wav_path, cci)

    return orig_wav_path

def _get_transforms(transforms:Dict):
    """
    Set up transforms for audio

    :param transforms: Dict containing transforms to run and the required arguments
    :return: composed transform list
    """
    transform_list = [Path2Wave()]
    if 'monochannel' in transforms:
        channel_sum = lambda w: torch.sum(w, axis = 0).unsqueeze(0)
        mono_tfm = ToMonophonic(reduce_fn=channel_sum)
        transform_list.append(mono_tfm)
    if 'resample' in transforms:
        resample_rate = transforms['resample']['resample_rate']
        downsample_tfm = ResampleAudio(resample_rate=resample_rate)
        transform_list.append(downsample_tfm)
    if 'trim' in transforms:
        trim_level = transforms['trim']['trim_level']
        trim_tfm = TrimSilence(threshold = trim_level)
        transform_list.append(trim_tfm)
    if 'truncate' in transforms: #160000
        clip_length = transforms['truncate']['clip_length']
        offset = transforms['truncate']['offset']
        truncate_tfm = Truncate(length = clip_length, offset=offset)
        transform_list.append(truncate_tfm)
    if 'wavemean' in transforms:
        transform_list.append(WaveMean())
    transform_list.append(Wave2File(transforms['format']))
    
    return torchvision.transforms.Compose(transform_list)

    
    