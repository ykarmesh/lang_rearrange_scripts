import os
import csv
import json
import subprocess

def load_csv(csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data

def get_column_idx(data, column_name):
    for idx, column in enumerate(data[0]):
        if column == column_name:
            return idx
    return -1

def get_object_ids_to_keep(csv_file):
    data = load_csv(csv_file)

    # find the column that has the heading Name
    name_cidx = get_column_idx(data, "Name")

    # get all the objects ids
    object_ids = [d[name_cidx] for d in data[1:]]

    return object_ids


def clean_objects_folder_version(old_path, new_path, object_ids_to_keep):
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    # get all objects in the old path
    counter = 0
    old_objects_folders = os.listdir(old_path)
    for object_folder in old_objects_folders:
        if object_folder in object_ids_to_keep:
            os.system("cp -r " + old_path + object_folder + " " + new_path + object_folder + "/")
            counter+=1
    print("Number of objects moved: ", counter)


def clean_objects(old_path, new_path, object_ids_to_keep):
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    # get all objects in the old path
    counter = 0
    objects = os.listdir(old_path)
    for object in objects:
        old_object = old_path + object
        old_object_id = object.split(".")[0]
        if old_object_id in object_ids_to_keep:
            os.system("cp " + old_object + " " + new_path + object)
            counter+=1
    print("Number of objects moved: ", counter)


def update_configs(config_path, object_ids_to_keep):
    all_configs = os.listdir(config_path)
    for config in all_configs:
        config_id = config.split(".")[0]
        if config_id in object_ids_to_keep:
            with open(config_path + config, "r") as f:
                config_data = json.load(f)

                config_data["render_asset"] = "../assets/" + config_data["render_asset"][3:]
                config_data["collision_asset"] = "../assets/" + config_data["collision_asset"][3:]

            with open(config_path + config, "w") as f:
                json.dump(config_data, f, indent=2)

def obj_to_glb(asset_path, assimp_exec):
    obj_path = asset_path + "objects/"
    glb_path = asset_path + "objects_glb/"
    for obj_folder in os.listdir(obj_path):
        obj_file = obj_folder + "meshes/model.obj"
        glb_file = glb_path + obj_folder + ".glb"

        convert_object(obj_file, glb_file, assimp_exec)

def convert_object(from_file, to_file, assimp_exec="assimp"):
    subprocess.call([
        assimp_exec, "export",
        from_file, to_file
    ], stdout=subprocess.DEVNULL)
    assert to_file.is_file(), f"conversion failed on file {from_file}"

if __name__ == "__main__":
    categories_csv_file = "csv/gso_categories.csv"

    object_ids_to_keep = get_object_ids_to_keep(categories_csv_file)
    print("Number of objects to keep: ", len(object_ids_to_keep))
    
    old_path = "/Users/karmeshyadav/Code/habitat-sim/data/objects/google_object_dataset/objects/"
    new_path = "/Users/karmeshyadav/Code/habitat-sim/data/objects/objects/google_scanned/assets/objects/"

    clean_objects_folder_version(old_path, new_path, object_ids_to_keep)

    # old_path = "/Users/karmeshyadav/Code/habitat-sim/data/objects/google_object_dataset/collision_meshes/"
    # new_path = "/Users/karmeshyadav/Code/habitat-sim/data/objects/objects/google_scanned/assets/collision_meshes/"

    # clean_objects_folder_version(old_path, new_path, object_ids_to_keep)
    
    # old_path = "/Users/karmeshyadav/Code/habitat-sim/data/objects/google_object_dataset/configs/"
    # new_path = "/Users/karmeshyadav/Code/habitat-sim/data/objects/objects/google_scanned/configs/"

    # clean_objects(old_path, new_path, object_ids_to_keep)

    # config_path = "/Users/karmeshyadav/Code/habitat-sim/data/objects/objects/google_scanned/configs/"
    
    # update_configs(config_path, object_ids_to_keep)

    # old_path = "/Users/karmeshyadav/Code/habitat-sim/data/objects/google_object_dataset/google_object_dataset.scene_dataset_config.json"
    # new_path = "/Users/karmeshyadav/Code/habitat-sim/data/objects/objects/google_scanned/google_scanned.scene_dataset_config.json"

    # os.system("cp " + old_path + " " + new_path)
