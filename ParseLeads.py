
import re



class ParseLeads:
    def __init__(self, filename):
        self.filename = filename
        self.page ={'pokemon_data':{}}

    #TOTAL BATTLES MIGHT NEED TO BE CHANGED TO LEADS DEPENDING ON IF YOU WANT USAGE OR LEADS
    def parse_leads(self):
        with open(self.filename, 'r') as file:
            data = file.read()

        # Extract total leads from the first line
        total_leads_pattern = r'Total leads: (\d+)'
        total_leads_match = re.search(total_leads_pattern, data)
        if total_leads_match:
            self.page['total_leads'] = int(total_leads_match.group(1))

        # Extract table data using regex
        table_pattern = r'\|\s*(\d+)\s*\|\s*([A-Za-z]+)\s*\|\s*([\d.]+)%\s*\|\s*(\d+)\s*\|\s*([\d.]+)%\s*\|'
        table_matches = re.findall(table_pattern, data)

        for match in table_matches:
            rank = match[0]
            pokemon = match[1]
            usage_perc = float(match[2])
            raw = int(match[3])
            raw_perc = float(match[4])

            # Store data in the pokemon_data dictionary
            self.page['pokemon_data'][pokemon] = {
                'usage_perc': usage_perc,
                'raw': raw,
                'raw_perc': raw_perc,
                # Assuming no 'real' and 'real_perc' data in the provided input
            }

        return self.page  # Optionally return the parsed data dictionary

    def parse_usage(self):
        #print('TESTTESTTEST')
        with open(self.filename, 'r') as file:
            data = file.read()

        # Extract total battles from the first line
        total_battles_pattern = r'Total battles: (\d+)'
        total_battles_match = re.search(total_battles_pattern, data)
        if total_battles_match:
            self.page['total_battles'] = int(total_battles_match.group(1))

        # Extract table data using regex
        table_pattern = r'\|\s*(\d+)\s*\|\s*([A-Za-z]+)\s*\|\s*([\d.]+)%\s*\|\s*(\d+)\s*\|\s*([\d.]+)%\s*\|\s*(\d+)\s*\|\s*([\d.]+)%\s*\|'
        table_matches = re.findall(table_pattern, data)

        for match in table_matches:
            rank = match[0]
            pokemon = match[1]
            usage_perc = float(match[2])
            raw = int(match[3])
            raw_perc = float(match[4])
            real = int(match[5])
            real_perc = float(match[6])

            self.page['pokemon_data'][pokemon] = {
                'usage_perc': usage_perc,
                'raw': raw,
                'raw_perc': raw_perc,
                'real': real,
                'real_perc': real_perc
            }
        return self.page


    def to_dict(self):
        return self.page

