#!/usr/bin/env python3
"""
Knowledge Graph Dataset Downloader
Downloads NELL-995 and FB15k-237 datasets for membership inference experiments.
HealthKG requires manual preprocessing (see data/README.md).
"""

import os
import argparse
import urllib.request
import zipfile
import sys
from pathlib import Path

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

class DownloadProgressBar:
    def __init__(self, desc="Downloading"):
        self.desc = desc
        self.last_percent = 0
        
    def update_to(self, count, block_size, total_size):
        if total_size > 0:
            percent = int(count * block_size * 100 / total_size)
            if percent != self.last_percent and percent % 10 == 0:
                print(f"{self.desc}... {percent}%")
                self.last_percent = percent

def download_file(url, output_path, desc="Downloading"):
    print(f"📥 {desc}")
    
    if TQDM_AVAILABLE:
        response = urllib.request.urlopen(url)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f, tqdm(
            total=total_size, unit='B', unit_scale=True,
            desc=os.path.basename(output_path)
        ) as pbar:
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                f.write(chunk)
                pbar.update(len(chunk))
    else:
        progress = DownloadProgressBar(desc)
        urllib.request.urlretrieve(url, output_path, reporthook=progress.update_to)
    
    print(f"   ✓ Downloaded\n")

def download_nell(data_dir):
    print("\n" + "="*70)
    print("📦 Downloading NELL-995 Dataset")
    print("="*70)
    
    nell_dir = os.path.join(data_dir, 'NELL')
    os.makedirs(nell_dir, exist_ok=True)
    
    expected_files = ['train.txt', 'valid.txt', 'test.txt']
    if all(os.path.exists(os.path.join(nell_dir, f)) for f in expected_files):
        print("✓ NELL-995 already exists")
        return True
    
    try:
        from datasets import load_dataset
        
        print("📥 Loading from HuggingFace (CleverThis/nell-995)...")
        dataset = load_dataset("CleverThis/nell-995")
        
        data = dataset["data"]
        triples = [(row["subject"], row["predicate"], row["object"]) for row in data]
        
        n = len(triples)
        splits = {
            'train.txt': triples[:int(n*0.8)],
            'valid.txt': triples[int(n*0.8):int(n*0.9)],
            'test.txt': triples[int(n*0.9):]
        }
        
        for filename, data in splits.items():
            path = os.path.join(nell_dir, filename)
            with open(path, 'w', encoding='utf-8') as f:
                for h, r, t in data:
                    f.write(f"{h}\t{r}\t{t}\n")
            print(f"💾 Saved {len(data):,} triples to {filename}")
        
        print("✅ NELL-995 downloaded successfully!")
        return True
        
    except ImportError:
        print("❌ 'datasets' library required")
        print("   Install: pip install datasets")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def download_fb15k237(data_dir):
    print("\n" + "="*70)
    print("📦 Downloading FB15k-237 Dataset")
    print("="*70)
    
    fb_dir = os.path.join(data_dir, 'FB15k-237')
    os.makedirs(fb_dir, exist_ok=True)
    
    expected_files = ['train.txt', 'valid.txt', 'test.txt']
    if all(os.path.exists(os.path.join(fb_dir, f)) for f in expected_files):
        print("✓ FB15k-237 already exists")
        return True
    
    url = "https://download.microsoft.com/download/8/7/0/8700516A-AB3D-4850-B4BB-805C515AECE1/FB15k-237.2.zip"
    zip_path = os.path.join(data_dir, "FB15k-237.zip")
    
    try:
        download_file(url, zip_path, "Downloading FB15k-237")
        
        print("📦 Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(data_dir)
        
        release_dir = os.path.join(data_dir, 'Release')
        if os.path.exists(release_dir):
            import shutil
            for item in os.listdir(release_dir):
                shutil.move(os.path.join(release_dir, item), 
                          os.path.join(fb_dir, item))
            shutil.rmtree(release_dir)
        
        os.remove(zip_path)
        print("✅ FB15k-237 downloaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def is_running_in_notebook():
    try:
        from IPython import get_ipython
        return get_ipython() is not None
    except:
        return False

def main():
    if is_running_in_notebook():
        filtered_argv = []
        skip_next = False
        for i, arg in enumerate(sys.argv):
            if skip_next:
                skip_next = False
                continue
            if arg == '-f':
                skip_next = True
                continue
            if 'kernel-' in str(arg) and '.json' in str(arg):
                continue
            filtered_argv.append(arg)
        sys.argv = filtered_argv
        if len(sys.argv) == 1:
            sys.argv.append('--all')
    
    parser = argparse.ArgumentParser(description='Download KG datasets')
    parser.add_argument('--dataset', choices=['NELL', 'FB15k-237'])
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--data_dir', default='./raw')
    
    args = parser.parse_args()
    
    if not args.all and not args.dataset:
        parser.error("Specify --all or --dataset")
    
    print("\n" + "="*70)
    print("  KNOWLEDGE GRAPH DATASET DOWNLOADER")
    print("="*70)
    
    os.makedirs(args.data_dir, exist_ok=True)
    
    results = {}
    if args.all:
        results['NELL'] = download_nell(args.data_dir)
        results['FB15k-237'] = download_fb15k237(args.data_dir)
    elif args.dataset == 'NELL':
        results['NELL'] = download_nell(args.data_dir)
    elif args.dataset == 'FB15k-237':
        results['FB15k-237'] = download_fb15k237(args.data_dir)
    
    print("\n" + "="*70)
    print(f"✅ {sum(results.values())}/{len(results)} datasets downloaded")
    print("="*70)
    print("\n📝 For HealthKG: See data/README.md\n")

if __name__ == '__main__':
    main()