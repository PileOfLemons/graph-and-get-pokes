import os
import requests
from datetime import datetime, timedelta
from ParseStats import ParseStats
from ReportsPoke import ReportsPoke
from dateutil.relativedelta import relativedelta
class PileOfLemons:
    def __init__(self, start_date, end_date, format_value, ranking):
        self.start_date = datetime.strptime(start_date, '%Y-%m')
        self.end_date = datetime.strptime(end_date, '%Y-%m')
        self.format_value = format_value
        self.ranking = ranking
        self.form_rank = f"{format_value}-{ranking}"
        self.folder_path = self.form_rank
        self.smogon_link = 'https://www.smogon.com/stats/'

    def get_files(self):
        current_date = self.start_date
        while current_date <= self.end_date:
            # Get the folder name for the current month
            folder_name = current_date.strftime('%Y-%m')

            # Print the name of the current month
            month_name = current_date.strftime('%B %Y')
            print(f"Processing files for: {month_name}")

            # Construct URLs for usage, moveset, and leads data
            usage_url = f"{self.smogon_link}{folder_name}/{self.form_rank}.txt"
            moveset_url = f"{self.smogon_link}{folder_name}/moveset/{self.form_rank}.txt"
            leads_url = f"{self.smogon_link}{folder_name}/leads/{self.form_rank}.txt"

            # Create directory if it doesn't exist
            folder_directory = os.path.join(self.folder_path, folder_name)
            os.makedirs(folder_directory, exist_ok=True)

            # Download and save usage.json
            usage_response = requests.get(usage_url)
            if usage_response.status_code == 200:
                with open(os.path.join(folder_directory, 'usage.json'), 'wb') as usage_file:
                    usage_file.write(usage_response.content)

            # Download and save moveset.json
            moveset_response = requests.get(moveset_url)
            if moveset_response.status_code == 200:
                with open(os.path.join(folder_directory, 'moveset.json'), 'wb') as moveset_file:
                    moveset_file.write(moveset_response.content)

            # Download and save leads.json
            leads_response = requests.get(leads_url)
            if leads_response.status_code == 200:
                with open(os.path.join(folder_directory, 'leads.json'), 'wb') as leads_file:
                    leads_file.write(leads_response.content)

            # Move to the next month using relativedelta to handle month transitions
            current_date += relativedelta(months=1)

        # After the loop, all required files should have been downloaded
        print("All files downloaded successfully.")

def main():
    start_date1 = '2020-01'
    end_date1 = '2022-01'
    format_value1 = 'gen8ru'
    ranking1 = '1760'
    lemon = PileOfLemons(start_date1, end_date1, format_value1, ranking1)
    top_count=10 #HOW MANY POKEMON DO YOU WANT ON THE GRAPH
    lemon.get_files()

    parser = ParseStats(start_date=lemon.start_date, end_date=lemon.end_date, new_folder=lemon.form_rank,
                        stats_location=lemon.form_rank,
                        format_value=lemon.format_value, ranking=lemon.ranking)
    parser.iterate_date_range()
    reporter = ReportsPoke(lemon.form_rank, top_count)
    # Convert datetime objects to strings for analyze_top_pokemon_ranks
    start_date_str = lemon.start_date.strftime('%Y-%m')
    end_date_str = lemon.end_date.strftime('%Y-%m')

    # Analyze top Pokémon rankings across the specified date range
    reporter.analyze_top_pokemon_ranks(start_date_str, end_date_str)

    # Plot monthly rankings with multiple pages
    reporter.plot_monthly_rankings()

if __name__ == "__main__":
    main()
