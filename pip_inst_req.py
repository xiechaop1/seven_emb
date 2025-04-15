import subprocess

with open("requirements.txt", "r") as f:
    for line in f:
        package = line.strip()
        if not package:
            continue
        try:
            print(f"Installing {package}...")
            subprocess.run(["pip", "install", package])
        except Exception as e:
            print(f"Failed to install {package}: {e}")
            print(f"Skipping and continuing ...")