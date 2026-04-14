import os
import sys
import re
from pathlib import Path

#(Get-ChildItem -Directory).Count

def update_image_tag(file_path, new_tag):
    """Update the image tag in a config.yaml file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match 'tag: <anything>' and replace with new tag
        # This handles various formats like tag: "value", tag: value, tag: 'value'
        pattern = r'(\s+tag:\s+)["\']?[^"\'\s]+["\']?'
        replacement = rf'\g<1>{new_tag}'
        
        updated_content = re.sub(pattern, replacement, content)
        
        # Check if any changes were made
        if content != updated_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            return True
        return False
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False


def get_client_folders(base_folder):
    """Get a sorted list of client folders in the base folder."""
    folder_path = Path(base_folder)
    if not folder_path.exists():
        print(f"Error: Folder '{base_folder}' does not exist.")
        return []
    
    # Get all subdirectories
    client_folders = [d for d in folder_path.iterdir() if d.is_dir()]
    # Sort alphabetically
    client_folders.sort(key=lambda x: x.name.lower())
    return client_folders


def parse_range(range_str):
    """Parse range string like '0-10' or '11-30' into start and end indices."""
    try:
        parts = range_str.split('-')
        if len(parts) != 2:
            raise ValueError("Range must be in format 'start-end'")
        start = int(parts[0])
        end = int(parts[1])
        if start < 0 or end < start:
            raise ValueError("Invalid range values")
        return start, end
    except ValueError as e:
        print(f"Error parsing range: {e}")
        return None, None


def main():
    if len(sys.argv) != 4:
        print("Usage: python updateImagetag.py <folder> <range> <tag>")
        print("Example: python updateImagetag.py prod-au01 0-10 26.01")
        print("         python updateImagetag.py prod-au01 11-30 26.01")
        sys.exit(1)
    
    base_folder = sys.argv[1]
    range_str = sys.argv[2]
    new_tag = sys.argv[3]
    
    # Parse the range
    start_idx, end_idx = parse_range(range_str)
    if start_idx is None or end_idx is None:
        sys.exit(1)
    
    # Get client folders
    client_folders = get_client_folders(base_folder)
    if not client_folders:
        print(f"No client folders found in '{base_folder}'")
        sys.exit(1)
    
    print(f"Found {len(client_folders)} client folders in '{base_folder}'")
    print(f"Processing clients {start_idx} to {end_idx} (inclusive)")
    print(f"New tag: {new_tag}")
    print("-" * 60)
    
    # Process the specified range
    updated_count = 0
    skipped_count = 0
    
    for idx in range(start_idx, min(end_idx + 1, len(client_folders))):
        client_folder = client_folders[idx]
        config_file = client_folder / "config.yaml"
        
        if not config_file.exists():
            skipped_count += 1
            continue
        
        if update_image_tag(config_file, new_tag):
            print(client_folder.name)
            updated_count += 1
    
    print("-" * 60)
    print(f"Summary: {updated_count} updated, {skipped_count} skipped")
    
    if start_idx >= len(client_folders):
        print(f"\nWarning: Start index {start_idx} is beyond the number of available folders ({len(client_folders)})")
    elif end_idx >= len(client_folders):
        print(f"\nNote: End index {end_idx} exceeds available folders. Processed up to index {len(client_folders) - 1}")


#python updateImagetag.py prod-au01 0-27 26.01
if __name__ == "__main__":
    main()
