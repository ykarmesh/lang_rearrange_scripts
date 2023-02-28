from argparse import ArgumentParser
import json
from pathlib import Path

import numpy as np
from tqdm import tqdm

parser = ArgumentParser()

parser.add_argument("--abo_path", type=Path, default="../data/objects/amazon_berkeley")
parser.add_argument("--obj_anns", type=Path, default="../data/scale_rots_all.npy")

def main(args):
    abo_path: Path = args.abo_path
    obj_anns = np.load(args.obj_anns, allow_pickle=True).item()
    config_path = abo_path / "configs"
    config_path.mkdir(exist_ok=True)
    num_objs = 0
    for path in tqdm(abo_path.rglob("*glb")):
        obj_id = path.stem
        obj = obj_anns.get(obj_id)
        if not obj:
            continue
        config_file = config_path / (obj_id + ".object_config.json")
        config = {
            "render_asset": str(".." / path.relative_to(abo_path)),
            "mass": 9,
            "scale": obj["scale"],
            "rotation": obj["rotation"],
            "requires_lighting": True,
            "collision_asset": f"../collision_meshes/{obj_id}.obj",
            "join_collision_meshes": False,
            # "up": [0, 0, 1],
            # "front": [0, -1, 0],
        }
        with open(config_file, "w") as f:
            json.dump(config, f)
        num_objs += 1
    print("Generated", num_objs, "configs.")

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
