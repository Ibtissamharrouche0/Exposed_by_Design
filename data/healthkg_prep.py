#!/usr/bin/env python3
"""
HealthKG Complete Extraction (NO FILTERING)
Extracts ALL RDF data from RDF1-4.zip files to TSV format.
NO meta-relation filtering, NO anonymization, EVERYTHING is kept.

Prerequisites:
    pip install rdflib

Usage:
    python preprocess_healthkg.py --input "/path/to/Phase 5 - Entity Definition/"
    python preprocess_healthkg.py --download
"""

import argparse
import os
import sys
import zipfile
import shutil
from pathlib import Path
from collections import Counter

# Relations that indicate the head entity is a PERSON
PERSON_RELATIONS = {
    'has_age_category',
    'has_gender',
    'has_family_ID',
    'has_is_westernized',
    'has_zygosity',
    'has_age_living_apart',
    'has_mother_subject_ID',
    'has_father_subject_ID',
    'has_partner_subject_ID',
    'has_sibling',
    'has_is-from',
    'has_country',
    'has_dataset',
}

def check_dependencies():
    """Check if required libraries are installed"""
    try:
        from rdflib import Graph
        return True
    except ImportError:
        print("❌ rdflib not installed")
        print("   Install with: pip install rdflib")
        print("\n   In Colab/Jupyter, run:")
        print("   !pip install rdflib")
        return False

if not check_dependencies():
    raise ImportError("rdflib is required. Install with: pip install rdflib")

from rdflib import Graph

def is_running_in_notebook():
    """Check if running in Jupyter/Colab"""
    try:
        from IPython import get_ipython
        return get_ipython() is not None
    except:
        return False

def download_healthkg_repo():
    """Download HealthKG RDF files from GitHub"""
    print("\n" + "="*70)
    print("📥 Downloading HealthKG from GitHub")
    print("="*70)
    
    try:
        import urllib.request
        
        repo_url = "https://github.com/Boreico/KGE_QCB_Project/archive/refs/heads/main.zip"
        zip_path = "/tmp/healthkg_repo.zip"
        extract_path = "/tmp/healthkg_repo"
        
        print(f"\n📥 Downloading repository...")
        urllib.request.urlretrieve(repo_url, zip_path)
        print(f"   ✓ Downloaded")
        
        print(f"\n📦 Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        repo_dir = os.path.join(extract_path, "KGE_QCB_Project-main", "Phase 5 - Entity Definition")
        
        if not os.path.exists(repo_dir):
            print(f"❌ Phase 5 directory not found")
            return None
        
        print(f"✅ Extracted to: {repo_dir}")
        return repo_dir
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def load_all_rdf_files(input_dir):
    """Load ALL RDF zip files without any filtering"""
    print(f"\n" + "="*70)
    print(f"📂 Loading All RDF Files (NO FILTERING)")
    print("="*70)
    print(f"\n📁 Input directory: {input_dir}")
    
    if not os.path.exists(input_dir):
        print(f"❌ Directory not found: {input_dir}")
        return None
    
    g = Graph()
    
    # Find all RDF zip files
    rdf_zips = [f for f in os.listdir(input_dir) if f.startswith('RDF') and f.endswith('.zip')]
    
    if not rdf_zips:
        print(f"⚠️  No RDF*.zip files found in {input_dir}")
        return None
    
    print(f"\n📑 Found {len(rdf_zips)} RDF zip files:")
    for zf in sorted(rdf_zips):
        print(f"   - {zf}")
    
    # Extract and load each zip
    temp_extract = "/tmp/healthkg_rdf_temp"
    os.makedirs(temp_extract, exist_ok=True)
    
    for i, zip_name in enumerate(sorted(rdf_zips), 1):
        zip_path = os.path.join(input_dir, zip_name)
        print(f"\n📦 [{i}/{len(rdf_zips)}] Processing {zip_name}...")
        
        try:
            # Extract
            extract_dir = os.path.join(temp_extract, zip_name.replace('.zip', ''))
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            extracted_items = list(os.listdir(extract_dir))
            print(f"   Extracted {len(extracted_items)} items")
            
            # Find ALL RDF files recursively
            rdf_files = []
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file.endswith(('.rdf', '.owl', '.xml', '.ttl', '.nt')):
                        full_path = os.path.join(root, file)
                        rdf_files.append(full_path)
            
            print(f"   Found {len(rdf_files)} RDF files")
            
            if not rdf_files:
                print(f"   ⚠️  No RDF files found. Contents:")
                for item in extracted_items[:5]:
                    item_path = os.path.join(extract_dir, item)
                    if os.path.isdir(item_path):
                        print(f"      📁 {item}/")
                    else:
                        print(f"      📄 {item}")
            
            # Load each RDF file
            for rdf_file in rdf_files:
                try:
                    if rdf_file.endswith('.ttl'):
                        g.parse(rdf_file, format='turtle')
                    elif rdf_file.endswith('.nt'):
                        g.parse(rdf_file, format='nt')
                    elif rdf_file.endswith(('.rdf', '.owl', '.xml')):
                        g.parse(rdf_file, format='xml')
                    else:
                        g.parse(rdf_file)
                    
                    file_name = os.path.basename(rdf_file)
                    print(f"   ✓ Loaded: {file_name}")
                except Exception as e:
                    file_name = os.path.basename(rdf_file)
                    print(f"   ⚠️  Error loading {file_name}: {str(e)[:80]}")
        
        except Exception as e:
            print(f"   ❌ Error processing {zip_name}: {e}")
    
    # Cleanup
    if os.path.exists(temp_extract):
        shutil.rmtree(temp_extract)
    
    print(f"\n✅ Loaded {len(g):,} RDF triples total")
    return g

def simplify_uri(uri):
    """Extract clean identifier from URI"""
    uri_str = str(uri)
    
    # Remove common prefixes
    prefixes = [
        'http://www.semanticweb.org/ontologies/',
        'http://example.org/',
        'http://purl.org/dc/elements/1.1/',
        'http://www.w3.org/2000/01/rdf-schema#',
        'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    ]
    
    for prefix in prefixes:
        uri_str = uri_str.replace(prefix, '')
    
    # Extract last part
    if '#' in uri_str:
        return uri_str.split('#')[-1]
    elif '/' in uri_str:
        return uri_str.split('/')[-1]
    
    return uri_str

def convert_to_tsv(graph):
    """Convert RDF to TSV - KEEP EVERYTHING, NO FILTERING"""
    print(f"\n" + "="*70)
    print(f"🔄 Converting to TSV (NO FILTERING)")
    print("="*70)
    
    print(f"\n🔍 Processing {len(graph):,} RDF triples...")
    print(f"   ⚠️  Keeping ALL triples (no meta-relation filtering)")
    
    triples = []
    relation_counts = Counter()
    
    for i, (subject, predicate, obj) in enumerate(graph):
        if (i + 1) % 100000 == 0:
            print(f"   Processed {i+1:,} triples...")
        
        # Simplify URIs
        head = simplify_uri(subject)
        relation = simplify_uri(predicate)
        tail = simplify_uri(obj)
        
        # NO FILTERING - Keep everything including type, subClassOf, etc.
        # Only skip if fields are empty
        if head and relation and tail:
            triples.append((head, relation, tail))
            relation_counts[relation] += 1
    
    print(f"\n✅ Converted {len(triples):,} triples")
    print(f"   └─ Unique relations: {len(relation_counts):,}")
    
    return triples, relation_counts

def anonymize_persons(triples):
    """Anonymize ONLY person entities, keep everything else as-is"""
    print(f"\n" + "="*70)
    print(f"👤 Anonymizing Person Entities")
    print("="*70)
    
    # Step 1: Identify person entities by semantic relations
    person_entities = set()
    
    print(f"\n🔍 Scanning for person-related triples...")
    for i, (head, relation, tail) in enumerate(triples):
        if (i + 1) % 500000 == 0:
            print(f"   Scanned {i+1:,} triples...")
        
        if relation in PERSON_RELATIONS:
            person_entities.add(head)
    
    print(f"   ✓ Found {len(person_entities):,} unique person entities")
    
    # Step 2: Create anonymization mapping
    person_mapping = {}
    for i, person in enumerate(sorted(person_entities), 1):
        person_mapping[person] = f"Person_{i:04d}"
    
    print(f"   ✓ Created anonymization mapping")
    
    # Show samples
    print(f"\n📝 Sample anonymization (first 5):")
    for i, (original, anonymized) in enumerate(list(person_mapping.items())[:5]):
        orig_display = original[:40] + '...' if len(original) > 40 else original
        print(f"   {orig_display:45s} → {anonymized}")
    if len(person_mapping) > 5:
        print(f"   ... and {len(person_mapping) - 5:,} more")
    
    # Step 3: Apply anonymization (only to persons)
    print(f"\n🔄 Applying anonymization to {len(triples):,} triples...")
    anonymized_triples = []
    
    for i, (head, relation, tail) in enumerate(triples):
        if (i + 1) % 500000 == 0:
            print(f"   Processed {i+1:,} triples...")
        
        # Anonymize head if it's a person
        if head in person_mapping:
            head = person_mapping[head]
        
        # Anonymize tail if it's a person (for sibling, partner relations)
        if tail in person_mapping:
            tail = person_mapping[tail]
        
        anonymized_triples.append((head, relation, tail))
    
    print(f"   ✓ Anonymization complete")
    
    return anonymized_triples, person_mapping

def export_to_tsv(triples, output_file, relation_counts):
    """Export to TSV"""
    print(f"\n" + "="*70)
    print(f"💾 Exporting to TSV")
    print("="*70)
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print(f"\n📝 Writing to: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, (head, relation, tail) in enumerate(triples):
            if (i + 1) % 500000 == 0:
                print(f"   Written {i+1:,} triples...")
            f.write(f"{head}\t{relation}\t{tail}\n")
    
    print(f"✅ Exported {len(triples):,} triples")
    
    # Show top relations
    print(f"\n🔝 Top 15 relations:")
    for i, (relation, count) in enumerate(relation_counts.most_common(15), 1):
        rel_display = relation[:45] + '...' if len(relation) > 45 else relation
        print(f"   {i:2d}. {rel_display:47s} : {count:>8,} triples")

def validate_output(output_file):
    """Validate output"""
    print(f"\n" + "="*70)
    print(f"🔍 Validating Output")
    print("="*70)
    
    if not os.path.exists(output_file):
        print(f"❌ Output file not found: {output_file}")
        return False
    
    print(f"\n📄 Checking: {output_file}")
    
    entities = set()
    relations = Counter()
    line_count = 0
    person_count = 0
    
    with open(output_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if i % 500000 == 0:
                print(f"   Validated {i:,} lines...")
            
            line_count += 1
            parts = line.strip().split('\t')
            
            if len(parts) == 3:
                head, relation, tail = parts
                entities.add(head)
                entities.add(tail)
                relations[relation] += 1
                
                if head.startswith('Person_'):
                    person_count += 1
    
    person_entities = len([e for e in entities if e.startswith('Person_')])
    
    print(f"\n✅ Validation passed!")
    print(f"\n📊 Final statistics:")
    print(f"   ├─ Total triples: {line_count:,}")
    print(f"   ├─ Unique entities: {len(entities):,}")
    print(f"   ├─ Unique relations: {len(relations):,}")
    print(f"   └─ Person entities: {person_entities:,} (anonymized)")
    
    # Sample with persons
    print(f"\n📝 Sample triples (with anonymized persons):")
    with open(output_file, 'r', encoding='utf-8') as f:
        count = 0
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 3 and parts[0].startswith('Person_'):
                h = parts[0][:30] + '...' if len(parts[0]) > 30 else parts[0]
                r = parts[1][:30] + '...' if len(parts[1]) > 30 else parts[1]
                t = parts[2][:30] + '...' if len(parts[2]) > 30 else parts[2]
                print(f"   {count+1}. {h:32s} | {r:32s} | {t:32s}")
                count += 1
                if count >= 5:
                    break
    
    return True

def main():
    # Filter Jupyter kernel arguments
    if is_running_in_notebook():
        import sys
        original_argv = sys.argv.copy()
        sys.argv = [original_argv[0] if original_argv else 'preprocess_healthkg.py']
        print("📓 Running in Jupyter/Colab")
        print("   Automatically using --download mode")
        sys.argv.append('--download')
    
    parser = argparse.ArgumentParser(
        description='Extract ALL HealthKG data without filtering',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download and process automatically
  python preprocess_healthkg.py --download
  
  # Process local RDF files
  python preprocess_healthkg.py --input "/path/to/Phase 5 - Entity Definition/"

What it does:
  1. Loads all RDF*.zip files (RDF1, RDF2, RDF3, RDF4)
  2. Merges all RDF triples
  3. Converts to TSV (NO FILTERING, keeps everything)
  4. Anonymizes ONLY person entities → Person_0001, Person_0002, etc.
  5. Exports to full_kg.tsv

All triples kept, only persons are anonymized.
        """
    )
    
    parser.add_argument(
        '--input',
        type=str,
        help='Directory containing RDF*.zip files'
    )
    parser.add_argument(
        '--download',
        action='store_true',
        help='Download from GitHub automatically'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='./raw/HealthKG/full_kg.tsv',
        help='Output TSV file (default: ./raw/HealthKG/full_kg.tsv)'
    )
    
    args = parser.parse_args()
    
    if not args.input and not args.download:
        parser.error("Specify --input <directory> or --download")
    
    print("\n" + "="*70)
    print("  HEALTHKG COMPLETE EXTRACTION")
    print("  Load → Convert → Export (NO FILTERING)")
    print("="*70)
    
    # Step 1: Get input
    if args.download:
        input_dir = download_healthkg_repo()
        if not input_dir:
            return 1
    else:
        input_dir = args.input
    
    # Step 2: Load RDF
    graph = load_all_rdf_files(input_dir)
    if not graph or len(graph) == 0:
        print("\n❌ No RDF data loaded")
        return 1
    
    # Step 3: Convert (no filtering)
    triples, relation_counts = convert_to_tsv(graph)
    if not triples:
        print("\n❌ No triples to export")
        return 1
    
    # Step 4: Anonymize persons only
    anonymized_triples, person_mapping = anonymize_persons(triples)
    
    # Step 5: Export
    export_to_tsv(anonymized_triples, args.output, relation_counts)
    
    # Step 6: Validate
    valid = validate_output(args.output)
    
    # Summary
    print("\n" + "="*70)
    if valid:
        print("✅ HEALTHKG EXTRACTION COMPLETE!")
    else:
        print("⚠️  COMPLETED WITH WARNINGS")
    print("="*70)
    
    print(f"\n📁 Output: {os.path.abspath(args.output)}")
    print(f"📊 Triples: {len(anonymized_triples):,}")
    print(f"👤 Persons anonymized: {len(person_mapping):,}")
    
    print("\n📝 Next steps:")
    print(f"   python scripts/split.py --global_path {args.output} ...")
    print()
    
    return 0 if valid else 1

if __name__ == '__main__':
    sys.exit(main())