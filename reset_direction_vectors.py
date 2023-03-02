import json
from pathlib import Path

def main():
    goog = Path("data/objects/google_object_dataset/configs")
    configs = list(goog.glob("*.json"))
    for config_file in configs:
        with open(config_file, "r") as f:
            config = json.load(f)
        
        config["up"] = [0, 0, -1]
        config["front"] = [0, 1, 0]

        with open(config_file, "w") as f:
            json.dump(config, f)
    
    abo = Path("data/objects/amazon_berkeley/configs")
    configs = list(abo.glob("*.json"))
    for config_file in configs:
        with open(config_file, "r") as f:
            config = json.load(f)
        
        config.pop("up", None)
        config.pop("front", None)

        with open(config_file, "w") as f:
            json.dump(config, f)

if __name__ == "__main__":
    main()
