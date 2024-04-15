

# Import module
import os
 
# Assign directory
directory = "GTFS_Realtime"
 
# Iterate over files in directory
for name in os.listdir(directory):
    # Open file
    with open(os.path.join(directory, name)) as f:
        print(name)
        # Read content of file
  