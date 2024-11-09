import torch 

class PadSilence:
    def __init__(self, context_sz):
        self.context_sz = context_sz

    def __call__(self, sample):
        sr = sample['sample_rate']
        wav = sample['waveform']
        wav = torch.cat([torch.zeros(int(self.context_sz*sr)), wav], axis=0)
        sample['waveform'] = wav
        return sample

    def remove_padding(self, sample):
        times = sample['times']
        times = torch.clip(times - self.context_sz, 0, torch.inf)
        assert torch.all(times >= 0), "padding is smaller than the correction (subtraction)!"
        assert torch.all(times[:,1] > 0), f"insufficient padding for require_full_context ! (times[times[:,1]<=0,1])"
        sample['times'] = times
        return sample