"""
Select stimulus to use for downstream tasks

Author(s): Aditya Vaidya, Daniela Wiepert
Last modified: 11/04/2024
"""
#IMPORTS
##built-in
import itertools
from pathlib import Path
from typing import List,Dict,Union

##local
from database_utils.functions import sess_to_story, get_stimulus_interface, get_all_stim_names

def select_stimuli(stim_dir:Union[str,Path], stim_bucket:str, sessions:List[str]=None, stories:List[str]=None,recursive:bool=False):
    """
    Select stimulus from corral bucket or local directory

    :param stim_dir: str, directory with processed stimulus
    :param stim_bucket: str, name of corral bucket containing stimulus
    :param sessions: List[str], list of session numbers to load in string format (e.g. '1')
    :param stories: List[str], list of stories to load (e.g. 'legacy')
    :param recursive: bool, boolean indicating whether to recursively find wav paths in a local directory
    :return: paths to selected stories as a Dict
    """
    # Using CLI arguments, find stimuli and their locations.
    select_from_bucket = stim_bucket is not None
    stim_dir = Path(stim_dir)
    assert stim_dir.exists(), f"Stimulus dir {str(stim_dir)} does not exist"
    assert stim_dir.is_dir(), f"Stimulus dir {str(stim_dir)} is not a directory"

    if select_from_bucket:
        return _select_from_bucket(stim_dir, stim_bucket, sessions, stories)
    else:
        return _select_from_dir(stim_dir, recursive)


def _select_from_bucket(stim_dir:Union[str,Path], stim_bucket:str, sessions:List[str]=None, stories:List[str]=None):
    """
    Select stimulus from corral bucket 

    :param stim_dir: str, directory with processed stimulus
    :param stim_bucket: str, name of corral bucket containing stimulus
    :param sessions: List[str], list of session numbers to load in string format (e.g. '1')
    :param stories: List[str], list of stories to load (e.g. 'legacy')
    """
    if stories is not None:
        stories = set(stories)
    else:
        assert sessions is not None
        stories = set()
        for s in sessions:
            cci = get_stimulus_interface(stim_bucket)
            ssd = sess_to_story(cci)
            train_stories, test_story = ssd[s]
            stories.add(test_story)
            for story in train_stories:
                stories.add(story)
    
    stimulus_paths: Dict[str, Path] = {} # map of stimulus name --> file path. We also use this as the list of stimuli
    for story in stories:
            # Find the associated sound file for each stimulus.
            # First extension found is preferred.
            for ext in ['flac', 'wav']:
                stimulus_path = stim_dir / f"{story}.{ext}"
                if stimulus_path.exists() and stimulus_path.is_file():
                    stimulus_paths[story] = stimulus_path
                    break
    missing_stories = set(stories).difference(set(stimulus_paths.keys()))
    if len(missing_stories) > 0:
        raise RuntimeError(f"missing stimuli for stories: " + ' '.join(missing_stories))

    return stimulus_paths

def _select_from_dir(stim_dir:Union[str,Path], recursive:bool):
    """
    Select stimulus from directory
    :param stim_dir: str, directory with processed stimulus
    :param recursive: bool, boolean indicating whether to recursively find wav paths in a local directory
    """
    stimulus_paths: Dict[str, Path] = {} # map of stimulus name --> file path. We also use this as the list of stimuli

    if recursive:
        stimulus_glob_wav_iter = stim_dir.rglob('*.wav')
        stimulus_glob_flac_iter = stim_dir.rglob('*.flac')
    else:
        stimulus_glob_wav_iter = stim_dir.glob('*.wav')
        stimulus_glob_flac_iter = stim_dir.glob('*.flac')

    for stimulus_path in itertools.chain(stimulus_glob_wav_iter, stimulus_glob_flac_iter):
        # Use 'relative_to' to preserve directory structure when using
        # --recursive
        stimulus_name = str(stimulus_path.relative_to(stim_dir).with_suffix(''))
        # If stimulus already exists, overwrite the path with the
        # most recent extension
        stimulus_paths[stimulus_name] = stimulus_path
    return stimulus_paths