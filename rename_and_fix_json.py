import os
import json

# Paths relative to your project root
root_folder = os.path.join("static", "cards")
json_path = os.path.join("tarot_data.json")

def force_lowercase_rename(base_path):
    """Rename all files under base_path to lowercase (Windows-safe)."""
    for dirpath, _, filenames in os.walk(base_path):
        for filename in filenames:
            lower_name = filename.lower()
            temp_name = lower_name + ".tmp_rename"

            old_path = os.path.join(dirpath, filename)
            temp_path = os.path.join(dirpath, temp_name)
            new_path = os.path.join(dirpath, lower_name)

            # Skip already-lowercase files
            if filename == lower_name:
                continue

            try:
                # Step 1: Rename to temp name (forces Windows to register a change)
                os.rename(old_path, temp_path)
                # Step 2: Rename to the proper lowercase name
                os.rename(temp_path, new_path)
                print(f"✅ Renamed: {filename} → {lower_name}")
            except Exception as e:
                print(f"⚠️ Error renaming {filename}: {e}")

def fix_json_image_paths(json_file):
    """Convert all image paths inside tarot_data.json to lowercase."""
    if not os.path.exists(json_file):
        print(f"⚠️ JSON file not found at {json_file}. Skipping JSON update.")
        return

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    def lowercase_images(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k.lower() == "image" and isinstance(v, str):
                    obj[k] = v.lower()
                else:
                    lowercase_images(v)
        elif isinstance(obj, list):
            for item in obj:
                lowercase_images(item)

    lowercase_images(data)

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"🧩 Updated all image paths in {json_file} to lowercase.")

if __name__ == "__main__":
    if os.path.exists(root_folder):
        print(f"🔧 Renaming all files in {root_folder} to lowercase...")
        force_lowercase_rename(root_folder)
        print("🎯 File renaming complete.\n")
    else:
        print("❌ Error: static/cards folder not found. Run this from your project root.\n")

    print(f"📘 Fixing image paths in {json_path}...")
    fix_json_image_paths(json_path)
    print("✅ All done! Filenames and JSON paths are now synchronized.")
