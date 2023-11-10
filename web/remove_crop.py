import argparse
import os, os.path

#Sample Usage
#python remove_crop.py --s "D:/saved_img/pick_up_truck/"

#A very small program to remove corrupt image
def remove(path):
    #Fine files in the path
    for root, _, files in os.walk(path):
        # get the full path
        for f in files:
            fullpath = os.path.join(root, f)
            #remove
            try:
                #set file size in kb
                if os.path.getsize(fullpath) < 10 * 1024:
                    print(fullpath)
                    os.remove(fullpath)
            except WindowsError:
                print("Error" + fullpath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--s",
        help="This is path of where you saved the image. End with /")
    args = parser.parse_args()

    path = args.s
    remove(path)
