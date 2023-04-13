import os
import json

def get_alfred_objects(old_path, new_path):
    # make the new folder if it doesnt exist
    # if not os.path.exists(new_path):
    #     os.mkdir(new_path)

    config_files = os.listdir(old_path)
    print(len(config_files))

    alfred_files_full_name = [file for file in config_files if not file.startswith("ArchitecTHOR") and not file.startswith("RoboTHOR") and not file.startswith("FloorPlan")]

    # remove everything after .
    alfred_files = [file.split(".")[0] for file in alfred_files_full_name]

    blacklist = ['Clothes_Dryer']
    # remove the blacklisted files
    for blacklist_file in blacklist:
        for alfred_file in alfred_files:
            if blacklist_file in alfred_file:
                alfred_files.remove(alfred_file)

    original_alfred_list = ["Alarm_Clock", "Apple", "AppleSliced", "BaseballBat", "Basketball", "Book", \
                            "Bowl", "Bread", "BreadSliced", "ButterKnife", "CD", "Candle", \
                            "Cellphone", "Cloth", "CreditCard", "Cup", "Dish_Sponge", "Egg", "Fork", \
                            "Glassbottle", "HandTowel", "Kettle", "Keychain", "Knife", "Ladle", "Laptop", \
                            "Lettuce", "LettuceSliced", "Mug", "Newspaper", "Pan", "Pencil", "Pen", \
                            "Pepper_Shaker", "pillow", "Plate", "Plunger", "Potato", "Pot", "PotatoSliced", \
                            "Remote", "Salt_Shaker", "Soap_Bar", "Soap_Bottle", "Spatula", "Spoon", \
                            "Spray_Bottle", "Statue", "Tennis_Racquet", "Tissue_Box", "ToiletPaper", "Tomato", \
                            "TomatoSliced", "Watch", "Vase", "Wine_Bottle", "Watering_Can", "Box"]
    # Not available in the dataset
    #AppleSliced
    #BreadSliced
    #LettuceSliced
    #PotatoSliced
    #TomatoSliced
    #CD
    #Glassbottle
    #HandTowel
    #ToiletPaper

    cat_to_obj_mapping = {}
    for obj in original_alfred_list:
        cat_to_obj_mapping[obj] = []

        files_to_remove = []
        for file in alfred_files:
            if obj in file:
                cat_to_obj_mapping[obj].append(file)
                # delete the file from the list
                files_to_remove.append(file)

        if len(cat_to_obj_mapping[obj]) == 0:
            print("No files found for object: ", obj)

        for file in files_to_remove:
            alfred_files.remove(file)

    # create a new file and store the mapping
    with open("cat_to_obj_mapping.txt", "w") as f:
        for key, value in cat_to_obj_mapping.items():
            for val in value:
                f.write("{},{}\n".format(val, key))
            # print(key, ":", value)ß
            # print(key, ":", len(value))

    selected_objects_name_list = list(cat_to_obj_mapping.values())
    selected_objects_name_list = [item for sublist in selected_objects_name_list for item in sublist]

    # copy over the files that are in the selected_objects_name_list
    for object_name in selected_objects_name_list:
        for file_name in alfred_files_full_name:
            if object_name in file_name:
                # full path of the file
                file_path = os.path.join(old_path, file_name)
                # copy the file to the new folder
                # os.system("cp " + file_path + " " + new_path)

    # # find part of the string that doesnt match between key and value
    # for key, value in cat_to_obj_mapping.items():
    #     for val in value:
    #         leftover = val.replace(key, "")
    #         leftover_parts = leftover.split("_")
    #         leftover_parts = [part for part in leftover_parts if part!='' and part!=' ' and not part.isdigit()]
    #         if len(leftover_parts) > 0:
    #             print(key, ":", leftover_parts)

def update_configs(config_path):
    all_configs = os.listdir(config_path)
    for config in all_configs:

        # load json file
        with open(os.path.join(config_path, config), "r") as f:
            data = json.load(f)
        
        # add path to the collision_asset
        data["collision_asset"] = "../../assets/collision_meshes/" + data["render_asset"].split("/")[-1]

        # save the file
        with open(os.path.join(config_path, config), "w") as f:
            json.dump(data, f, indent=2)


if __name__ == "__main__":
    old_path = "/private/home/karmeshyadav/language_rearrangement/object_datasets/ai2thorhab/assets/objects/"
    new_path = "/private/home/karmeshyadav/language_rearrangement/object_datasets/ai2thorhab/assets/selected_objects/"

    # get_alfred_objects(old_path, new_path)

    # old_path = "/private/home/karmeshyadav/language_rearrangement/object_datasets/ai2thorhab/configs/objects/"
    # new_path = "/private/home/karmeshyadav/language_rearrangement/object_datasets/ai2thorhab/configs/selected_objects/"

    # get_alfred_objects(old_path, new_path)

    config_path = "/private/home/karmeshyadav/language_rearrangement/object_datasets/ai2thorhab/configs/objects/"
    update_configs(config_path)