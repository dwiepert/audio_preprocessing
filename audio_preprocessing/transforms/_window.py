import torch
class Window:
    def __init__(self, chunksz:float=0.1, contextsz:float=8., batchsz:int=1, sampling_rate:int=16000,require_full_context:bool=True, min_length_samples:float=0, skip_window:bool=False):
        self.sampling_rate=sampling_rate
        self.chunksz=chunksz
        self.chunksz_samples = int(self.chunksz*self.sampling_rate)
        self.contextsz=contextsz
        self.contextsz_samples = int(self.contextsz*self.sampling_rate)
        self.require_full_context=require_full_context
        self.min_length_samples = min_length_samples
        self.skip_window = skip_window
        if self.skip_window:
            self.batchsz = 1
        else:
            self.batchsz = batchsz 

    def __call__(self, sample):
        wav = torch.squeeze(sample['waveform'])
        sr = sample['sample_rate']
        assert sample['sample_rate'] == self.sampling_rate, f'Sample rate {sr} is incompatible with this transform. Resample to {self.sampling_rate}.'
        
        snippet_ends = []

        if not self.skip_window:
            if not self.require_full_context:
                # Add all snippets that are _less_ than the total input size
                # (context+chunk)
                snippet_ends.append(torch.arange(self.chunksz_samples, self.contextsz_samples+self.chunksz_samples, self.chunksz_samples))
            
            # Add all snippets that are exactly the length of the requested input
            # (`Tensor.unfold` is basically a sliding window).
            if wav.shape[0] >= self.chunksz_samples+self.contextsz_samples:
                # `unfold` fails if `wav.shape[0]` is less than the window size.
                snippet_ends.append(
                    torch.arange(wav.shape[0]).unfold(0, self.chunksz_samples+self.contextsz_samples, self.chunksz_samples)[:,-1]+1
                )
        else:
            snippet_ends.append(torch.tensor([wav.shape[0]]))
        
        if snippet_ends == []:
            raise ValueError(f"No snippets possible! Stimulus is probably too short ({wav.shape[0]} samples). Consider reducing context size or setting `require_full_context=True`")

        snippet_ends = torch.cat(snippet_ends, dim=0) # shape: (num_snippets,)
        # 2-D array where `[i,0]` and `[i,1]` are the start and end, respectively,
        # of snippet `i` in samples. Shape: (num_snippets, 2)

        if not self.skip_window:
            snippet_times = torch.stack([torch.maximum(torch.zeros_like(snippet_ends),
                                                    snippet_ends-(self.contextsz_samples+self.chunksz_samples)),
                                        snippet_ends], dim=1)
        else:
            snippet_times = torch.stack([torch.tensor([0]),snippet_ends],dim=1)

        snippet_times = snippet_times[(snippet_times[:,1] - snippet_times[:,0]) >= self.min_length_samples]
        snippet_times_sec = snippet_times / self.sampling_rate # snippet_times, but in sec.
        sample['snippet_times'] = snippet_times
        sample['snippet_times_sec'] = snippet_times_sec

        #assert (frames_per_chunk % frame_skip) == 0, "These must be divisible"

        snippet_length_samples = snippet_times[:,1] - snippet_times[:,0] # shape: (num_snippets,)
        if self.require_full_context:
            assert all(snippet_length_samples == snippet_length_samples[0]), "uneven snippet lengths!"
            snippet_length_samples = snippet_length_samples[0]
            assert snippet_length_samples.ndim == 0

        #create snippet batchets
        if self.require_full_context or self.skip_window:
        # This case is simpler, so handle it explicitly
            snippet_batches = snippet_times.T.split(self.batchsz, dim=1)
        else:
            # First, batch the snippets that are of different lengths.
            snippet_batches = snippet_times.tensor_split(torch.where(snippet_length_samples.diff() != 0)[0]+1, dim=0)
            # Then, split any batches that are too big to fit into the given
            # batch size.
            snippet_iter = []
            for batch in snippet_batches:
                # split, *then* transpose
                if batch.shape[0] > self.batchsz:
                    snippet_iter += batch.T.split(self.batchsz,dim=1)
                else:
                    snippet_iter += [batch.T]
            snippet_batches = snippet_iter

        snippet_iter = snippet_batches

        sample['snippet_iter'] = snippet_batches
        sample['waveform'] = wav
        
        return sample