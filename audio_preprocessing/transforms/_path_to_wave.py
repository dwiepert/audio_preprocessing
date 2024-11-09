import torchaudio

class Path2Wave:
    """
    Load wav file
    """
    def __call__(self, sample):
        path = sample['path']
        wav, sr = torchaudio.load(path)
        sample['waveform'] = wav
        sample['sample_rate'] = sr
        return sample
        