import json

RULE_FILE_NAME = "gameofliferules.txt"
rule_names = []
rule_file = open(RULE_FILE_NAME, "r")
for line in rule_file:
	rule = line.split(":")
	rule_names.append(rule[0])

	

logic = json.dumps([
    {'type': 'title',
     'title': 'Gameplay Settings'},
    {'type': 'numeric',
     'title': 'Update Speed',
     'desc': 'Number of updates per second',
     'section': 'logic',
     'key': 'updates_per_second'},
    {'type': 'string',
     'title': 'Living Requirement',
     'desc': 'Number of neighbours required to stay alive\nNo need to separate numbers',
     'section': 'logic',
     'key': 'req_to_live'},
    {'type': 'string',
     'title': 'Birth Requirement',
     'desc': 'Number of neighbours required to come to life\nNo need to separate numbers',
     'section': 'logic',
     'key': 'req_to_birth'},
    {'type': 'options',
     'title': 'Saved Settings',
     'desc': 'Load a pre-defined set of rules',
     'section': 'logic',
     'key': 'rule_to_use',
     'options': rule_names}])

aesthetics = json.dumps([
    {'type': 'title',
     'title': 'Tile and Background Settings'},
    {'type': 'options',
     'title': 'Live Tile',
     'desc': 'The look of living tiles',
     'section': 'aesthetics',
     'key': 'live_tile',
     'options': ['Green Fade', 'add more']},
    {'type': 'options',
     'title': 'Dead Tile',
     'desc': 'The look of dead tiles',
     'section': 'aesthetics',
     'key': 'dead_tile',
     'options': ['Transparent', 'add more']},
    {'type': 'numeric',
     'title': 'Tile Size',
     'desc': 'The size of tiles in pixels: changes number of tiles\nToo many tiles will slow things down; takes time to render',
     'section': 'aesthetics',
     'key': 'tile_size'},
    {'type': 'options',
     'title': 'Background',
     'desc': 'Image to use as the background',
     'section': 'aesthetics',
     'key': 'background',
     'options': ['Black', 'still need to implement a background', 'add more']},
    {'type': 'path',
     'title': 'New Living Tile Image',
     'desc': 'Choose a new image from your phone to represent living tiles',
     'section': 'aesthetics',
     'key': 'custom_live_tile'},
    {'type': 'path',
     'title': 'New Dead Tile Image',
     'desc': 'Choose a new image from your phone to represent dead tiles',
     'section': 'aesthetics',
     'key': 'custom_dead_tile'},
    {'type': 'path',
     'title': 'New Background Image',
     'desc': 'Choose a new image from your phone to represent the background. Works with transparent living/dead tiles only.',
     'section': 'aesthetics',
     'key': 'custom_background'},
])

about_me = json.dumps([
    {'type': 'title',
     'title': 'About Me'}])
