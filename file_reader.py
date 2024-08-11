import json

class JsonFileHandler:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_json(self):
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file: {self.file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def write_json(self, new_data):
        try:
            # Read the current data
            current_data = self.read_json()
            if not isinstance(current_data, list):
                # THIS SHOULD NEVER HAPPENS BUT JUST IN CASE
                current_data = [current_data]
            
            # Append the new data
            if isinstance(new_data, list):
                current_data.extend(new_data)
            else:
                current_data.append(new_data)
            
            # Write the updated data back to the file
            with open(self.file_path, 'w') as file:
                json.dump(current_data, file, indent=4)
        except Exception as e:
            print(f"An error occurred while writing to the file: {e}")