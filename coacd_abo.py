import argparse
from pathlib import Path
import subprocess
from multiprocessing import Pool

from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("--objs_path", type=Path, default="../data/versioned_data/amazon_berkeley/3dmodels")
parser.add_argument("--out_path", type=Path, default="../data/versioned_data/amazon_berkeley/collision_meshes")
parser.add_argument("--coacd_exec", default="/home/kyash/CoACD/build/main")

def convert_object(from_file, to_file):
    subprocess.call([
        "assimp", "export",
        from_file, to_file
    ], stdout=subprocess.DEVNULL)
    assert to_file.is_file(), f"conversion failed on file {from_file}"

def create_mesh(args):
    object_glb_file: Path
    out_dir: Path
    object_glb_file, out_dir, coacd_exec = args
    out_dir.mkdir(parents=True, exist_ok=True)

    object_name = object_glb_file.stem
    coll_obj_file = out_dir/(object_name + ".obj")
    if coll_obj_file.is_file() or object_name in {"B07GFG117Y", "B07BWL248S", "B07BW8QTX1"}:
        return

    object_obj_file = object_glb_file.with_suffix(".obj")
    convert_object(object_glb_file, object_obj_file)

    subprocess.call([
        coacd_exec,
        "-i", object_obj_file,
        "-o", coll_obj_file,
        "-l", "/dev/null",
        "-t", "0.4"
    ], stdout=subprocess.DEVNULL)
    assert coll_obj_file.is_file(), f"coacd failed on file {object_obj_file}"

    # coll_glb_file = coll_obj_file.with_suffix(".glb")
    # convert_object(coll_obj_file, coll_glb_file)

    # coll_obj_file.unlink()
    coll_obj_file.with_suffix(".wrl").unlink()
    object_obj_file.unlink()
    object_obj_file.with_suffix(".mtl").unlink()

def main(args):
    # import pdb
    # pdb.set_trace()
    objs_path: Path = args.objs_path
    obj_files = objs_path.rglob("*glb")
    args = [(obj_file, args.out_path, args.coacd_exec) for obj_file in obj_files]
    with Pool(10) as p:
        list(tqdm(p.imap(create_mesh, args, chunksize=4), total=len(args)))
    # for obj_files in tqdm(obj_files):
    #     create_mesh((obj_files, args.out_path, args.coacd_exec))

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
