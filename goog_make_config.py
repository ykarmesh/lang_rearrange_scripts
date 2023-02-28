from argparse import ArgumentParser
import json
from pathlib import Path

import numpy as np
from tqdm import tqdm

parser = ArgumentParser()

parser.add_argument("--goog_path", type=Path, default="../data/objects/google_object_dataset")
parser.add_argument("--obj_anns", type=Path, default="../data/scale_rots_all.npy")

def main(args):
    goog_path: Path = args.goog_path
    obj_anns = np.load(args.obj_anns, allow_pickle=True).item()
    config_path = goog_path / "configs"
    config_path.mkdir(exist_ok=True)
    num_objs = 0
    for path in tqdm((goog_path/"objects").rglob("*obj")):
        assert path.name == "model.obj"
        obj_id = path.parts[-3]
        obj = obj_anns.get(obj_id)
        if not obj:
            continue
        config_file = config_path / (obj_id + ".object_config.json")
        config = {
            "render_asset": str(".." / path.relative_to(goog_path)),
            "scale": obj["scale"],
            "rotation": obj["rotation"],
            "requires_lighting": False,
            "collision_asset": f"../collision_meshes/{obj_id}/model.obj",
            "join_collision_meshes": False,
            "use_bounding_box_for_collision": False,
            "mass": 5,
            "margin": 0,
            "up": [0, 0, -1],
            "front": [0, 1, 0],
        }
        with open(config_file, "w") as f:
            json.dump(config, f)
        num_objs += 1
    print("Generated", num_objs, "configs.")

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
