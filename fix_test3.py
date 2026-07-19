import json

def get_user_data(key, default):
    # Simulating the exact return value
    # If the database returns the list [13, 14] parsed from json...
    return [13, 14]

print(set(get_user_data("pokedex_caught", [])))
