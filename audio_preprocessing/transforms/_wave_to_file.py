import torchaudio
import os
class Wave2File:
    """
    Save audio file
    :param format: str, output format type
    """
    def __init__(self, format:str='flac'):
        self.format = format

    def __call__(self, sample):
        assert os.path.splitext(str(sample['out_path']))[1][1:] == self.format
        torchaudio.save(uri=str(sample['out_path']), src=sample['waveform'], sample_rate=sample['sample_rate'], format=self.format)