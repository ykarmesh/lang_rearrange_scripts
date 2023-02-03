import argparse
from pathlib import Path
import subprocess
from multiprocessing import Pool

from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("--objs_path", type=Path, default="../data/versioned_data/google_object_dataset/objects")
parser.add_argument("--out_path", type=Path, default="../data/versioned_data/google_object_dataset/collision_meshes")
parser.add_argument("--coacd_exec", default="/home/kyash/CoACD/build/main")

def create_mesh(args):
    obj_dir: Path
    out_dir: Path
    obj_dir, out_dir, coacd_exec = args

    obj_file = obj_dir/"meshes/model.obj"
    obj_name = obj_dir.stem

    obj_out_dir = out_dir/obj_name
    obj_out_dir.mkdir(parents=True, exist_ok=True)
    obj_out_file = obj_out_dir/"model.obj"
    subprocess.call([
        coacd_exec,
        "-i", obj_file,
        "-o", obj_out_file,
        "-t", "0.2"
    ], stdout=subprocess.DEVNULL)
    glb_file = obj_out_file.with_suffix(".glb")
    subprocess.call([
        "assimp", "export",
        obj_out_file, glb_file
    ], stdout=subprocess.DEVNULL)
    assert glb_file.is_file()
    obj_out_file.unlink()

def main(args):
    # import pdb
    # pdb.set_trace()
    objs_path: Path = args.objs_path
    obj_dirs = objs_path.glob("*")
    args = [(obj_dir, args.out_path, args.coacd_exec) for obj_dir in obj_dirs]
    # for obj_dir in tqdm(obj_dirs):
    #     create_mesh((obj_dir, args.out_path, args.coacd_exec))
    with Pool(10) as p:
        list(tqdm(p.imap(create_mesh, args, chunksize=4), total=len(args)))

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
