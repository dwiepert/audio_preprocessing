from audio_preprocessing.transforms import Path2Wave, Window, ResampleAudio

wavfile = "/Users/dwiepert/Documents/GitHub/audio_preprocessing/gettysburg.wav"
sample = {}
sample['path'] = wavfile
load = Path2Wave()
sample = load(sample)

resample = ResampleAudio(resample_rate=16000)
sample = resample(sample)

window = Window(chunksz=0.1,  contextsz=1, batchsz=1, sampling_rate=16000, skip_window=True)
sample = window(sample)

for x in sample['snippet_iter']:
    print('pause')
print('pause')