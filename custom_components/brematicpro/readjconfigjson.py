import json
import os

def read_and_transform_json(path):
    try:
        with open(path, 'r') as file:
            data = json.load(file)
            transformed_data = []
            for item in data.values():
                # Set frequency based on sys value, default to 0 if neither B8 nor B4
                if item['sys'] == 'B8':
                    freq = 868
                elif item['sys'] == 'B4':
                    freq = 433
                else:
                    freq = 0

                # Augment command URLs with the local value
                commands = {cmd: item['local'] + item['commands'][cmd]['url'] for cmd in item['commands']}

                transformed_data.append({
                    "uniqueid": item['address'],
                    "name": item['name'],
                    "freq": freq,
                    "type": item['type'],
                    "commands": commands
                })
            return transformed_data
    except FileNotFoundError:
        print("File not found.")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def save_data_to_file(data, output_path):
    try:
        with open(output_path, 'w') as file:
            json.dump(data, file, indent=2)
        print(f"Data successfully saved to {output_path}")
    except Exception as e:
        print(f"Failed to write data to file: {e}")

# Define the path to the JSON file, assuming it's two directories above the current directory
file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'BrematicPro.json')

# Define the path for the output JSON file
output_path = os.path.join(os.path.dirname(__file__), 'BrematicProDevices.json')

# Transform the data
transformed_data = read_and_transform_json(file_path)

# Save the transformed data to a file
if transformed_data is not None:
    save_data_to_file(transformed_data, output_path)
else:
   print("No data to save.")
