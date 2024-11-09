"""
Download stimuli from corral or find path names of stimuli in local directory

Author(s): Aditya Vaidya, Daniela Wiepert
Last modified: 10/31/2024
"""
#IMPORTS
##built-in
from pathlib import Path
from typing import List, Union

##local
from database_utils.functions import sess_to_story, get_stimulus_interface, get_all_stim_names

def load_stimuli(stim_bucket:str, sessions:List[str]=None, stories:List[str]=None,recursive:bool=False, in_dir:Union[str,Path]=None):
    """
    Load stimulus from corral bucket or local directory

    :param stim_bucket: str, name of corral bucket containing stimulus
    :param sessions: List[str], list of session numbers to load in string format (e.g. '1')
    :param stories: List[str], list of stories to load (e.g. 'legacy')
    :param recursive: bool, boolean indicating whether to recursively find wav paths in a local directory
    :param in_dir: str, path to local dir with stimulus files. stim_bucket must be None to use this. Otherwise defaults to loading from corral
    :return stories: list of stories to process
    :return story_paths: list of story paths (None if loading from corral)
    """
    download_audio = stim_bucket is not None
    if download_audio:
        stories = _load_from_bucket(stim_bucket, sessions, stories)
        return stories, None
    else:
        assert in_dir is not None, 'Must give either stimulus bucket for accessing corral stimulus or a path containining stimulus'
        stories, story_paths = _load_from_dir(in_dir, sessions, stories, recursive)
        return stories, story_paths

def _load_from_bucket(stim_bucket:str, sessions:List[str]=None, stories:List[str]=None):
    """
    Loading steps if using corrall. Only one of sessions or stories can be specified

    :param stim_bucket: str, name of corral bucket containing stimulus
    :param sessions: List[str], list of session numbers to load in string format (e.g. '1')
    :param stories: List[str], list of stories to load (e.g. 'legacy')
    :return stories: List[str], list of stories to process
    """
    cci = get_stimulus_interface(stim_bucket)

    assert (stories is None) != (sessions is None), "exactly one of these must be specified!"

    if stories is not None:
        stories = set(stories)
    else:
        stories = set()
        for s in sessions:
            ssd = sess_to_story(cci)
            train_stories, test_story = ssd[s]
            stories.add(test_story)
            for story in train_stories:
                stories.add(story)
    
    if len(stories) == 0:
        stories = set(get_all_stim_names())
    return stories

def _load_from_dir(in_dir:Union[str,Path], stories:List[str], recursive:bool):
    """
    Load stimuli from a local directory
    
    :param in_dir: str, path to local dir with stimulus files. stim_bucket must be None to use this. Otherwise defaults to loading from corral
    :param stories: List[str], list of stories to load (e.g. 'legacy')
    :param recursive: bool, boolean indicating whether to recursively find wav paths in a local directory
    :return stories: List[str], list of stories to process
    :return story_paths: list of story paths 
    """
    in_dir = Path(in_dir)
    assert in_dir.exists()

    if recursive:
        story_paths = sorted(list(in_dir.rglob('*.wav')))
    else:
        story_paths = sorted(list(in_dir.glob('*.wav')))
    
    # Strip the extension to get the "name" of the stimulus, and make it
    # relative to the stimulus directory
    stories = [str(x.relative_to(in_dir).with_suffix('')) for x in story_paths]
    story_paths = dict(zip(stories, story_paths))
    print(story_paths)

    return stories, story_paths
