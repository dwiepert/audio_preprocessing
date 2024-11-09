import torchaudio.functional as taf
import torchaudio.sox_effects as tase
import torch

class TrimSilence:
    """
    Trim beginning and end silence
    :param threshold: trigger level (torchaudio)

    """
    def __init__(self, threshold: int = 60):
        self.threshold = threshold
    
    def __call__(self, sample):
        waveform = sample['waveform']
        sr = sample['sample_rate']
        beg_trim = taf.vad(waveform, sample_rate=sr, trigger_level=self.threshold)
        if beg_trim.nelement() == 0:
            print('Waveform may be empty. Currently skipping trimming. See TrimBeginningEndSilence for more information.')
            out_waveform = waveform 
        else:
            rev = torch.flip(beg_trim, [0,1])
            #rev, sr = tase.apply_effects_tensor(beg_trim, sample_rate=sr, effects=[['reverse']])
            
            end_trim = taf.vad(rev, sample_rate=sr, trigger_level=self.threshold)
            if end_trim.nelement() == 0:
                print('Waveform may be empty. Currently ignoring. See TrimBeginningEndSilence for more information.')
                out_waveform = waveform 
            else:
                out_waveform = torch.flip(end_trim, [0,1])#tase.apply_effects_tensor(end_trim, sample_rate=sr, effects=[['reverse']])
            
        sample['waveform'] = out_waveform

        return sample