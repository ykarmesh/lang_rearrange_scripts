import argparse
import os
import subprocess

START_IDX = 817
TOTAL_OBJECTS = 5091
TOTAL_RUNS = 100

def read_log_files(path):
    log_files = os.listdir(path)
    log_files = [f for f in log_files if f.endswith(".out")]
    print("Found {} log files".format(len(log_files)))
    
    objects_completed = []
    objects_completed_name = []
    for log_file in log_files:
        obj_completed, obj_completed_name = read_log_file(os.path.join(path, log_file))
        objects_completed.extend(obj_completed)
        objects_completed_name.extend(obj_completed_name)
        print("Objects completed in {}: {}".format(log_file, len(obj_completed)))
    
    print("Total objects completed: {}".format(len(objects_completed)))

    # find missing idx from START_IDX to TOTAL_OBJECTS
    missing_objects = []
    for i in range(START_IDX, TOTAL_OBJECTS + 1):
        if str(i) not in objects_completed:
            missing_objects.append(i)
    print("Missing objects: {}".format(missing_objects))
    print("Missing objects size: {}".format(len(missing_objects)))

def read_log_file(path):
    objects_completed = []
    objects_completed_name = []
    with open(path, "r") as f:
        lines = f.readlines()
        for line in lines:
            if "Completed optimization" in line:
                objects_completed.append(line.split(" ")[-3].strip())
                object_name = line.split(" ")[-5].strip().split("/")[-1].split(".")[0]
                objects_completed_name.append(object_name)
    return objects_completed, objects_completed_name

def main(subset=0):
    start_idx = max((TOTAL_OBJECTS * subset // TOTAL_RUNS) + 1, START_IDX)
    end_idx = min(TOTAL_OBJECTS * (subset + 1) // TOTAL_RUNS, TOTAL_OBJECTS)
    assert start_idx <= end_idx, "start_idx {} must be less than or equal to end_idx {}".format(start_idx, end_idx)


    print("============= Subset {} =============".format(subset))
    print("Launching collision shape automation tool for objects {} to {}".format(start_idx, end_idx))

    launch_run(start_idx, end_idx)

def finish_leftover_objects(idx):
    leftover_objects = [865, 916, 967, 1010, 1011, 1018, 1069, 1116, 1120, 1158, \
    1163, 1170, 1176, 1203, 1221, 1240, 1272, 1323, 1374, 1425, 1459, 1476, 1490, \
    1527, 1529, 1538, 1578, 1605, 1629, 1680, 1719, 1730, 1765, 1771, 1775, 1781, \
    1782, 1783, 1784, 1785, 1786, 1787, 1788, 1789, 1790, 1791, 1792, 1793, 1794, \
    1795, 1796, 1797, 1798, 1799, 1800, 1801, 1802, 1803, 1804, 1805, 1806, 1807, \
    1808, 1809, 1810, 1811, 1812, 1813, 1814, 1815, 1816, 1817, 1818, 1819, 1820, \
    1821, 1822, 1823, 1824, 1825, 1826, 1827, 1828, 1829, 1830, 1831, 1832, 1883, \
    1893, 1934, 1985, 2036, 2087, 2138, 2189, 2240, 2267, 2289, 2290, 2341, 2346, \
    2363, 2392, 2403, 2443, 2494, 2545, 2546, 2596, 2647, 2698, 2749, 2764, 2800, \
    2850, 2901, 2952, 2958, 3003, 3050, 3054, 3105, 3156, 3191, 3207, 3224, 3258, \
    3276, 3309, 3360, 3410, 3461, 3498, 3512, 3563, 3614, 3665, 3716, 3767, 3818, \
    3869, 3920, 3970, 4021, 4072, 4123, 4174, 4214, 4216, 4221, 4225, 4237, 4276, \
    4327, 4378, 4379, 4380, 4381, 4382, 4383, 4384, 4385, 4386, 4387, 4388, 4389, \
    4390, 4391, 4392, 4393, 4394, 4395, 4396, 4397, 4398, 4399, 4400, 4401, 4402, \
    4403, 4404, 4405, 4406, 4407, 4408, 4409, 4410, 4411, 4412, 4413, 4414, 4415, \
    4416, 4417, 4418, 4419, 4420, 4421, 4422, 4423, 4424, 4425, 4426, 4427, 4428, \
    4429, 4454, 4480, 4499, 4514, 4530, 4566, 4581, 4609, 4632, 4683, 4734, 4744, \
    4785, 4817, 4836, 4841, 4886, 4887, 4938, 4989, 4995, 5040, 5091]
    
    launch_run(leftover_objects[idx], leftover_objects[idx] + 1)

def launch_run(start_idx, end_idx):
    # launch a python program in the terminal 
    subprocess.run([
        "python", "../tools/collision_shape_automation.py",
        "--dataset", "../../fphab/fphab/fphab.scene_dataset_config.json",
        "--all-rec-objects",
        "--exclude-files", "../troublesome_object_ids.txt",
        "--start-ix", str(start_idx),
        "--end-ix", str(end_idx)
    ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--subset", type=int, default=0)
    parser.add_argument("--logs-path", type=str,
        default="/private/home/alexclegg/habitat-sim/collision_shape_automation/slurm_logs/")
    parser.add_argument("--launch_script", action="store_true")
    parser.add_argument("--read_logs", action="store_true")
    args = parser.parse_args()
    
    if args.launch_script:
        # main(args.subset)
        finish_leftover_objects(args.subset)
    
    if args.read_logs:
        read_log_files(args.logs_path)