import shutil
import json
from datetime import datetime
import os
import datetime


class ParseMoveset:
    def __init__(self, filename):
        self.filename = filename

    def split_sections_from_file(self, file_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the currently executing script
        full_path = os.path.join(script_dir, file_path)  # Combine with the relative path to get the full path

        sections = []
        with open(full_path, 'r') as file:
            lines = file.readlines()
            start_index = None

            for i, line in enumerate(lines):
                if "Raw count:" in line:
                    if start_index is not None:
                        section = [line.strip().replace('|', '') for line in lines[start_index - 3:i - 3] if
                                   not line.startswith('+') and '+' not in line]
                        sections.append(section)
                    start_index = i

            if start_index is not None:
                section = [line.strip().replace('|', '') for line in lines[start_index - 3:] if
                           not line.startswith('+') and '+' not in line]
                sections.append(section)

        return sections

    def sections_to_list_of_dicts(self, sections, link='none'):
        page = []
        for section in sections:
            input_text = ('\n'.join(section))
            sections = self.split_into_sections(input_text)
            cleansections = self.clean_sections(sections)
            newdict = self.parse_sections(cleansections, link)
            page.append(newdict)
        return (page)

    def format_section(self, section):
        max_width = 80  # Maximum width for each line
        formatted_section = []
        for line in section:
            if len(line) > max_width:
                formatted_line = ""
                words = line.split()
                current_width = 0
                for word in words:
                    if current_width + len(word) <= max_width:
                        formatted_line += word + " "
                        current_width += len(word) + 1
                    else:
                        formatted_section.append(formatted_line.strip())
                        formatted_line = word + " "
                        current_width = len(word) + 1
                if formatted_line:
                    formatted_section.append(formatted_line.strip())
            else:
                formatted_section.append(line)
        return formatted_section

    def split_into_sections(self, input_text):
        sections = []
        current_section = []
        section_start_phrases = ["Viability Ceiling", "Abilities", "Items", "Spreads", "Moves", "Teammates",
                                 "Checks and Counters"]

        for line in input_text.split('\n'):
            line = line.strip()  # Trim leading and trailing whitespace
            if any(phrase.lower() in line.lower() for phrase in section_start_phrases):
                if current_section:
                    sections.append(current_section)
                current_section = [line]
            else:
                current_section.append(line)

        if current_section:
            sections.append(current_section)

        sections = [[line.rstrip().rstrip('_') for line in section] for section in
                    sections]  # Remove trailing whitespace from each line
        sections = [section for section in sections if section]  # Remove empty sections

        return sections

    def clean_sections(self, sections):
        cleaned_sections = []
        for section in sections:

            if isinstance(section, dict):
                cleaned_section = {}
                for key, value in section.items():
                    # Clean the key only if value is a dictionary
                    cleaned_key = key.lower().replace(' ', '_').rstrip('_')
                    if isinstance(value, dict):
                        cleaned_value = self.clean_sections(value)  # Recursively clean nested dictionaries
                    else:
                        cleaned_value = value  # Pass through non-dictionary values unchanged
                    cleaned_section[cleaned_key] = cleaned_value
                cleaned_sections.append(cleaned_section)
            else:
                cleaned_sections.append(section)  # Pass through non-dictionary sections unchanged
        # print(cleaned_sections)
        return cleaned_sections

    def parse_sections(self, data, link='None'):
        # Check if data contains the expected number of sections
        x = 0
        if len(data) < 2:
            print("Insufficient sections in data:", data)
            return {}  # Return an empty dictionary if there are not enough sections

        dict = {}
        section0 = data[0]
        section1 = data[1]

        # Check if sections contain the expected number of elements
        if len(section0) < 3 or len(section1) < 1:
            print("Invalid format for sections:", data)
            return {}  # Return an empty dictionary if sections are not properly formatted

        dict['name'] = section0[0]
        dict['raw_count'] = int(section0[1].split(': ')[1])
        dict['avg_weight'] = section0[2].split(': ')[1]
        try:
            dict['viability_ceiling'] = int(section1[0].split(': ')[1])
        except IndexError:
            # print("IndexError: section0 =", section0)
            # print(link)
            x = -1
            dict['viability_ceiling'] = 0
            # Return an empty dictionary if section1 is empty or doesn't contain enough elements

        # Ensure sections are properly formatted before accessing them
        if len(data) >= 7:
            section2 = data[2 + x]
            section3 = data[3 + x]
            section4 = data[4 + x]
            section5 = data[5 + x]

            dict['abilities'] = self.add_ability_counts(self.update_ability_count(section2, dict['raw_count']))
            dict['items'] = self.add_ability_counts(self.update_ability_count(section3, dict['raw_count']))
            dict['spreads'] = self.add_ability_counts(self.update_ability_count(section4, dict['raw_count']))
            dict['moves'] = self.add_ability_counts(self.update_ability_count(section5, dict['raw_count']))

        return dict

    def update_ability_count(self, abilities, count):
        # Check if the abilities list is empty
        if not abilities:
            return []

        # Remove the first entry
        abilities.pop(0)

        updated_abilities = []
        for entry in abilities:
            parts = entry.split(' ')
            if len(parts) < 2:  # If entry does not split into at least two parts
                print(f"Skipping invalid entry: {entry}")
                continue

            name = '_'.join(parts[:-1])  # Replace spaces with underscores in the name
            percent_with_symbol = parts[-1]  # Extract percentage with percent symbol

            # Remove the percentage symbol to get the float value of the percentage
            percent_str = percent_with_symbol[:-1]

            try:
                percent = float(percent_str)  # Convert the percentage string to a float
            except ValueError:
                print(f"Skipping invalid percentage: {percent_str}")
                continue

            updated_entry = f'{name} {percent:.3f}'  # Format the updated entry
            updated_abilities.append(updated_entry)

        return updated_abilities

    def add_ability_counts(self, abilities_list):
        sorted_dict = {}
        dictionary = {}
        for entry in abilities_list:
            parts = entry.split(' ')
            if len(parts) != 2:
                print(f"Skipping invalid entry: {entry}")
                continue

            key, value = parts
            try:
                value = float(value)
            except ValueError:
                print(f"Skipping invalid value: {value}")
                continue
            cleaned_key = key.lower().replace(' ', '_').rstrip('_')
            dictionary[cleaned_key] = value
            sorted_dict = dict(sorted(dictionary.items(), key=lambda item: item[1], reverse=True))
        return sorted_dict

    def combine_dicts(self, dict1, dict2):
        combined_dict = {}

        # Get 'Avg. weight' from dict1 and dict2 with default values of 0
        dict1_weight = float(dict1.get('avg_weight', 0)) * dict1.get('raw_count', 1)
        dict2_weight = float(dict2.get('avg_weight', 0)) * dict2.get('raw_count', 1)
        dict3_weight = dict1_weight + dict2_weight

        # Get 'Viability ceiling' from dict1 and dict2 with default value of 0
        dict1_via = float(dict1.get('viability_ceiling', 0))
        dict2_via = float(dict2.get('viability_ceiling', 0))
        dict3_via = max(dict1_via, dict2_via)

        # Combine dictionaries
        for key in dict1:
            if key in dict2:
                if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                    combined_dict[key] = {}
                    for inner_key in dict1[key]:
                        if inner_key in dict2[key]:
                            combined_dict[key][inner_key] = dict1[key][inner_key] + dict2[key][inner_key]
                        else:
                            combined_dict[key][inner_key] = dict1[key][inner_key]
                    for inner_key in dict2[key]:
                        if inner_key not in combined_dict[key]:
                            combined_dict[key][inner_key] = dict2[key][inner_key]
                else:
                    if key != 'avg_weight' and key != 'name':
                        combined_dict[key] = dict1[key] + dict2[key]
                    else:
                        combined_dict[key] = dict1[key]
            else:
                combined_dict[key] = dict1[key]

        for key in dict2:
            if key not in combined_dict:
                combined_dict[key] = dict2[key]

        # Calculate 'Avg. weight' for combined dictionary
        combined_dict['avg_weight'] = dict3_weight / (dict1.get('raw_count', 1) + dict2.get('raw_count', 1))
        combined_dict['viability_ceiling'] = dict3_via

        return combined_dict

    def compare_and_combine(self, list1, list2):
        page3 = []

        for dict1 in list1:
            found_match = False
            for dict2 in list2:
                if dict1.get('name') == dict2.get('name'):
                    combined_dict = self.combine_dicts(dict1, dict2)
                    page3.append(combined_dict)
                    found_match = True
                    break
            if not found_match:
                page3.append(dict1)

        for dict2 in list2:
            found_match = False
            for dict1 in list1:
                if dict2.get('name') == dict1.get('name'):
                    found_match = True
                    break
            if not found_match:
                page3.append(dict2)

        return page3

    def sort_list_by_raw_count(self, list_of_dicts):
        sorted_list = sorted(list_of_dicts, key=lambda x: x.get('Raw count', 0), reverse=True)
        return sorted_list

    def find_json_files(self, root_folder):
        json_files = []
        for root, dirs, files in os.walk(root_folder):
            for dir_name in dirs:
                moveset_folder = os.path.join(root, dir_name, 'moveset')
                if os.path.exists(moveset_folder):
                    json_file_path = os.path.join(moveset_folder, 'gen3ou-1760.json')
                    if os.path.isfile(json_file_path):
                        json_files.append(json_file_path)
        return json_files

    def combine_pages(self, page_list):
        """

        :param page_list:
        :return:
        """
        combined_page = []
        for link in page_list:
            # print(link)
            page = self.sections_to_list_of_dicts(self.split_sections_from_file(link), link)
            # print(page)
            combined_page = self.compare_and_combine(combined_page, page)
        return combined_page

    def find_move(self, page_list, move, pokemonname):
        for link in page_list:
            page = self.sections_to_list_of_dicts(self.split_sections_from_file(link), link)
            for pokemon in page:
                # Convert the entire dictionary to lowercase recursively
                pokemon_lower = self.recursive_lower(pokemon)

                # Check if the lowercase 'name' key in the dictionary is 'tyranitar'
                if pokemon_lower.get('name') == pokemonname:
                    # print(pokemon_lower)
                    # Check if there is a lowercase 'move' key and if it's a dictionary
                    if 'moves' in pokemon_lower and isinstance(pokemon_lower['moves'], dict):
                        # Check if the lowercase 'attract' key exists in the lowercase 'move' dictionary
                        if move in pokemon_lower['moves']:
                            print(link)

    def find_spread(self, page_list, spread, pokemonname):
        for link in page_list:
            page = self.sections_to_list_of_dicts(self.split_sections_from_file(link), link)
            for pokemon in page:
                # Convert the entire dictionary to lowercase recursively
                pokemon_lower = self.recursive_lower(pokemon)

                # Check if the lowercase 'name' key in the dictionary is 'tyranitar'
                if pokemon_lower.get('name') == pokemonname:
                    # print(pokemon_lower)
                    # Check if there is a lowercase 'move' key and if it's a dictionary
                    if 'moves' in pokemon_lower and isinstance(pokemon_lower['spreads'], dict):
                        # Check if the lowercase 'attract' key exists in the lowercase 'move' dictionary
                        if spread in pokemon_lower['spreads']:
                            print(link)
                            print(pokemon_lower['spreads'])

    def recursive_lower(self, d):
        if isinstance(d, dict):
            return {k.lower(): self.recursive_lower(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [self.recursive_lower(i) for i in d]
        elif isinstance(d, str):
            return d.lower()
        else:
            return d

    def save_to_json(self, data, filename="new_all_moveset2.json"):
        # Filter dictionaries that have a 'Name' key
        filtered_data = [d for d in data if 'name' in d]

        # Sort the filtered data by the 'Raw count' key
        sorted_data = sorted(filtered_data, key=lambda x: x.get('raw_count', 0), reverse=True)

        with open(filename, 'w') as json_file:
            json.dump(sorted_data, json_file, indent=4)

    def clean_dict(self, dictionary, keyname, raw_count=0, ):
        """
        Process a dictionary by converting numeric values to integers, calculating percentages,
        sorting by highest value, and returning the sorted dictionary.

        Args:
            dictionary (dict): The input dictionary with numeric values.

        Returns:
            dict: The sorted dictionary by highest value.
            :param dictionary:
            :param keyname:
            :param raw_count:
            :return:
        """
        # Step 1: Convert all numeric values to integers and compute total_count
        total_count = sum(int(value) for key, value in dictionary.items() if
                          isinstance(value, (int, float)) and 'other' not in key.lower())
        # Step 2: Calculate percentage for each value
        num = raw_count - total_count
        print(f"Name: {keyname}, Difference: {num}")
        if (keyname == 'moves'):
            percent_dict = {
                key: round((int(value) / raw_count) * 100, 3)
                for key, value in dictionary.items()
                if isinstance(value, (int, float)) and 'other' not in key.lower()
            }
        else:
            percent_dict = {
                key: round((int(value) / total_count) * 100, 3)
                for key, value in dictionary.items()
                if isinstance(value, (int, float)) and 'other' not in key.lower()
            }
        # Step 3: Sort the dictionary by highest value (descending order)
        sorted_dict = dict(sorted(percent_dict.items(), key=lambda item: item[1], reverse=True))

        return sorted_dict

    def clean_nested_dicts(self, dictionary):
        """
        Recursively clean all nested dictionaries within the input dictionary.

        Args:
            dictionary (dict): The input dictionary possibly containing nested dictionaries.

        Returns:
            dict: The cleaned dictionary with all nested dictionaries processed.
        """
        cleaned_dictionary = {}

        for key, value in dictionary.items():
            if isinstance(value, dict):
                # Recursively clean the nested dictionary
                cleaned_value = self.clean_dict(dictionary=value, raw_count=dictionary['raw_count'], keyname=key)
            else:
                cleaned_value = value  # Keep non-dictionary values unchanged

            cleaned_dictionary[key] = cleaned_value

        return cleaned_dictionary

    def clean_page(self, page):
        """
        Clean a list of dictionaries (page) by processing each dictionary.

        Args:
            page (list): A list of dictionaries to be cleaned.

        Returns:
            list: The cleaned list of dictionaries with nested dictionaries processed.
        """
        cleaned_page = []

        for dictionary in page:
            cleaned_dict = self.clean_nested_dicts(dictionary)
            cleaned_page.append(cleaned_dict)

        return cleaned_page

    def final_tidy(self, page):
        for dicts in page:
            dicts['avg_weight'] = 0
        return page

    def restructure_stats(self, new_folder, stats_location, date1, format_value, ranking):
        """
        Restructures statistics files based on specified parameters.

        Args:
            new_folder (str): Path to the folder where restructured files will be saved.
            stats_location (str): Path to the location of original statistics files.
            date1 (str): Date identifier for the statistics files (e.g., '2024-01').
            format_value (str): Format value used in filename generation (e.g., 'gen3ou').
            ranking (str): Ranking value used in filename generation (e.g., '1760').

        Returns:
            None
        """
        # Generate the REMAINING filename
        remaining = f"{format_value}-{ranking}.json"

        folder_names = ['moveset', 'leads', 'chaos', 'metagame']

        # Iterate over each folder name
        for name in folder_names:
            # Construct the result_string path with .json extension
            result_string = os.path.join(stats_location, date1, name, remaining)

            # Check if the file exists
            if not os.path.exists(result_string):
                print(f"Error: File '{result_string}' not found.")
                continue

            # Construct the new file path under gen3ou-1760 with .json extension
            new_file_path = os.path.join(new_folder, date1, f"{name}.json")

            # Create the directories if they don't exist
            os.makedirs(os.path.dirname(new_file_path), exist_ok=True)

            # Copy the file to the new location
            try:
                shutil.copyfile(result_string, new_file_path)
                print(f"File saved: {new_file_path}")
            except Exception as e:
                print(f"Error: Failed to copy file from '{result_string}' to '{new_file_path}': {e}")

        # Download and save the usage file
        usage_string = os.path.join(stats_location, date1, remaining)  # Construct usage_string path
        usage_destination = os.path.join(new_folder, date1, "usage.json")  # Set usage_destination path

        try:
            shutil.copyfile(usage_string, usage_destination)
            print(f"Usage file saved: {usage_destination}")
        except Exception as e:
            print(f"Error: Failed to download and save usage file '{usage_string}' to '{usage_destination}': {e}")

    def iterate_date_range(self, start_date, end_date, new_folder, stats_location, format_value, ranking):
        """
        Iterates through a date range and calls restructure_stats for each month.

        Args:
            start_date (str): Start date in YYYY-MM format (e.g., '2014-11').
            end_date (str): End date in YYYY-MM format (e.g., '2024-03').
            new_folder (str): Path to the folder where restructured files will be saved.
            stats_location (str): Path to the location of original statistics files.
            format_value (str): Format value used in filename generation (e.g., 'gen3ou').
            ranking (str): Ranking value used in filename generation (e.g., '1760').

        Returns:
            None
        """
        current_date = datetime.datetime.strptime(start_date, '%Y-%m')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m')

        while current_date <= end_date:
            date1 = current_date.strftime('%Y-%m')
            print(f"Processing date: {date1}")

            # Call restructure_stats with the current date
            self.restructure_stats(new_folder, stats_location, date1, format_value, ranking)

            # Move to the next month
            current_date += datetime.timedelta(days=32)  # Move to the 1st of the next month
