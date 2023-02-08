from copy import deepcopy
from typing import List

import argparse
from multiprocessing import Pool
from pathlib import Path
import json
import os.path as osp
import functools

import trimesh
import trimesh.graph
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("--config-dir", type=Path)
parser.add_argument("--new-config-dir", type=Path)
parser.add_argument("--surfaces-dir", type=Path)
parser.add_argument("--debug", action="store_true")

def decompose_mesh(mesh: trimesh.Trimesh) -> List[trimesh.Trimesh]:
    decomposed_meshes : List[trimesh.Trimesh] = []
    ccs: List[trimesh.Trimesh] = trimesh.graph.split(mesh, only_watertight=False)
    for cc_concave_mesh in ccs:
        cc_decomposed_meshes = cc_concave_mesh.convex_decomposition(concavity=0.6)
        if type(cc_decomposed_meshes) is not list:
            cc_decomposed_meshes = [cc_decomposed_meshes]
        decomposed_meshes.extend(cc_decomposed_meshes)
    return decomposed_meshes

bad_meshes = [
    "b29f18c61b925bf549c484a58bd2e7515d11eef8",
    "9a1c224cd11be35a5c28347de7868674f56789da",
    "bb4a9531e0504b7b59b6649ac4d61b438112d3c2",
    "05e68620260bd6328447c56da2bc0912923e1db3",
]

def decompose_surface(config_file: Path, new_config_dir: Path, surfaces_dir: Path):
    new_config_file = new_config_dir/config_file.name
    if new_config_file.is_file():
        return

    if any(bad_mesh in config_file.name for bad_mesh in bad_meshes):
        print(f"Skipping {config_file} because it is a bad mesh.")
        return

    with open(config_file) as f:
        config = json.load(f)

    if "user_defined" not in config:
        return

    decomposed_meshes: List[trimesh.Trimesh] = []
    new_mesh_configs = {}
    for surface_key, surface in config["user_defined"].items():
        assert surface_key.startswith("receptacle_mesh_")
        receptacle_name = surface_key[len("receptacle_mesh_"):]
        surface_file = config_file.parent/Path(surface["mesh_filepath"])

        mesh = trimesh.load(surface_file)
        decomposed_meshes.extend(decompose_mesh(mesh))

        for i, decomposed_mesh in enumerate(decomposed_meshes):
            decomposed_mesh_key = f"{surface_key}_{i}"
            decomposed_surface = deepcopy(surface)
            decomposed_surface["name"] = decomposed_mesh_key

            new_file_name, file_suffix = surface_file.name.split(".", 1)
            new_file = surfaces_dir/receptacle_name/f"{new_file_name}_{i}.{file_suffix}"
            new_file.parent.mkdir(exist_ok=True, parents=True)
            decomposed_mesh.export(new_file)

            new_file = osp.relpath(new_file, new_config_dir)
            decomposed_surface["mesh_filepath"] = str(new_file)

            new_mesh_configs[decomposed_mesh_key] = decomposed_surface

    config["user_defined"] = new_mesh_configs
    with open(new_config_file, "w") as f:
        json.dump(config, f)

def main(config_dir: Path, new_config_dir: Path, surfaces_dir: Path, debug: bool):
    configs = list(config_dir.glob("*.json"))
    new_config_dir.mkdir(exist_ok=True, parents=True)
    surfaces_dir.mkdir(exist_ok=True, parents=True)
    partial = functools.partial(decompose_surface, new_config_dir=new_config_dir, surfaces_dir=surfaces_dir)
    if debug:
        for config in tqdm(configs):
            partial(config)
    else:
        with Pool(10) as p:
            list(tqdm(p.imap(partial, configs, chunksize=1), total=len(configs)))

if __name__ == "__main__":
    args = parser.parse_args()
    main(**vars(args))
