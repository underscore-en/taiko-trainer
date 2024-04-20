from bs4 import BeautifulSoup
from pprint import pprint
from collections import OrderedDict

def scrape_normalized():
    # retval
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
                    print(difficulty_name)
                    
                    songs = songs.find_all('a')
                    song_names = list(map(lambda e: e.get_text(), songs))
                    song_urls = list(map(lambda e: e.get('href'), songs))
                    
                    aggregated_difficulties.append(difficulty_name)
                    retval[difficulty_name] = [song_names, [], [], [], []]
                
                
            else: # rest of the column does not contain the difficulty
                songss = aggregated_difficulty_skill_column.find_all('tr')[1:] # one diff have songs, multiple diff have songss
                assert aggregated_difficulty_count == len(songss) # assert consistency
                
                for difficulty_name, songs in zip(aggregated_difficulties, songss):
                    songs = songs.find_all('a')
                    song_names = list(map(lambda e: e.get_text(), songs))
                    song_urls = list(map(lambda e: e.get('href'), songs))
                    retval[difficulty_name][idx] = song_names
            
                
    return retval
        

if __name__ == "__main__":
    difficulty_normalized_data = scrape_normalized()
    pprint(difficulty_normalized_data)

    
    