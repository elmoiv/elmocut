get_raw = lambda img: open(img, 'rb').read()

with open('assets.py', 'w') as assets_file:
    for png in 'app,scan_easy,scan_hard,kill,unkill,killall,unkillall,settings,about,facebook,twitter,linkedin,github,me'.split(','):
        variable = f'{png}_icon'
        real_file = f'{png}.png'
        assets_file.write(f'{variable} = {str(get_raw(real_file))}\n\n')