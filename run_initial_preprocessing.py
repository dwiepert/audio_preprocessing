import argparse
import json

from audio_preprocessing.io import load_stimuli, select_stimuli, process_stimuli

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=str, required=True)
    parser.add_argument("--transform_json", type=str, default='audio_preprocessing/configs/transform_config.json')
    parser.add_argument("--stim_bucket", default=None)
    parser.add_argument("--stories", nargs="+")
    parser.add_argument("--sessions", nargs="+", default=['1'])
    parser.add_argument("--recursive", action='store_true')
    parser.add_argument("--in_dir", default=None)
    args = parser.parse_args()

    
    #stimulus_paths = select_stimuli(stim_dir=args.outdir, stim_bucket=args.stim_bucket, sessions=args.sessions, stories=args.stories, recursive=args.recursive)
    stories, story_paths = load_stimuli(args.stim_bucket, args.sessions, args.stories, args.recursive, args.in_dir)
    
    with open(args.transform_json,'r') as f:
        transforms = json.load(f)

    process_stimuli(args.outdir, args.stim_bucket, transforms, stories, story_paths)