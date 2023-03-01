import argparse
from pathlib import Path
import json

import numpy as np
import quaternion
import pandas as pd
from tqdm import tqdm

from habitat.utils.geometry_utils import quaternion_rotate_vector

parser = argparse.ArgumentParser()

parser.add_argument("--dataset-test-file", required=True)
parser.add_argument("--config-dir", type=Path, required=True)

axes = {
    "axis1": ([1, 0, 0], 0),
    "axis2": ([1, 0, 0], 90),
    "axis3": ([1, 0, 0], 180),
    "axis4": ([-1, 0, 0], 90),
    "axis5": ([0, 0, -1], 90),
    "axis6": ([0, 0, 1], 90),
}

def main(args):
    config_dir: Path = args.config_dir
    dataset = pd.read_csv(args.dataset_test_file)
    configs = list(config_dir.glob("*.json"))
    for config_file in tqdm(configs):
        with open(config_file, "r") as f:
            config = json.load(f)

        up = config.get("up", [0, 1, 0])
        front = config.get("front", [0, 0, -1])

        object_file = config_file.name
        object_data = dataset[dataset["file"] == object_file]
        assert len(object_data) == 1
        
        best_axis = None
        best_time = np.inf
        for axis_name in axes:
            settle_time = object_data[axis_name].values[0]
            if "timed out" in settle_time:
                continue
            settle_time = float(settle_time.split(" ", 1)[0])
            if settle_time < best_time:
                best_time = settle_time
                best_axis = axis_name

        if best_axis is None:
            print(f"Skipping {object_file} because it timed out on all axes")
            continue

        axis_vector, axis_angle = axes[best_axis]
        axis = quaternion.from_rotation_vector(np.array(axis_vector) * np.deg2rad(axis_angle))
        up = quaternion_rotate_vector(axis, up)
        front = quaternion_rotate_vector(axis, front)
        config["up"] = up.round().tolist()
        config["front"] = front.round().tolist()

        with open(config_file, "w") as f:
            json.dump(config, f)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
