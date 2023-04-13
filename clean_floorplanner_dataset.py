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

def get_object_ids_to_keep(categories_csv_file, objects_csv_file):
    categories_data = load_csv(categories_csv_file)
    objects_data = load_csv(objects_csv_file)

    # find the column that has the heading main_category
    cs_main_category_cidx = get_column_idx(categories_data, "main_category")
    os_main_category_cidx = get_column_idx(objects_data, "main_category")
    os_main_wnsynsetkey_cidx = get_column_idx(objects_data, "main_wnsynsetkey")


    # find the column that has the heading id
    os_id_cidx = get_column_idx(objects_data, "id")

    # find the column that has the heading Notes from Karmesh
    cs_notes_cidx = get_column_idx(categories_data, "Notes from Karmesh")

    # remove the header
    categories_data = categories_data[1:]
    objects_data = objects_data[1:]

    category_to_object_type_mapping = {}
    for category in categories_data:
        category_to_object_type_mapping[category[cs_main_category_cidx]] = category[cs_notes_cidx]

    object_ids_to_keep = []
    counter = 0
    unknown_categories = {}
    collected_categories = {}
    # find the object ids that we want to keep
    with open("cat_to_obj_mapping.txt", "w") as f:
        for obj in objects_data:
            if obj[os_main_category_cidx] in category_to_object_type_mapping:
                if category_to_object_type_mapping[obj[os_main_category_cidx]] == "pickupable":
                    object_ids_to_keep.append(obj[os_id_cidx])
                    if obj[os_main_category_cidx] not in collected_categories:
                        collected_categories[obj[os_main_category_cidx]] = 0
                    collected_categories[obj[os_main_category_cidx]] += 1
                    f.write("{},{}\n".format(obj[os_id_cidx], obj[os_main_wnsynsetkey_cidx].split(".")[0]))

                    counter+=1
            else:
                if obj[os_main_category_cidx] not in unknown_categories:
                    unknown_categories[obj[os_main_category_cidx]] = 0
                unknown_categories[obj[os_main_category_cidx]] += 1

    print("Number of objects to keep: ", counter)
    print("Number of unknown categories: ", len(unknown_categories))
    print("Unknown categories: ", unknown_categories)
    print("Number of collected categories: ", collected_categories)

    return object_ids_to_keep

def clean_objects(old_path, new_path, object_ids_to_keep):
    # get all objects in the old path
    counter = 0
    old_objects = os.listdir(old_path)
    for old_object in old_objects:
        old_object_id = old_object.split(".")[0]
        if old_object_id in object_ids_to_keep:
            os.system("cp " + old_path + old_object + " " + new_path + old_object)
            counter+=1
    print("Number of objects moved: ", counter)    

def update_configs(config_path, object_ids_to_keep):
    all_configs = os.listdir(config_path)
    for config in all_configs:
        config_id = config.split(".")[0]
        if config_id in object_ids_to_keep:
            with open(config_path + config, "r") as f:
                config_data = json.load(f)

            if "compressed-objects" in config_data["render_asset"]:
                config_data["render_asset"] = config_data["render_asset"].replace("compressed-objects", "objects")
            if "coacd" in config_data["collision_asset"]:
                config_data["collision_asset"] = config_data["collision_asset"].replace("coacd", "collision_meshes")
            if "\"../assets/collision_meshes/" in config_data["collision_asset"]:
                config_data["collision_asset"] = config_data["collision_asset"].replace("../assets/collision_meshes/", "../../assets/collision_meshes/")
            
            with open(config_path + config, "w") as f:
                json.dump(config_data, f, indent=2)

if __name__ == "__main__":
    categories_csv_file = "floorplanner_categories_v0.2.3.csv"
    objects_csv_file = "floorplanner_objects_v0.2.3.csv"

    object_ids_to_keep = get_object_ids_to_keep(categories_csv_file, objects_csv_file)
    
    # old_path = "/private/home/karmeshyadav/language_rearrangement/floorplanner/assets/compressed-objects/"
    # new_path = "/private/home/karmeshyadav/language_rearrangement/object_datasets/floorplanner/assets/objects/"

    # clean_objects(old_path, new_path, object_ids_to_keep)

    # old_path = "/private/home/karmeshyadav/language_rearrangement/floorplanner/configs/objects/"
    # new_path = "/private/home/karmeshyadav/language_rearrangement/object_datasets/floorplanner/configs/objects/"

    # clean_objects(old_path, new_path, object_ids_to_keep)

    # old_path = "/private/home/karmeshyadav/language_rearrangement/floorplanner/assets/coacd/"
    # new_path = "/private/home/karmeshyadav/language_rearrangement/object_datasets/floorplanner/assets/collision_meshes/"

    # clean_objects(old_path, new_path, object_ids_to_keep)

    config_path = "/private/home/karmeshyadav/language_rearrangement/object_datasets/floorplanner/configs/objects/"
    
    update_configs(config_path, object_ids_to_keep)
