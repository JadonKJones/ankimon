import csv
import json

input_file = 'src/Ankimon/data_files/pokemon_evolution.csv'
output_file = 'src/Ankimon/data_files/pokemon_evolution_new.csv'

with open('src/Ankimon/data_files/pokedex.json', 'r') as f:
    pokedex = json.load(f)

# The prevo mapping based on actual_id
prevo_map = {}
for name, data in pokedex.items():
    if data.get('prevo'):
        prevo_name = data['prevo']
        prevo_data = pokedex.get(prevo_name.lower())
        if prevo_data:
            evo_id = str(data['actual_id'])
            prevo_id = str(prevo_data['actual_id'])
            prevo_map[evo_id] = prevo_id

name_to_id = {}
def normalize(name):
    return name.lower().replace(" ", "").replace("-", "").replace("'", "").replace(".", "").replace(":", "").replace("♀", "f").replace("♂", "m").replace("é", "e").replace("’", "")

for name, data in pokedex.items():
    actual_id = str(data['actual_id'])
    name_to_id[normalize(name)] = actual_id
    if 'species_id' in data:
        name_to_id[normalize(str(data['species_id']))] = actual_id

# Let's add special cases that might be weird in pokedex.json
for name, data in pokedex.items():
    if data.get('prevo'):
        evo_id = str(data['actual_id'])
        prevo_name = data['prevo']
        norm_prevo = normalize(prevo_name)

        if norm_prevo in name_to_id:
            prevo_map[evo_id] = name_to_id[norm_prevo]
        elif prevo_name.lower() in pokedex:
            prevo_map[evo_id] = str(pokedex[prevo_name.lower()]['actual_id'])

# Manually add missing ones that the automated normalize function couldn't catch
name_to_id[normalize("Farfetch’d-Galar")] = "10166"
prevo_map["865"] = "10166"

name_to_id[normalize("Type: Null")] = "772"
prevo_map["773"] = "772" # Silvally

name_to_id[normalize("Mime Jr.")] = "439"
prevo_map["122"] = "439" # Mr. Mime

name_to_id[normalize("Flabébé")] = "669"
prevo_map["670"] = "669" # Floette

# Check exactly what the code reviewer complained about:
# Nidorina (30), Nidorino (33), Mime Jr (439->122), Farfetch'd (10166->865), Flabebe (669->670), Type: Null (772->773)

# Let's print out what we found
print("Nidorina (30) prevo should be 29. prevo_map[30] =", prevo_map.get("30"))
print("Nidorino (33) prevo should be 32. prevo_map[33] =", prevo_map.get("33"))
print("Mr. Mime (122) prevo should be 439. prevo_map[122] =", prevo_map.get("122"))
print("Floette (670) prevo should be 669. prevo_map[670] =", prevo_map.get("670"))
print("Silvally (773) prevo should be 772. prevo_map[773] =", prevo_map.get("773"))

with open(input_file, 'r', newline='') as f_in, open(output_file, 'w', newline='') as f_out:
    reader = csv.DictReader(f_in)
    writer = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
    writer.writeheader()
    for row in reader:
        evo_id = row['evolved_species_id']
        expected_prevo_id = prevo_map.get(evo_id)
        if expected_prevo_id and row['id'] != expected_prevo_id:
            row['id'] = expected_prevo_id
        writer.writerow(row)
