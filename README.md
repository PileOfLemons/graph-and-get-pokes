# graph-and-get-pokes
Download and modify needed files from smogon.com/stats to then make them easy to modify


Okay this is my first readme. I don't super know what im doing in here.
So the only files that should need modified at all for users is the PileOfLemons.py and technically the ReportsPoke file. 

start_date1 = '2020-01'
end_date1 = '2023-03'
format_value1 = 'gen8ru'
ranking1 = '1760'

These should be fairly self explanitory. But when you want a set of files. You need the start_date and the end_date. check smogon.com/stats to make sure the format you want exists during those time frames. gen9ru didn't exist before the game came out. but also didnt exist for the first month or two.

Format value and ranking should be easy. just make sure they match whats on the stats website otherwise it wont work.

Sometimes the code gets weird and will skip some months and not gather their files. I'm working on a fix but if that happens. just switch the dates around so it starts on the date its missing so it gets those files and then you should be golden.

The line that says lemon.getfiles can be commented out and ignored after you've downloaded all the raw files.
same with the    parser.iterate_date_range(). this just makes the raw files into pretty files.
so if you're just messing around with graphs then comment out those two lines so you're not wasting time/processing power

The thing to change in ReportsPoke is a dictionary at the top of the file looks like this

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

Pick the color you want for each pokemon. add pokemon that you see often on the graphs and give them a color otherwise the bars will default to black. 


Plans to do next involve getting a good dictionary of all the pokemon colors. Will use some api to generate that dictionary and just add that to the files.
And add a way to make it just toggle random colors in case you don't feel like fooling with the dictionary

The code is quick easy and ugly. I am not a great programmer and am still a student. ChatGPT was used to help speed up the process due to my lack of experience and laziness.

Any suggestions are welcome
