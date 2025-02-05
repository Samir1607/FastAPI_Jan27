import os

file_paths = [
    'F:\\FastAPI Pizza Delivery API\\auth_routes.py',
    'F:\\FastAPI Pizza Delivery API\\database.py',
    'F:\\FastAPI Pizza Delivery API\\main.py',
    'F:\\FastAPI Pizza Delivery API\\order_routes.py',
    'F:\\FastAPI Pizza Delivery API\\pizza_delivery.db',
    'F:\\FastAPI Pizza Delivery API\\pizza_models.py',
    'F:\\FastAPI Pizza Delivery API\\requirements.txt',
    'F:\\FastAPI Pizza Delivery API\\schemas.py'
]

# Creating or opening the allcode.py file in write mode
with open('allcode.py', 'w') as output_file:
    for path in file_paths:
        try:
            with open(path, 'r') as file:
                # Using os.path.basename() to get the file name
                output_file.write(f"# {os.path.basename(path)}\n")
                # Writing the content of the file
                output_file.write(file.read())
                # Adding 10 new lines after each file's content
                output_file.write("\n" * 10)
        except Exception as e:
            output_file.write(f"# Could not read {path}: {e}\n")
