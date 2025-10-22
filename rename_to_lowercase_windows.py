import os

root_folder = os.path.join("static", "cards")

def force_lowercase_rename(base_path):
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
                # Step 1: Rename to a temp filename (forces Windows to register a change)
                os.rename(old_path, temp_path)
                # Step 2: Rename again to the proper lowercase name
                os.rename(temp_path, new_path)
                print(f"✅ {filename} → {lower_name}")
            except Exception as e:
                print(f"⚠️ Error renaming {filename}: {e}")

if __name__ == "__main__":
    if os.path.exists(root_folder):
        print(f"Renaming all files in {root_folder} to lowercase...")
        force_lowercase_rename(root_folder)
        print("🎯 Done! All filenames should now be lowercase.")
    else:
        print("❌ Error: static/cards folder not found. Run this script from your project root.")
