import datetime
import os
import json



class combine_pretty:
    def __init__(self):
        pass

    def build_pages(self, date, start_folder):
        temp_leads = self.get_leads(date, start_folder)
        temp_moveset = self.get_moveset(date, start_folder)
        temp_usage = self.get_usage(date, start_folder)
        page = self.combine_data(leads=temp_leads, moveset=temp_moveset, usage=temp_usage, date=date,start_folder= start_folder)
        #self.save_file(page)
        return(page)


    def get_leads(self, date, start_folder):
        # Define the path to the leads.json file
        leads_file_path = os.path.join(start_folder, date, 'pretty/leads.json')
        # Check if the leads.json file exists
        if not os.path.isfile(leads_file_path):
            print(f"Error: File '{leads_file_path}' not found.")
            return {}

        # Load and process the leads.json file
        with open(leads_file_path, 'r') as file:
            leads_data = json.load(file)

        # Check if the required keys exist in the leads_data dictionary
        if 'total_leads' not in leads_data or 'pokemon_data' not in leads_data:
            print(f"Error: Invalid format in '{leads_file_path}'.")
            return {}

        # Process and transform the pokemon_data dictionary
        transformed_pokemon_data = {}
        for pokemon, stats in leads_data['pokemon_data'].items():
            transformed_stats = {
                f"leads_{key}": value for key, value in stats.items()
            }
            transformed_pokemon_data[pokemon] = transformed_stats

        # Construct the result dictionary with transformed pokemon_data
        result = {
            'total_leads': leads_data['total_leads'],
            'pokemon_data': transformed_pokemon_data
        }

        return result

    def get_moveset(self, date, start_folder):
        # Define the path to the moveset.json file
        moveset_file_path = os.path.join(start_folder, date, 'pretty/moveset.json')

        # Check if the moveset.json file exists
        if not os.path.isfile(moveset_file_path):
            print(f"Error: File '{moveset_file_path}' not found.")
            return []

        # Load and process the moveset.json file
        moveset_data = []
        try:
            with open(moveset_file_path, 'r') as file:
                moveset_data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in '{moveset_file_path}': {e}")
        except FileNotFoundError:
            print(f"Error: File '{moveset_file_path}' not found.")

        # Transform the moveset_data list of dictionaries
        transformed_moveset_data = []
        for entry in moveset_data:
            if 'raw_count' in entry:
                entry['moveset_raw_count'] = entry.pop('raw_count')  # Rename 'raw_count' to 'moveset_raw_count'
            transformed_moveset_data.append(entry)

        return transformed_moveset_data

    def get_usage(self, date, start_folder):
        # Define the path to the usage.json file
        usage_file_path = os.path.join(start_folder, date, 'pretty/usage.json')
        # Check if the usage.json file exists
        if not os.path.isfile(usage_file_path):
            print(f"Error: File '{usage_file_path}' not found.")
            return {}

        # Load and process the usage.json file
        with open(usage_file_path, 'r') as file:
            usage_data = json.load(file)

        # Check if the required keys exist in the usage dictionary
        #print(date)
        if 'total_battles' not in usage_data or 'pokemon_data' not in usage_data:
            print(f"Error: Invalid format in '{usage_file_path}'.")
            return {}

        # Process and transform the pokemon_data dictionary
        transformed_pokemon_data = {}
        for pokemon, stats in usage_data['pokemon_data'].items():
            transformed_stats = {
                f"usage_{key}": value for key, value in stats.items()
            }
            transformed_pokemon_data[pokemon] = transformed_stats

        # Construct the result dictionary with transformed pokemon_data
        result = {
            'usage_total_battles': usage_data['total_battles'],
            'pokemon_data': transformed_pokemon_data
        }

        return result

    def combine_pages(self, leads, moveset, usage, date,start_folder):
        # Implement logic to combine leads, moveset, and usage data into a single page

        combined_page = {
            'date': date,
            'usage_total_battles': usage['usage_total_battles'],
            'total_leads': leads['total_leads'],

        }
        usage_pokemon_data=usage['pokemon_data']
        leads_pokemon_data=leads['pokemon_data']
        moveset_pokemon_data=self.fix_moveset(moveset)
        print(usage_pokemon_data)
        print(leads_pokemon_data)
        print(moveset_pokemon_data)
        combined_page
        return combined_page

    def combine_data(self,date, usage, leads, moveset, start_folder):
        """
        Combines data from usage, leads, and moveset into a single combined dictionary.

        Args:
            date (str): The date associated with the combined data.
            usage (dict): Dictionary containing usage data.
            leads (dict): Dictionary containing leads data.
            moveset (list): List of dictionaries containing moveset data.
            self: Reference to the current object (assuming this is part of a class).

        Returns:
            dict: A combined dictionary containing the merged data.
            :param start_folder:
        """
        # Create a new combined_page dictionary with initial data
        combined_page = {
            'date': date,
            'usage_total_battles': usage['usage_total_battles'],
            'total_leads': leads['total_leads'],
            'location': start_folder
        }

        # Extract data dictionaries from usage, leads, and moveset
        usage_pokemon_data = usage['pokemon_data']
        leads_pokemon_data = leads['pokemon_data']
        moveset_pokemon_data = self.fix_moveset(moveset)

        # Combine data from all dictionaries into a new dictionary
        new_dict = {}

        # Add usage_pokemon_data to new_dict
        new_dict.update(usage_pokemon_data)

        # Add leads_pokemon_data to new_dict
        for pokemon, data in leads_pokemon_data.items():
            if pokemon in new_dict:
                new_dict[pokemon].update(data)  # Update existing entry with leads data
            else:
                new_dict[pokemon] = data  # Add new entry from leads data

        # Add moveset_pokemon_data to new_dict
        for pokemon, data in moveset_pokemon_data.items():
            if pokemon in new_dict:
                new_dict[pokemon].update(data)  # Update existing entry with moveset data
            else:
                new_dict[pokemon] = data  # Add new entry from moveset data

        # Update combined_page dictionary with new_dict
        combined_page['combined_data'] = new_dict

        return combined_page

    def fix_moveset(self,moveset):
        """
        Transforms a list of dictionaries representing moveset data into a dictionary
        where each Pokémon name serves as a key mapping to its corresponding dictionary of attributes.

        Args:
            moveset (list): A list of dictionaries where each dictionary contains 'name' and other attributes.

        Returns:
            dict: A dictionary where each Pokémon name is a key mapping to its attribute dictionary.
        """
        dict1 = {}  # Initialize the result dictionary

        # Convert the list of dictionaries to a single dictionary
        for entry in moveset:
            pokemon_name = entry['name']  # Get the Pokémon name
            # Create a new dictionary for the Pokémon with its attributes
            pokemon_data = {key: value for key, value in entry.items() if key != 'name'}
            # Add the Pokémon data to the main dictionary with the Pokémon name as the key
            dict1[pokemon_name] = pokemon_data

        return dict1

    def save_file(self, page):
        # Implement logic to save the combined page data to a file
        filename = f"combined_page_{page['date']}.json"
        with open(filename, 'w') as file:
            json.dump(page, file, indent=4)
        print(f"Combined page saved to {filename}")

# Main function
def main():
    '''date1 = '2024-01'
    start_folder = 'gen3ou-1760'
    print('hi')
    # Create instance of combine_pretty class
    combiner = combine_pretty()
    print(combiner.get_usage(date=date1,start_folder=start_folder))
    print(combiner.get_moveset(date=date1,start_folder=start_folder))
    print(combiner.get_leads(date=date1,start_folder=start_folder))
    # Build pages for the specified date and start folder
    #combiner.build_pages(date1, start_folder)
    page1=combiner.build_pages(date=date1,start_folder=start_folder)
    # Specify the path where you want to save the JSON file
    output_file_path = 'page1.json'

    # Save 'page1' as a JSON file
    with open(output_file_path, 'w') as json_file:
        json.dump(page1, json_file, indent=4)

    print(f"Saved page1 to '{output_file_path}'")

    start_date = '2014-11'
    end_date = '2015-'
    new_folder = 'gen3oubeta-1760'
    stats_location = 'gen3ou-1760a'
    current_date = datetime.datetime.strptime(start_date, '%Y-%m')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m')
    while current_date <= end_date:
        date1 = current_date.strftime('%Y-%m')
        print(f"Processing date: {date1}")
        page1 = combiner.build_pages(date=date1, start_folder=stats_location)

        output_file_path = os.path.join(new_folder, date1, 'pretty', 'combined.json')
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

        # Save the list as JSON to the specified file path
        with open(output_file_path, 'w') as json_file:
            json.dump(page1, json_file, indent=4)
        # Move to the next month
        current_date += datetime.timedelta(days=32)  # Move to the 1st of the next month'''
if __name__ == '__main__':
    main()
