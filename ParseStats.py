import os
import json
import datetime
import ParseLeads
import ParseMoveset
import CombinePretty
from dateutil.relativedelta import relativedelta


class ParseStats:
    def __init__(self, start_date, end_date, new_folder, stats_location, format_value, ranking):
        self.start_date = start_date
        self.end_date = end_date
        self.new_folder = new_folder
        self.stats_location = stats_location
        self.format_value = format_value
        self.ranking = ranking
        self.remaining = f"{format_value}-{ranking}"

    def iterate_date_range(self):
        current_date = self.start_date

        while current_date <= self.end_date:
            date_str = current_date.strftime('%Y-%m')
            print(f"Processing date: {date_str}")

            # Process usage stats if the file exists
            print(self.remaining)
            usage_file_path = os.path.join(self.stats_location, date_str, "usage.json")
            if os.path.exists(usage_file_path):
                self.process_stats(usage_file_path, 'usage', date_str)

            # Process leads stats if the file exists
            leads_file_path = os.path.join(self.stats_location, date_str, 'leads.json')
            if os.path.exists(leads_file_path):
                self.process_stats(leads_file_path, 'leads', date_str)

            # Process moveset stats if the file exists
            moveset_file_path = os.path.join(self.stats_location, date_str, "moveset.json")
            if os.path.exists(moveset_file_path):
                self.process_stats(moveset_file_path, 'moveset', date_str)

            # Combine these new files
            self.combine_three(date_str)

            # Move to the next month
            current_date += relativedelta(months=1)

    def combine_three(self, date1):
        combiner = CombinePretty.combine_pretty()
        page1 = combiner.build_pages(date=date1, start_folder=self.new_folder)
        output_file_path = os.path.join(self.new_folder, date1, 'pretty', 'combined.json')
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

        # Save the list as JSON to the specified file path
        with open(output_file_path, 'w') as json_file:
            json.dump(page1, json_file, indent=4)
        print(f"Saved combined data for {date1} to {output_file_path}")

    def process_stats(self, input_file_path, stats_type, date1):
        # Determine which parser to use based on stats_type
        if stats_type == 'usage':
            parser = ParseLeads.ParseLeads(input_file_path)
            parsed_data = parser.parse_usage()

        elif stats_type == 'leads':
            parser = ParseLeads.ParseLeads(input_file_path)
            parsed_data = parser.parse_leads()
        elif stats_type == 'moveset':
            parser = ParseMoveset.ParseMoveset(input_file_path)
            parsed_data = parser.sections_to_list_of_dicts(parser.split_sections_from_file(input_file_path))
        else:
            raise ValueError(f"Unsupported stats_type: {stats_type}")

        # Parse and retrieve result dictionary
        '''if stats_type == 'usage':
            print(parsed_data)'''
        result_dict = parsed_data

        # Save the processed data as JSON
        output_folder = os.path.join(self.new_folder, date1, 'pretty')
        os.makedirs(output_folder, exist_ok=True)
        output_file_path = os.path.join(output_folder, f'{stats_type}.json')

        with open(output_file_path, 'w') as json_file:
            json.dump(result_dict, json_file, indent=4)

        print(f"Saved {stats_type} data for {date1} to {output_file_path}")

'''
nstart_date = '2015-04'
nend_date = '2024-03'
nnew_folder = 'gen3ou-1760'
nstats_location = 'stats'
nformat_value = 'gen3ou'
nranking = '1760'
parser = ParseStats(start_date=nstart_date, end_date=nend_date, new_folder=nnew_folder, stats_location=nstats_location,
                    format_value=nformat_value, ranking=nranking)
parser.iterate_date_range()'''
