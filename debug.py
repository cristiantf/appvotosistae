
import sys
import os

print("--- Python Executable ---")
print(sys.executable)
print("\n--- Python Path (sys.path) ---")
for path in sys.path:
    print(path)

site_packages_path = None
for path in sys.path:
    if 'site-packages' in path:
        site_packages_path = path
        break

if site_packages_path and os.path.exists(site_packages_path):
    print(f"\n--- Contents of {site_packages_path} ---")
    try:
        contents = os.listdir(site_packages_path)
        for item in sorted(contents):
            print(item)
    except Exception as e:
        print(f"Error listing directory: {e}")
else:
    print("\n--- site-packages directory not found in sys.path or does not exist ---")
