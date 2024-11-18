import os, re
from collections import Counter

def parser(directory):
    artist_counter = Counter()
    match_lines = r'"[^"]+\.mp3"\s+"([^"]+)"'
    artist_split = r"\s*,\s*"
    song_split = r"\s*/\s*"
    consolidation = {
        "Pokémon OST": ["Pokémon"],
        "Final Fantasy OST": [r"ff[ivxlc]+"],
        "Half-Life OST": ["Half-Life"],
        "Harry Potter OST": ["Harry Potter"],
        "Nier OST": [r"NieR Replicant ver\.1\.22", r"NieR Gestalt Replicant", r"NieR: Automata"]
    }

    def consolidate(artist_name):
        for main_artist, aliases in consolidation.items():
            for alias in aliases:
                if re.match(alias, artist_name, re.IGNORECASE):
                    return main_artist
        return artist_name

    for file_name in os.listdir(directory):
        if file_name.endswith('.cfg') and (not file_name.startswith("zs_") or file_name.startswith("zs_obj")):
            file_path = os.path.join(directory, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                lines = re.findall(match_lines, content)
                for line in lines:
                    artists = re.split(artist_split, line)
                    for artist_entry in artists:
                        match = re.match(r"(.{0,5}-.*?|[^-\s]+.*?)\s*-\s*", artist_entry)
                        if match:
                            artist = match.group(1).strip()
                            consolidated_artist = consolidate(artist)
                            if consolidated_artist != artist:
                                print(f"Consolidating {artist} into {consolidated_artist}")
                            songs = re.split(song_split, artist_entry)
                            additional_count = len(songs)
                            artist_counter[consolidated_artist] += additional_count
    return artist_counter

def updatedata(artist_counts):
    total_count = sum(artist_counts.values())
    sorted_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)

    table = "\n| Artist | Count | Percentage |\n"
    table += "| --- | --- | --- |\n"

    for artist, count in sorted_artists[:15]:
        percentage = (count / total_count) * 100
        table += f"| {artist} | {count} | {percentage:.2f}% |\n"

    print(table)


    readme_path = 'README.MD'
    with open(readme_path, 'r', encoding='utf-8') as readme_file:
        lines = readme_file.readlines()
    # Hard define the table lines, otherwise it will nuke everything below it, these will need to be updated if the table is moved to a seperate section OR if table size is updated. This WILL create a forced newline at line 91 on run
    top_section = lines[:72]
    bottom_section = lines[91:]
    updated_content = top_section + [table] + bottom_section

    with open(readme_path, 'w', encoding='utf-8') as readme_file:
        readme_file.writelines(updated_content)

def main():
    directory = './musicname'
    artist_counts = parser(directory)
    updatedata(artist_counts)

if __name__ == "__main__":
    main()
