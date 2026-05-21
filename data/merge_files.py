
"""
Usage:
    python merge_files.py --dataset NELL
    python merge_iles.py --dataset FB15k-237
    python merge_files.py --all
"""

import argparse
import os
from pathlib import Path
from collections import defaultdict

def merge_dataset(dataset_name, data_dir='./raw'):
    """Merge train/valid/test files into full_kg.tsv"""
    
    print(f"\n{'='*70}")
    print(f"📦 Merging {dataset_name}")
    print('='*70)
    
    dataset_path = os.path.join(data_dir, dataset_name)
    
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset directory not found: {dataset_path}")
        return False
    
    # Files to merge
    input_files = ['train.txt', 'valid.txt', 'test.txt']
    output_file = os.path.join(dataset_path, 'full_kg.tsv')
    
    # Check if output already exists
    if os.path.exists(output_file):
        response = input(f"⚠️  {output_file} already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("   Skipping merge")
            return True
    
    # Check input files exist
    missing_files = []
    for filename in input_files:
        filepath = os.path.join(dataset_path, filename)
        if not os.path.exists(filepath):
            missing_files.append(filename)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    # Merge files and remove duplicates
    print("\n📥 Reading files...")
    all_triples = set()  # Use set to automatically remove duplicates
    file_stats = {}
    
    for filename in input_files:
        filepath = os.path.join(dataset_path, filename)
        count = 0
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    all_triples.add(line)
                    count += 1
        
        file_stats[filename] = count
        print(f"  ├─ {filename}: {count:,} triples")
    
    print(f"  └─ Total before deduplication: {sum(file_stats.values()):,} triples")
    print(f"  └─ Total after deduplication: {len(all_triples):,} triples")
    
    duplicates = sum(file_stats.values()) - len(all_triples)
    if duplicates > 0:
        print(f"  ⚠️  Removed {duplicates:,} duplicate triples")
    
    # For NELL, clean the URIs
    if dataset_name == 'NELL':
        print("\n🧹 Cleaning NELL URIs...")
        print("   Removing http://nell.ml.cmu.edu/ prefixes...")
        cleaned_triples = set()
        invalid_count = 0
        
        for triple_line in all_triples:
            parts = triple_line.split('\t')
            if len(parts) == 3:
                # Extract clean identifiers
                head = parts[0].replace('http://nell.ml.cmu.edu/entity/', '')
                relation = parts[1].replace('http://nell.ml.cmu.edu/relation/', '')
                tail = parts[2].replace('http://nell.ml.cmu.edu/entity/', '')
                
                # Also remove http/https prefixes if any
                head = head.replace('http://', '').replace('https://', '')
                relation = relation.replace('http://', '').replace('https://', '')
                tail = tail.replace('http://', '').replace('https://', '')
                
                # Basic validation - skip obviously bad triples
                bad_patterns = ['use_resources_copyright', 'pakdirectory__net', '__']
                is_valid = True
                for pattern in bad_patterns:
                    if pattern in head.lower() or pattern in tail.lower():
                        is_valid = False
                        invalid_count += 1
                        break
                
                if is_valid and head and relation and tail:
                    cleaned_triples.add(f"{head}\t{relation}\t{tail}")
                elif not is_valid:
                    pass  # Already counted
                else:
                    invalid_count += 1
        
        all_triples = cleaned_triples
        print(f"  ├─ URIs cleaned")
        print(f"  ├─ Removed {invalid_count:,} invalid triples")
        print(f"  └─ Final count: {len(all_triples):,} clean triples")
    
    # Write merged file
    print(f"\n💾 Writing to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for triple in sorted(all_triples):  # Sort for consistency
            f.write(triple + '\n')
    
    print(f"✅ Merged successfully!")
    print(f"   Output: {output_file}")
    print(f"   Total triples: {len(all_triples):,}")
    
    # Verify the output
    print("\n🔍 Verifying output...")
    with open(output_file, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        parts = first_line.split('\t')
        
        if len(parts) == 3:
            print(f"   ✓ Format verified: tab-separated triples")
            # Truncate long identifiers for display
            h_display = parts[0][:40] + '...' if len(parts[0]) > 40 else parts[0]
            r_display = parts[1][:40] + '...' if len(parts[1]) > 40 else parts[1]
            t_display = parts[2][:40] + '...' if len(parts[2]) > 40 else parts[2]
            print(f"   ✓ Sample: {h_display} | {r_display} | {t_display}")
            
            if dataset_name == 'NELL':
                # Verify no URIs remain
                if 'http://' not in first_line and 'nell.ml.cmu.edu' not in first_line:
                    print(f"   ✓ NELL URIs successfully cleaned")
                else:
                    print(f"   ⚠️  Warning: Some URIs may remain")
        else:
            print(f"   ⚠️  Warning: Expected 3 columns, found {len(parts)}")
    
    return True

def analyze_statistics(dataset_name, data_dir='./raw'):
    """Analyze and display statistics about the merged dataset"""
    
    dataset_path = os.path.join(data_dir, dataset_name)
    full_kg_path = os.path.join(dataset_path, 'full_kg.tsv')
    
    if not os.path.exists(full_kg_path):
        print(f"⚠️  {full_kg_path} not found. Run merge first.")
        return
    
    print(f"\n{'='*70}")
    print(f"📊 Statistics for {dataset_name}")
    print('='*70)
    
    entities = set()
    relations = defaultdict(int)
    
    with open(full_kg_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 3:
                head, relation, tail = parts
                entities.add(head)
                entities.add(tail)
                relations[relation] += 1
    
    print(f"\n📈 Overview:")
    print(f"  ├─ Total triples: {sum(relations.values()):,}")
    print(f"  ├─ Unique entities: {len(entities):,}")
    print(f"  └─ Unique relations: {len(relations):,}")
    
    print(f"\n🔝 Top 10 most frequent relations:")
    sorted_relations = sorted(relations.items(), key=lambda x: x[1], reverse=True)
    for i, (relation, count) in enumerate(sorted_relations[:10], 1):
        # Truncate long relation names
        rel_display = relation[:50] + '...' if len(relation) > 50 else relation
        print(f"  {i:2d}. {rel_display:50s} : {count:>8,} triples")
    
    if len(relations) > 10:
        print(f"  ... and {len(relations) - 10} more relations")

def cleanup_original_files(dataset_name, data_dir='./raw'):
    """Optionally remove train/valid/test files after merging"""
    
    dataset_path = os.path.join(data_dir, dataset_name)
    files_to_remove = ['train.txt', 'valid.txt', 'test.txt']
    
    print(f"\n🗑️  Cleanup original split files?")
    print(f"   This will remove: {', '.join(files_to_remove)}")
    print(f"   You can regenerate them with your own split.py script")
    
    response = input(f"   Remove files? (y/n): ")
    
    if response.lower() == 'y':
        for filename in files_to_remove:
            filepath = os.path.join(dataset_path, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"  ✓ Removed {filename}")
        print("✅ Cleanup complete")
    else:
        print("  Keeping original files")

def main():
    parser = argparse.ArgumentParser(
        description='Merge train/valid/test into full_kg.tsv for custom splitting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Merge one dataset
  python merge_kg_files.py --dataset NELL
  
  # Merge all datasets
  python merge_kg_files.py --all
  
  # Merge and show statistics
  python merge_kg_files.py --dataset FB15k-237 --stats
  
  # Merge and cleanup original files
  python merge_kg_files.py --all --cleanup

NELL Cleaning:
  For NELL datasets, URIs are automatically cleaned:
  Before: http://nell.ml.cmu.edu/entity/concept:personus:anne_mccaffrey
  After:  concept:personus:anne_mccaffrey

Workflow:
  1. Download datasets: python download_datasets.py --all
  2. Merge files: python merge_kg_files.py --all
  3. Apply your split: python scripts/split.py --global_path data/raw/NELL/full_kg.tsv ...
        """
    )
    
    parser.add_argument(
        '--dataset',
        type=str,
        choices=['NELL', 'FB15k-237', 'HealthKG'],
        help='Dataset to merge'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Merge all datasets'
    )
    parser.add_argument(
        '--data_dir',
        type=str,
        default='./raw',
        help='Data directory (default: ./raw)'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show detailed statistics after merging'
    )
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Remove original train/valid/test files after merging'
    )
    
    args = parser.parse_args()
    
    if not args.all and not args.dataset:
        parser.error("Please specify --all or --dataset <name>")
    
    print("\n" + "="*70)
    print("  KNOWLEDGE GRAPH FILE MERGER")
    print("  Combines train/valid/test into full_kg.tsv")
    print("  (NELL: Automatically cleans URIs)")
    print("="*70)
    
    # Datasets to process
    if args.all:
        datasets = ['NELL', 'FB15k-237']
        # Check if HealthKG exists
        healthkg_path = os.path.join(args.data_dir, 'HealthKG', 'full_kg.tsv')
        if os.path.exists(healthkg_path):
            print("\nℹ️  HealthKG already has full_kg.tsv (from preprocessing)")
        else:
            print("\nℹ️  HealthKG not found (requires manual preprocessing)")
    else:
        if args.dataset == 'HealthKG':
            print("\n⚠️  HealthKG already produces full_kg.tsv from preprocessing")
            print("   No merging needed for HealthKG")
            return 0
        datasets = [args.dataset]
    
    # Process each dataset
    results = {}
    for dataset in datasets:
        success = merge_dataset(dataset, args.data_dir)
        results[dataset] = success
        
        if success and args.stats:
            analyze_statistics(dataset, args.data_dir)
        
        if success and args.cleanup:
            cleanup_original_files(dataset, args.data_dir)
    
    # Summary
    print("\n" + "="*70)
    print("📊 MERGE SUMMARY")
    print("="*70)
    
    for dataset, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {dataset}")
    
    success_count = sum(1 for v in results.values() if v)
    print(f"\n✅ {success_count}/{len(results)} datasets merged successfully")
    
    print("\n📝 Next steps:")
    print("   1. Use scripts/split.py to create your custom train/test splits")
    print("   2. Example:")
    print("      python scripts/split.py \\")
    print("        --global_path data/raw/NELL/full_kg.tsv \\")
    print("        --relation 'concept:teamplaysagainstteam' \\")
    print("        --outdir data/public/NELL/")
    print()

if __name__ == '__main__':
    main()