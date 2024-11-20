import os, re
from collections import Counter

def parser(directory):
    artist_counter = Counter()
    match_lines = r'"[^"]+\.mp3"\s+"([^"]+)"'
    artist_split = r"\s*,\s*"
    song_split = r"\s*/\s*"
    # To compile multiple tags / artists into one using strings or regex, add it here with the format below "Consolidated Artist Name": [Rules for how to consolidate]
    # The log of what is consolidated into what will be printed to the github actions log,
    consolidation = {
        "Pokémon OST": ["Pokémon"],
        "Final Fantasy OST": [r"ff[ivxlc]+"],
        "Half-Life OST": ["Half-Life"],
        "Harry Potter OST": ["Harry Potter"],
        "Nier OST": [r"NieR Replicant ver\.1\.22", r"NieR Gestalt Replicant", r"NieR: Automata"],
        "Castlevania OST": ["Castlevania"]
    }

    def consolidate(artist_name):
        for main_artist, aliases in consolidation.items():
            for alias in aliases:
                if re.match(alias, artist_name, re.IGNORECASE):
                    return main_artist
        return artist_name

    for file_name in os.listdir(directory):
        if file_name.endswith('.cfg') and not file_name.startswith("zs_") or file_name.startswith("zs_obj"):
            with open(os.path.join(directory, file_name), 'r', encoding='utf-8') as file:
                content = file.read()
                for line in re.findall(match_lines, content):
                    for artist_entry in re.split(artist_split, line):
                        match = re.match(r"(.{0,5}-.*?|[^-\s]+.*?)\s*-\s*", artist_entry)
                        if match:
                            artist = match.group(1).strip()
                            consolidated_artist = consolidate(artist)
                            if consolidated_artist != artist:
                                print(f"Consolidating {artist} into {consolidated_artist}")
                            artist_counter[consolidated_artist] += len(re.split(song_split, artist_entry))
    return artist_counter

def updatedata(artist_counts):
    total_count = sum(artist_counts.values())
    sorted_artists = sorted(artist_counts.items(), key=lambda x: (-x[1], x[0]))

    table = "| Artist | Count | Percentage |\n"
    table += "| --- | --- | --- |\n"

    for artist, count in sorted_artists[:15]:
        percentage = (count / total_count) * 100
        table += f"| {artist} | {count} | {percentage:.2f}% |\n"

    print(table)

    readme_path = 'README.MD'
    with open(readme_path, 'r', encoding='utf-8') as readme_file:
        lines = readme_file.readlines()
    # Hard define the table lines, otherwise it will nuke everything below it, these will need to be updated if the table is moved to a seperate section OR if table size is updated. This WILL create a forced newline at line 93 on run
    top_section = lines[:74]
    bottom_section = lines[93:]
    updated_content = top_section + [table] + bottom_section

    with open(readme_path, 'w', encoding='utf-8') as readme_file:
        readme_file.writelines(updated_content)

def cleanup(directory):
    matchsongs = re.compile(r".*\.(?:mp3|wav)", re.IGNORECASE)
    #matchsongs = re.compile(r".*\.mp3", re.IGNORECASE)
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".cfg"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                matches = matchsongs.findall(content)
                print(matches)
                for match in matches:
                    if any(char.isupper() for char in match):
                        lowercase = match.lower()
                        content = content.replace(match, lowercase)

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

def main():
    # Honestly I have no idea if this needs to be hard-defined, but currently it works as is, and this is how it was running in debug environment
    directory = './musicname'
    artist_counts = parser(directory)
    updatedata(artist_counts)
    cleanup(directory)

if __name__ == "__main__":
    main()
