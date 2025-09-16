import cv2 as cv
import numpy as np
import glob
import os
import random
import re
import config
import csv

def get_foggy_img(img, distance_map, beta):
    # Assuming that RGB image is smaller or equal to sift/flow images it can be resized for faster processing.
    if img.shape[0] > project_config.SIFT_FLOW_IMG_HEIGHT or img.shape[1] > project_config.SIFT_FLOW_IMG_WIDTH:
        img = cv.resize(img, (project_config.SIFT_FLOW_IMG_WIDTH, project_config.SIFT_FLOW_IMG_HEIGHT))
        distance_map = cv.resize(distance_map, (project_config.SIFT_FLOW_IMG_WIDTH, project_config.SIFT_FLOW_IMG_HEIGHT))

    img_fogged = img.copy()

    width = img.shape[1]
    height = img.shape[0]

    # Semantic Foggy Scene Understanding with Synthetic Data
    # DOI: 10.1007/s11263-018-1072-8
    # https://arxiv.org/abs/1708.07819
    for x in range(width):
        for y in range(height):
            t = np.exp(-beta * (255-distance_map[y - 1, x - 1]))
            val = t * img[y, x] + 255 * (1 - t)
            img_fogged[y, x] = val
    return img_fogged

def get_next_frame_name(img_name):
    try:
        regex = re.split('(\d+)', img_name)
        idx = str(int(regex[1]) + 1)
        # Filename in a datasets expects 6 digits at the end
        zeros = "0" * (6 - len(idx))
        return regex[0] + zeros + idx
    except:
        return None

def get_sift_img(img):
    img_copy = img.copy()
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img_gray = cv.resize(img, (project_config.SIFT_FLOW_IMG_WIDTH, project_config.SIFT_FLOW_IMG_HEIGHT))

    sift = cv.SIFT_create()
    kp = sift.detect(img_gray, None)
    img_sift = cv.drawKeypoints(img_gray, kp, img_copy)
    return img_sift

def get_flow_img(img, next_img):
    img_gray = cv.resize(img, (project_config.SIFT_FLOW_IMG_WIDTH, project_config.SIFT_FLOW_IMG_HEIGHT))
    hsv = np.zeros_like(img_gray)
    img_gray = cv.cvtColor(img_gray,cv.COLOR_BGR2GRAY)
    
    next_img_gray = cv.resize(next_img, (project_config.SIFT_FLOW_IMG_WIDTH, project_config.SIFT_FLOW_IMG_HEIGHT))
    next_img_gray = cv.cvtColor(next_img_gray,cv.COLOR_BGR2GRAY)
    
    flow = cv.calcOpticalFlowFarneback(img_gray, next_img_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    mag, ang = cv.cartToPolar(flow[...,0], flow[...,1])
    
    hsv[...,1] = 255
    hsv[...,0] = ang * 180/ np.pi / 2
    hsv[...,2] = cv.normalize(mag, None, 0, 255, cv.NORM_MINMAX)

    img_flow = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
    return img_flow

def process_folder(images_folder, idx):
    print("Processing %s..." % images_folder)
    rgb_img_path = os.path.join(images_folder, "raw")
    depth_img_path = os.path.join(images_folder, "depth")
    rgb_files = glob.glob(os.path.join(rgb_img_path, "image*.jpg"))

    for rgb_path in rgb_files:
        rgb_sample_name_no_extension = os.path.basename(rgb_path).split(".")[0]
        depth_path = os.path.join(depth_img_path, rgb_sample_name_no_extension + "_depth.png")

        print("Processing %s (%s)" % (rgb_sample_name_no_extension, str(idx)))

        # Roll fog density
        beta_idx = random.randrange(0, len(project_config.BETAS))
        beta = random.uniform(0, 1) * project_config.BETAS[beta_idx]
        print("Selected fog density: %s" % project_config.BETAS_STR[beta_idx])
        print("BETA is %f" % beta)

        if(not os.path.exists(depth_path)):
            print("No depth data for %s, skipping processing" % rgb_sample_name_no_extension)
            continue

        img_rgb = cv.imread(rgb_path)
        img_depth = cv.imread(depth_path, cv.IMREAD_GRAYSCALE)

        # Apply artificial fog
        img_fogged = get_foggy_img(img_rgb, img_depth, beta)
            
        # SIFT 
        img_sift = get_sift_img(img_fogged)
            
        # Optical Flow
        rgb_sample_next_name_no_extension = get_next_frame_name(rgb_sample_name_no_extension)
        if not rgb_sample_next_name_no_extension:
            print("Failed to get next frame name for %s" % rgb_sample_name_no_extension)
            continue
            
        rgb_next_sample_path = os.path.join(rgb_img_path, rgb_sample_next_name_no_extension + ".jpg")
        if(not os.path.exists(rgb_next_sample_path)):
            print("No next frame for %s, skipping processing" % rgb_sample_name_no_extension)
            continue

        rgb_next_sample_depth_path = os.path.join(depth_img_path, rgb_sample_next_name_no_extension + "_depth.png")
        if(not os.path.exists(rgb_next_sample_depth_path)):
            print("No next frame depth data for %s, skipping processing" % rgb_sample_name_no_extension)
            continue

        img_rgb_next = cv.imread(rgb_next_sample_path)
        img_depth_next = cv.imread(rgb_next_sample_depth_path)
        img_foggy_next = get_foggy_img(img_rgb_next, img_depth_next, beta)

        img_flow = get_flow_img(img_fogged, img_foggy_next)

        # Resize fogged image at the end of processing
        img_fogged = cv.resize(img_fogged, (project_config.RGB_IMG_WIDTH, project_config.RGB_IMG_HEIGHT))

        cv.imwrite(os.path.join(EXPORT_PATH, str(idx) + "_rgb.png"), img_fogged)
        cv.imwrite(os.path.join(EXPORT_PATH, str(idx) + "_sift.png"), img_sift)
        cv.imwrite(os.path.join(EXPORT_PATH, str(idx) + "_flow.png"), img_flow)

        with open(csv_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([str(str(idx))] + [str(project_config.BETAS_STR[beta_idx])] + [str(beta)])

        idx += 1
        print("%s (%s) processed" % (rgb_sample_name_no_extension, str(idx)))

    return idx

if __name__ == "__main__":
    # Non random seed to make generator predictable for each run
    random.seed(1)

    # Dataset paths
    DATASET_PATH = "./dataset/"
    EXPORT_PATH = "./dataset/processed/"
    CSV_PATH = "./dataset/"

    images_folders = glob.glob(DATASET_PATH + "traffic_0*")
    print("Found %d image folders" % len(images_folders))

    if not os.path.exists(EXPORT_PATH):
        print("Creating %s" % EXPORT_PATH)
        os.makedirs(EXPORT_PATH)
    else:
        print("%s already existr" % EXPORT_PATH)

    csv_path = os.path.join(CSV_PATH, "labels.csv")
    if(os.path.exists(csv_path)):
        print("Removing old %s" % csv_path)
        os.remove(csv_path)

    idx = 0
    for images_folder in images_folders:
        idx = process_folder(images_folder, idx)
        

        