import os

# Replace 'your_directory' with the path of the folder you want to scan
folder_path = 'F:\FastAPI Pizza Delivery API'
output_file = 'path.txt'

with open(output_file, 'w') as f:
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            f.write(file_path + '\n')