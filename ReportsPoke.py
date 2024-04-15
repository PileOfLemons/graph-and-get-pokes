import matplotlib.pyplot as plt
import numpy as np
import json
import os
from datetime import datetime

class ReportsPoke:
    def __init__(self, folder_path, top_count=10):
        self.folder_path = folder_path
        self.top_count = top_count
        self.monthly_rankings = {}
        self.pokemon_colors = {
            'Krookodile': 'yellow',
            'Bulbasaur': 'green',
            'Charmander': 'red',
            'Slowbro': 'magenta',
            'Espeon': 'pink',
            'Flamigo': 'purple',
            'Gengar': 'black',
            'Mewtwo': 'purple',
            'Eevee': 'brown',
            'Dragonite': 'orange'
            # Add more Pokémon names and colors as needed
        }

    def load_data(self, target_date):
        month_label = target_date
        filename = os.path.join(self.folder_path, month_label, 'pretty', 'usage.json')

        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                pokemon_data = data.get('pokemon_data', {})
                # Sort Pokémon by usage percentage (descending)
                sorted_pokemon = sorted(pokemon_data.items(), key=lambda x: x[1].get('usage_perc', 0), reverse=True)
                # Keep only the top N Pokémon
                top_pokemon = [(pokemon, stats.get('usage_perc', 0)) for pokemon, stats in sorted_pokemon[:self.top_count]]
                self.monthly_rankings[target_date] = top_pokemon

        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")

    def analyze_top_pokemon_ranks(self, start_date, end_date):
        current_date = datetime.strptime(start_date, '%Y-%m')
        end_date = datetime.strptime(end_date, '%Y-%m')

        while current_date <= end_date:
            target_date = current_date.strftime('%Y-%m')
            self.load_data(target_date)
            current_date = current_date.replace(day=1)  # Move to the first day of next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

    def plot_monthly_rankings(self):
        if not self.monthly_rankings:
            print("No monthly rankings data available.")
            return

        months = list(self.monthly_rankings.keys())
        num_months = len(months)
        num_pages = (num_months + 11) // 12  # Calculate number of pages needed

        for page in range(num_pages):
            fig, axes = plt.subplots(3, 4, figsize=(16, 12))
            axes = axes.ravel()  # Flatten the 2D array of axes

            for i in range(12):
                ax = axes[i]
                idx = page * 12 + i
                if idx < num_months:
                    target_date = months[idx]
                    top_pokemon = self.monthly_rankings[target_date]
                    pokemon_names = [pokemon for pokemon, _ in top_pokemon]
                    usage_percents = [usage for _, usage in top_pokemon]

                    # Get colors based on pokemon_names
                    colors = [self.pokemon_colors.get(pokemon, 'black') for pokemon in pokemon_names]

                    ax.bar(pokemon_names, usage_percents, color=colors)
                    ax.set_title(f"Top 10 Pokémon Usage - {target_date}")
                    ax.set_xlabel('Pokémon')
                    ax.set_ylabel('Usage Percentage')

                    # Set ticks and labels
                    ax.set_xticks(np.arange(len(pokemon_names)))
                    ax.set_xticklabels(pokemon_names, rotation=45, ha='right')

                    ax.set_facecolor('lightgrey')  # Set background color
                else:
                    ax.axis('off')  # Hide empty subplots

            # Set title of the page to folder_path
            fig.suptitle(f"Top 10 Pokémon Usage - {self.folder_path}", fontsize=14, fontweight='bold')
            plt.tight_layout()
            plt.show()

def main():
    folder_path = 'gen9ru-1760'
    start_date = '2023-01'
    end_date = '2024-03'
    top_count = 10  # Number of top Pokémon to consider

    # Create an instance of ReportsPoke
    reporter = ReportsPoke(folder_path, top_count)

    # Analyze top Pokémon rankings across the specified date range
    reporter.analyze_top_pokemon_ranks(start_date, end_date)

    # Plot monthly rankings with multiple pages
    reporter.plot_monthly_rankings()

if __name__ == '__main__':
    main()
