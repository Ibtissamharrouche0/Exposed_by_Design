
"""
Dataset Validation Script
Validates the integrity and format of full_kg.tsv knowledge graph files.

Usage:
    python validate_data.py
    python validate_data.py --dataset NELL
    python validate_data.py --verbose
"""

import os
import sys
from pathlib import Path
from collections import defaultdict

# Expected dataset statistics for full_kg.tsv
EXPECTED_STATS = {
    'NELL': {
        'file': 'full_kg.tsv',
        'min_triples': 140000,
        'max_triples': 160000,
        'format': 'tsv',
        'description': 'NELL-995 full knowledge graph'
    },
    'FB15k-237': {
        'file': 'full_kg.tsv',
        'min_triples': 300000,
        'max_triples': 320000,
        'format': 'tsv',
        'description': 'FB15k-237 full knowledge graph'
    },
    'HealthKG': {
        'file': 'full_kg.tsv',
        'min_triples': 40000,
        'max_triples': 60000,
        'format': 'tsv',
        'description': 'HealthKG full knowledge graph'
    }
}

def validate_triple_format(line, line_num, filename):
    """Validate that a line is a proper tab-separated triple"""
    parts = line.strip().split('\t')
    
    if len(parts) != 3:
        return False, f"Line {line_num}: Expected 3 parts (head\trelation\ttail), got {len(parts)}"
    
    head, relation, tail = parts
    
    # Check for empty fields
    if not head or not relation or not tail:
        return False, f"Line {line_num}: Empty field detected"
    
    # Check if it looks like a URI (shouldn't be for cleaned data)
    if 'http://' in head or 'http://' in relation or 'http://' in tail:
        return False, f"Line {line_num}: Found URI (should be cleaned). Run merge_kg_files.py again."
    
    # Check for pipe character which is definitely wrong (but commas/semicolons can be valid in NELL)
    if '|' in head or '|' in relation or '|' in tail:
        return False, f"Line {line_num}: Found pipe character '|' - wrong delimiter"
    
    # Check for newlines or tabs in the middle (indicates parsing error)
    if '\n' in head or '\n' in relation or '\n' in tail:
        return False, f"Line {line_num}: Found newline character in field"
    
    return True, None

def validate_file(filepath, verbose=False):
    """Validate a single data file"""
    if not os.path.exists(filepath):
        return False, f"File not found: {filepath}", None
    
    filename = os.path.basename(filepath)
    errors = []
    triples = []
    entities = set()
    relations = defaultdict(int)
    
    try:
        print(f"\n   📄 Reading {filename}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                # Skip empty lines
                if not line.strip():
                    continue
                
                # Validate format
                valid, error = validate_triple_format(line, i, filename)
                if not valid:
                    errors.append(error)
                    if len(errors) >= 10:  # Stop after 10 errors
                        errors.append(f"... (stopped after 10 errors)")
                        break
                    continue
                
                # Parse triple
                head, relation, tail = line.strip().split('\t')
                triples.append((head, relation, tail))
                entities.add(head)
                entities.add(tail)
                relations[relation] += 1
                
                if verbose and i % 50000 == 0:
                    print(f"      Processed {i:,} lines...")
        
        if errors:
            return False, errors, None
        
        stats = {
            'num_triples': len(triples),
            'num_entities': len(entities),
            'num_relations': len(relations),
            'duplicates': len(triples) - len(set(triples)),
            'relations_dist': relations
        }
        
        return True, None, stats
        
    except Exception as e:
        return False, f"Error reading file: {e}", None

def validate_dataset(dataset_name, data_dir='./raw', verbose=False):
    """Validate a complete dataset"""
    
    print(f"\n{'='*70}")
    print(f"📋 Validating {dataset_name}")
    print('='*70)
    
    dataset_path = os.path.join(data_dir, dataset_name)
    
    # Check if directory exists
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset directory not found: {dataset_path}")
        print(f"   Run: python download_datasets.py --dataset {dataset_name}")
        return False
    
    expected = EXPECTED_STATS[dataset_name]
    filepath = os.path.join(dataset_path, expected['file'])
    
    # Check if file exists
    if not os.path.exists(filepath):
        print(f"❌ File not found: {expected['file']}")
        print(f"   Expected: {filepath}")
        print(f"   Run: python merge_kg_files.py --dataset {dataset_name}")
        return False
    
    # Validate the file
    valid, error, stats = validate_file(filepath, verbose)
    
    if not valid:
        print(f"❌ Validation failed:")
        if isinstance(error, list):
            for err in error:
                print(f"   - {err}")
        else:
            print(f"   - {error}")
        return False
    
    # Print statistics
    print(f"\n   ✅ Format valid: tab-separated triples")
    print(f"\n   📊 Statistics:")
    print(f"      ├─ Total triples: {stats['num_triples']:,}")
    print(f"      ├─ Unique entities: {stats['num_entities']:,}")
    print(f"      ├─ Unique relations: {stats['num_relations']:,}")
    
    if stats['duplicates'] > 0:
        print(f"      ⚠️  Duplicates found: {stats['duplicates']}")
    else:
        print(f"      └─ No duplicates ✓")
    
    # Check triple count is in expected range
    print(f"\n   🔍 Checking triple count...")
    if stats['num_triples'] < expected['min_triples']:
        print(f"      ⚠️  Warning: Only {stats['num_triples']:,} triples")
        print(f"         Expected at least {expected['min_triples']:,}")
        return False
    elif stats['num_triples'] > expected['max_triples']:
        print(f"      ⚠️  Warning: {stats['num_triples']:,} triples")
        print(f"         Expected at most {expected['max_triples']:,}")
        return False
    else:
        print(f"      ✓ Triple count in expected range: {expected['min_triples']:,} - {expected['max_triples']:,}")
    
    # Show top relations
    if verbose:
        print(f"\n   🔝 Top 10 relations:")
        sorted_relations = sorted(stats['relations_dist'].items(), key=lambda x: x[1], reverse=True)
        for i, (relation, count) in enumerate(sorted_relations[:10], 1):
            rel_display = relation[:60] + '...' if len(relation) > 60 else relation
            print(f"      {i:2d}. {rel_display:62s} : {count:>7,} triples")
    
    # Sample triples
    print(f"\n   📝 Sample triples:")
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 3:
                break
            parts = line.strip().split('\t')
            if len(parts) == 3:
                h = parts[0][:35] + '...' if len(parts[0]) > 35 else parts[0]
                r = parts[1][:35] + '...' if len(parts[1]) > 35 else parts[1]
                t = parts[2][:35] + '...' if len(parts[2]) > 35 else parts[2]
                print(f"      {i+1}. {h:37s} | {r:37s} | {t:37s}")
    
    print(f"\n   ✅ {dataset_name} validation PASSED")
    return True

def check_nell_cleaning(data_dir='./raw'):
    """Special check for NELL to ensure URIs were cleaned"""
    
    nell_path = os.path.join(data_dir, 'NELL', 'full_kg.tsv')
    if not os.path.exists(nell_path):
        return None
    
    print(f"\n{'='*70}")
    print(f"🧹 Checking NELL URI Cleaning")
    print('='*70)
    
    uri_count = 0
    total_lines = 0
    
    with open(nell_path, 'r', encoding='utf-8') as f:
        for line in f:
            total_lines += 1
            if 'http://' in line or 'nell.ml.cmu.edu' in line:
                uri_count += 1
            
            if total_lines >= 1000:  # Sample first 1000 lines
                break
    
    if uri_count > 0:
        print(f"   ⚠️  Found {uri_count} URIs in first {total_lines} lines")
        print(f"   ⚠️  NELL data may not be properly cleaned")
        print(f"   💡 Run: python merge_kg_files.py --dataset NELL")
        return False
    else:
        print(f"   ✅ No URIs found in sample of {total_lines} lines")
        print(f"   ✅ NELL data is properly cleaned")
        return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validate full_kg.tsv knowledge graph files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all datasets
  python validate_data.py
  
  # Validate specific dataset
  python validate_data.py --dataset NELL
  
  # Verbose output with relation statistics
  python validate_data.py --verbose

What this validates:
  ✓ File exists and is readable
  ✓ All lines are valid tab-separated triples
  ✓ No empty fields
  ✓ No URIs (should be cleaned)
  ✓ Triple count in expected range
  ✓ No suspicious characters
        """
    )
    
    parser.add_argument(
        '--dataset',
        type=str,
        choices=['NELL', 'FB15k-237', 'HealthKG'],
        help='Validate specific dataset only'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Validate all datasets (default behavior if no --dataset specified)'
    )
    parser.add_argument(
        '--data_dir',
        type=str,
        default='./raw',
        help='Data directory (default: ./raw)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed statistics and relation distribution'
    )
    
    args = parser.parse_args()
    
    # Handle --all option (it's actually the default, but explicit is nice)
    if args.all and args.dataset:
        parser.error("Cannot specify both --all and --dataset")

    
    print("="*70)
    print("  KNOWLEDGE GRAPH VALIDATOR")
    print("  Validates full_kg.tsv files")
    print("="*70)
    
    # Check if data directory exists
    if not os.path.exists(args.data_dir):
        print(f"\n❌ Data directory not found: {args.data_dir}")
        print("   Run: python download_datasets.py --all")
        sys.exit(1)
    
    print(f"\n📁 Data directory: {os.path.abspath(args.data_dir)}")
    
    # Validate datasets
    if args.dataset:
        datasets = [args.dataset]
    else:
        datasets = ['NELL', 'FB15k-237', 'HealthKG']
    
    results = {}
    for dataset in datasets:
        if dataset in EXPECTED_STATS:
            results[dataset] = validate_dataset(dataset, args.data_dir, args.verbose)
    
    # Special check for NELL cleaning
    if 'NELL' in datasets:
        check_nell_cleaning(args.data_dir)
    
    # Print final summary
    print("\n" + "="*70)
    print("📊 VALIDATION SUMMARY")
    print("="*70)
    
    for dataset, passed in results.items():
        if passed is None:
            status = "⏭️  SKIPPED"
        elif passed:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        print(f"{status} - {dataset}")
    
    print("="*70)
    
    # Exit code
    if all(v for v in results.values() if v is not None):
        print("\n✅ All datasets validated successfully!")
        print("\n📝 Next steps:")
        print("   1. Split datasets: bash scripts/split_all_datasets.sh")
        print("   2. Or use: python scripts/split.py --global_path raw/NELL/full_kg.tsv ...")
        sys.exit(0)
    else:
        print("\n❌ Some datasets failed validation")
        print("   Please check the errors above")
        sys.exit(1)

if __name__ == '__main__':
    main()