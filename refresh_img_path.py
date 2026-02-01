import os
import re
import shutil
from pathlib import Path

def heal_bounded_assets():
    # Use current directory as the repo root
    repo_root = Path.cwd()
    
    # Matches exactly: ![](./assets/filename.ext) or ![alt](./assets/filename.ext)
    # Group 1: alt text, Group 2: filename
    img_regex = re.compile(r'!\[(.*?)\]\(\./assets/([^/)]+\.(?:png|jpg|jpeg|gif|svg|webp))\)')

    # 1. Create a global index of all images available in the repo
    image_pool = {}
    for img_path in repo_root.rglob('*'):
        if img_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']:
            # Unique filename constraint allows us to map name -> absolute path
            image_pool[img_path.name] = img_path

    print(f"--- Syncing bounded assets in: {repo_root} ---")

    # 2. Iterate through all Markdown files
    for md_path in repo_root.rglob('*.md'):
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        matches = img_regex.findall(content)
        if not matches:
            continue

        doc_dir = md_path.parent
        local_assets_dir = doc_dir / "assets"
        
        for alt_text, img_name in matches:
            expected_path = local_assets_dir / img_name
            
            # If the image is missing from the local bounded 'assets' folder
            if not expected_path.exists():
                print(f"[!] Missing bounded asset: {img_name} for {md_path.name}")
                
                if img_name in image_pool:
                    # Create the assets folder if it doesn't exist
                    local_assets_dir.mkdir(exist_ok=True)
                    
                    # Copy the image from its current location in the repo to this doc's assets
                    source_origin = image_pool[img_name]
                    shutil.copy2(source_origin, expected_path)
                    print(f"    [+] Successfully pulled to: {expected_path.relative_to(repo_root)}")
                else:
                    print(f"    [?] Error: {img_name} not found anywhere in the repository.")

    print("\n--- Sync Complete ---")

if __name__ == "__main__":
    heal_bounded_assets()