import argparse
from pathlib import Path
import subprocess
from multiprocessing import Pool

from tqdm import tqdm

def convert_object(from_file, to_file, assimp_exec="assimp"):
    subprocess.call([
        assimp_exec, "export",
        from_file, to_file
    ], stdout=subprocess.DEVNULL)
    assert to_file.is_file(), f"conversion failed on file {from_file}"

def create_mesh_glb(args):
    object_glb_file: Path
    out_dir: Path
    object_glb_file, out_dir, coacd_exec, assimp_exec = args

    object_name = object_glb_file.stem

    out_dir.mkdir(parents=True, exist_ok=True)

    coll_obj_file = out_dir/(object_name + ".obj")
    if coll_obj_file.is_file():
        return

    object_obj_file = object_glb_file.with_suffix(".obj")
    convert_object(object_glb_file, object_obj_file, assimp_exec)

    subprocess.call([
        coacd_exec,
        "-i", object_obj_file,
        "-o", coll_obj_file,
        "-l", "/dev/null",
        "-t", "0.4"
    ], stdout=subprocess.DEVNULL)
    assert coll_obj_file.is_file(), f"CoACD failed on file {object_obj_file}"

    coll_glb_file = coll_obj_file.with_suffix(".glb")
    convert_object(coll_obj_file, coll_glb_file, assimp_exec)
    coll_obj_file.unlink()

    coll_obj_file.with_suffix(".wrl").unlink()
    object_obj_file.unlink()
    object_obj_file.with_suffix(".mtl").unlink()

def create_mesh_obj(args):
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
        "-t", "0.4"
    ], stdout=subprocess.DEVNULL)
    assert obj_out_file.is_file(), f"CoACD failed on file {obj_file}"


def main(args):
    objs_path: Path = args.objs_path
    obj_files = objs_path.rglob("*glb")
    
    if args.data_type == "glb":
        create_mesh = create_mesh_glb
    elif args.data_type == "obj":
        create_mesh = create_mesh_obj
    else:
        raise ValueError(f"Unknown dataset {args.dataset}")

    if args.use_multiprocessing:
        args_for_function = [(obj_file, args.out_path, args.coacd_exec, args.assimp_exec) for obj_file in obj_files]
        with Pool(10) as p:
            list(tqdm(p.imap(create_mesh, args_for_function, chunksize=4), total=len(args)))
    else:
        for obj_files in tqdm(obj_files):
            create_mesh((obj_files, args.out_path, args.coacd_exec, args.assimp_exec))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--objs_path", type=Path, default="../data/versioned_data/amazon_berkeley/3dmodels")
    parser.add_argument("--out_path", type=Path, default="../data/versioned_data/amazon_berkeley/collision_meshes")
    parser.add_argument("--coacd_exec", type=str, default="../CoACD/build/main")
    parser.add_argument("--assimp_exec", type=str, default="assimp")
    parser.add_argument("--data_type", type=str, default="glb")
    parser.add_argument("--use_multiprocessing", action="store_true", default=False)
    args = parser.parse_args()

    main(args)
