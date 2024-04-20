from bs4 import BeautifulSoup
from pprint import pprint
from collections import OrderedDict
import re

def sanitize_song_name(name: str):
    for f, t in [
        (" ",""),
        ("　", ""),
        ("♡",""),
        ("Ⅶ","VII"),
        ('Ⅵ', "VI"),
        ('Ⅴ', "V"),
        ('Ⅰ', "I"),
        ('★', '☆'),
        ("（","("),
        ('）', ')'),
        ("Ｎ","N"),
        ("＋","+"),
        ("Ａ","A"),
        ("Ｃ","C"),
        ("＆","&"),
        ("’","'"),
        ('／', "/"),
        ("：",":"),
        ("？","?"),
        ("！","!"),
        ("・","･"),
        ("‐","-"),
        ("－","-"),
    ]:
        name = name.replace(f, t)
        
    # they can't type for this
    if name.startswith('NeGa/PoSi'):
        name.replace('NeGa/PoSi', 'NeGa/Posi')
    if name.startswith('エンジェルドリーム(デレマス)'):
        name = 'エンジェルドリーム'

    return name

def scrape_normalized():
    retval: OrderedDict[str, tuple[list[str], list[str],list[str], list[str],  list[str] ]] = OrderedDict()
    
    
    with open("./raw/normalized.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    content_div = soup.find('div', id='content')
    assert content_div
    
    aggregated_difficulty_rows = content_div.find_all('div', class_='flex-container')[:11]
    assert len(aggregated_difficulty_rows) == 11
    
    for aggregated_difficulty_row in aggregated_difficulty_rows:
        # columns
        aggregated_difficulty_skill_columns = aggregated_difficulty_row.find_all('tbody')
        assert(len(aggregated_difficulty_skill_columns) == 5)
        
        aggregated_difficulty_count = None # store to assert consistent across tbodys
        aggregated_difficulties = [] 
        for idx, aggregated_difficulty_skill_column in enumerate(aggregated_difficulty_skill_columns):


            if idx == 0: # first column contain the difficulties as well
                difficulty_song_pairs = aggregated_difficulty_skill_column.find_all('tr')[1:]
                aggregated_difficulty_count = len(difficulty_song_pairs)
                
                assert(1 <= aggregated_difficulty_count <= 3) # 1 - 3 levels per aggregation
                for difficulty_song_pair in difficulty_song_pairs:
                    difficulty, songs = difficulty_song_pair.find_all('td')
                    assert difficulty, songs

                    difficulty_name = difficulty.get_text()
                    
                    songs = songs.find_all('a')
                    song_names = list(map(lambda e: e.get_text(), songs))
                    song_names = list(map(sanitize_song_name, song_names))
                    # song_urls = list(map(lambda e: e.get('href'), songs))
                    
                    aggregated_difficulties.append(difficulty_name)
                    retval[difficulty_name] = [song_names, [], [], [], []]
                
                
            else: # rest of the column does not contain the difficulty
                songss = aggregated_difficulty_skill_column.find_all('tr')[1:] # one diff have songs, multiple diff have songss
                assert aggregated_difficulty_count == len(songss) # assert consistency
                
                for difficulty_name, songs in zip(aggregated_difficulties, songss):
                    songs = songs.find_all('a')
                    song_names = list(map(lambda e: e.get_text(), songs))
                    song_names = list(map(sanitize_song_name, song_names))
                    song_urls = list(map(lambda e: e.get('href'), songs))
                    retval[difficulty_name][idx] = song_names
            
                
    return retval

def scrape_sequence():
    # cat, name, oni, inneroni
    retval:list[tuple[str, str, str|None, str|None]] = []
    
    
    with open("./raw/sequence.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    tables = soup.find_all('div', class_='wikiwiki-tablesorter-wrapper')
    tables = tables[1:]        # first one is irrelevant
    assert len(tables) == 9
    
    for table in tables:
        category_name = table.find('thead').find('tr').get_text()
        
        
        for row in table.find('tbody').find_all('tr'):
            data = row.find_all('td')
            assert len(data) == 9
            song_name = data[2].find('strong').get_text()
            song_name = sanitize_song_name(song_name)
            oni_diff, inneroni_diff = None, None
            
            if data[7].find('a'):
                oni_diff = data[7].get_text()
            if data[8].find('a'):
                inneroni_diff = data[8].get_text()
            retval.append([category_name, song_name, oni_diff, inneroni_diff])

    return retval

def summerize(difficulty_normalized_data: OrderedDict[str, tuple[list[str], list[str],list[str], list[str],  list[str] ]] , sequence_data: list[tuple[str, str, str|None, str|None]] ): 
    d7_oni = []
    d7_ioni = []
    d8_oni = []
    d8_ioni = []
    d9_oni = []
    d9_ioni = []
    d10_oni = []
    d10_ioni = []

    for cat, song, oni_diff_string, ioni_diff_string in sequence_data:
        if oni_diff_string is not None:
            difficulty_int = int(re.findall(r"★×(\d+)", oni_diff_string)[0])
            if difficulty_int == 7:
                d7_oni.append((cat, song))
            elif difficulty_int == 8:
                d8_oni.append((cat, song))
            elif difficulty_int == 9:
                d9_oni.append((cat, song))
            elif difficulty_int == 10:
                d10_oni.append((cat, song))
        if ioni_diff_string is not None:
            difficulty_int = int(re.findall(r"★×(\d+)", ioni_diff_string)[0])
            if difficulty_int == 7:
                d7_ioni.append((cat, song))
            elif difficulty_int == 8:
                d8_ioni.append((cat, song))
            elif difficulty_int == 9:
                d9_ioni.append((cat, song))
            elif difficulty_int == 10:
                d10_ioni.append((cat, song))

    with open("./output/report.txt", 'w') as f:
        for difficulty, (overall, stamina, pattern, speed, dynamic) in difficulty_normalized_data.items():
            difficulty_int = int(re.findall(r"★×(\d+)", difficulty)[0])
            oni_maps = d7_oni if difficulty_int == 7 else d8_oni if difficulty_int == 8 else d9_oni if difficulty_int == 9 else d10_oni
            ioni_maps = d7_ioni if difficulty_int == 7 else d8_ioni if difficulty_int == 8 else d9_ioni if difficulty_int == 9 else d10_ioni
            
            def report(skill_songs:list[tuple[str, str]], skill_name: str, maps: list[str], oni_or_ioni: str):
                s = difficulty + '\t' + oni_or_ioni + '\t' + skill_name + '\n'
                s += "practice maps:\n"
                
                skill_songs_set: set[str] = set()
                for song in skill_songs:
                    if oni_or_ioni == 'oni' and '裏譜面' in song:
                        continue
                    if oni_or_ioni == 'ioni' and '裏譜面' not in song:
                        continue
                    # since skill song have suffix, remove them
                    suffixes = ["(裏譜面)", "(達人譜面)", "(普通譜面)", "(玄人譜面)", "(裏譜面1P側譜面)", "(旧譜面)", "(新)", "※1"]
                    for suffix in suffixes:
                        if suffix in song:
                            song = song.replace(suffix, "")
                    skill_songs_set.add(song)
                    s += song + '\n'
                    
                s += '\n'
                    
                for cat, song_name in maps:
                    if song_name in skill_songs_set:
                        s += '╔' + '═'*30 + '╗' + '\n'
                        s += cat + '\t' + song_name + '\n'
                        s += '╚' + '═'*30 + '╝' + '\n'
                        skill_songs_set.remove(song_name)
                    else:
                        s += cat + '\t' + song_name + '\n'
                if len(skill_songs_set) > 0:
                    # leftover???
                    # print(cat, difficulty, skill_name, skill_songs_set)
                    pass
                
                f.write(s)
                f.write('\n'*10)
                
                

            report(overall, 'overall', oni_maps, 'oni')
            report(overall, 'overall', ioni_maps, 'ioni')
            report(stamina, 'stamina', oni_maps, 'oni')
            report(stamina, 'stamina', ioni_maps, 'ioni')
            report(pattern, 'pattern', oni_maps, 'oni')
            report(pattern, 'pattern', ioni_maps, 'ioni')
            report(speed, 'speed', oni_maps, 'oni')
            report(speed, 'speed', ioni_maps, 'ioni')
            report(dynamic, 'dynamic', oni_maps, 'oni')
            report(dynamic, 'dynamic', ioni_maps, 'ioni')
            
        
    pass
    
        

if __name__ == "__main__":
    difficulty_normalized_data = scrape_normalized()
    sequence_data = scrape_sequence()
    
    summerize(difficulty_normalized_data, sequence_data)
    
    