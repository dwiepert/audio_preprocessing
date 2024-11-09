import torchaudio

class ResampleAudio(object):
    '''
    Resample a waveform
    :param resample_rate: rate to resample to
    '''
    def __init__(self, resample_rate: int = 16000):
        
        self.resample_rate = resample_rate
        
    def __call__(self, sample):    
        waveform, sample_rate = sample['waveform'], sample['sample_rate']
        if sample_rate != self.resample_rate:
            transformed = torchaudio.transforms.Resample(sample_rate, self.resample_rate)(waveform)
            sample['waveform'] = transformed
            sample['sample_rate'] = self.resample_rate
        
        return sample