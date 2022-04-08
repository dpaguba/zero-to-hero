# to work with the operating system
import os

# change the current directory. move to the directory indicated in brackets
os.chdir("")

# show all folders in the current directory
# print(os.listdir())

# go through all the folders in this directory
for folder in os.listdir():
    # if the given file is a folder, then split the folder name by spaces
    if os.path.isdir(folder):
        parts = folder.split(" ")
        # rename the file so that the last part of the name becomes the first
        os.rename(folder, parts[-1] + "-" + parts[0] + "-" + parts[1])
