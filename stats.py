import os, re
from collections import Counter

def parser(directory):
    artist_counter = Counter()
    match_lines = r'"[^"]+\.mp3"\s+"([^"]+)"'
    artist_split = r"\s*,\s*" # These two splits should help account for the weird formatting done in the NPST configs, through debugging the ammounts appended ontop of the original value seem correct
    song_split = r"\s*/\s*"
    # To compile multiple tags / artists into one using strings or regex, add it here with the format below "Consolidated Artist Name": [Rules for how to consolidate]
    # The log of what is consolidated into what will be printed to the github actions log
    # This is entirely used for statistics and does not touch any file
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
        if file_name.endswith(".cfg") and (file_name.startswith("zs_obj") or not file_name.startswith("zs_")):
            with open(os.path.join(directory, file_name), "r", encoding="utf-8") as file:
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

    with open("README.MD", "r+", encoding="utf-8") as readme_file:
        lines = readme_file.readlines()
    # Hard define the table lines, otherwise it will nuke everything below it, these will need to be updated if the table is moved to a seperate section OR if table size is updated. This WILL create a forced newline at line 93 on run
    # If the table will always be at the bottom of README.MD, bottom_section can be removed, otherwise it needs to be defined
        top_section = lines[:74]
        bottom_section = lines[93:]
        updated_content = top_section + [table] + bottom_section
        readme_file.seek(0)
        readme_file.writelines(updated_content)

def cleanup(directory):
    # This will check every single .cfg file where the song is inputted correctly (.mp3 / .wav / .ogg), and if it contains any capital letters, it will lowercase it automatically to abide by the plugin format
    # TODO: Add linter to alert for configs that have incorrect song formattings, i.e missing file extension or ,mp3 instead of .mp3 etc
    matchsongs = re.compile(r".*\.(?:mp3|wav|ogg)", re.IGNORECASE)
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".cfg"):
                file_path = os.path.join(root, file)
                with open(file_path, "r+", encoding="utf-8") as f:
                    content = f.read()
                    # Match all upper case strings using this function instead of whatever jank I had before, honestly has 0 different effect except not being forced to open the file twice
                    content = matchsongs.sub(lambda m: m.group(0).lower() if any(char.isupper() for char in m.group(0)) else m.group(0), content)
                    f.seek(0)
                    f.write(content)

def main():
    # Honestly I have no idea if this needs to be hard-defined, could walk entire repo, but currently it works as is, and this is how it was running in debug environment
    directory = "./musicname"
    artist_counts = parser(directory)
    updatedata(artist_counts)
    cleanup(directory)

if __name__ == "__main__":
    main()
