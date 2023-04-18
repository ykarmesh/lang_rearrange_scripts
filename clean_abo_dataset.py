import os
import csv
import json

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
        for objects in os.listdir(old_path + object_folder):
            old_object = object_folder + "/" + objects
            old_object_id = objects.split(".")[0]
            if old_object_id in object_ids_to_keep and objects.split(".")[1] == "glb":
  
                os.system("cp " + old_path + old_object + " " + new_path + objects)
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

                config_data["render_asset"] = "../assets/objects/" + config_data["render_asset"].split("/")[-1]
                config_data["collision_asset"] = "../assets/collision_meshes/" + config_data["collision_asset"].split("/")[-1]

            with open(config_path + config, "w") as f:
                json.dump(config_data, f, indent=2)

def remove_non_basis_files(path):
    objects = os.listdir(path)
    for object in objects:
        if object.split(".")[1] != "basis":
            os.system("rm " + path + object)
    
    objects = os.listdir(path)
    for object in objects:
        os.system("mv " + path + object + " " + path + object.split(".")[0] + ".glb")

if __name__ == "__main__":
    categories_csv_file = "csv/abo_categories.csv"

    object_ids_to_keep = get_object_ids_to_keep(categories_csv_file)
    print("Number of objects to keep: ", len(object_ids_to_keep))
    
    # old_path = "/Users/karmeshyadav/Code/habitat-sim/data/objects/amazon_berkeley/3dmodels/original/"
    # new_path = "/Users/karmeshyadav/Code/habitat-sim/data/objects/objects/amazon_berkeley/assets/objects/"

    # clean_objects_folder_version(old_path, new_path, object_ids_to_keep)

    # old_path = "/Users/karmeshyadav/Code/habitat-sim/data/objects/amazon_berkeley/collision_meshes/"
    # new_path = "/Users/karmeshyadav/Code/habitat-sim/data/objects/objects/amazon_berkeley/assets/collision_meshes/"

    # clean_objects(old_path, new_path, object_ids_to_keep)
    
    # old_path = "/Users/karmeshyadav/Code/habitat-sim/data/objects/amazon_berkeley/configs/"
    # new_path = "/Users/karmeshyadav/Code/habitat-sim/data/objects/objects/amazon_berkeley/configs/"

    # clean_objects(old_path, new_path, object_ids_to_keep)

    # config_path = "/Users/karmeshyadav/Code/habitat-sim/data/objects/objects/amazon_berkeley/configs/"
    
    # update_configs(config_path, object_ids_to_keep)

    objects_path = "/Users/karmeshyadav/Code/habitat-sim/data/objects/objects/amazon_berkeley/assets/objects/"
    remove_non_basis_files(objects_path)

