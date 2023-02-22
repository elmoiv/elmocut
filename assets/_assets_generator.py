import os

get_raw = lambda f: open(f, 'rb').read()

with open('assets.py', 'w') as assets_file:
    for asset_file in filter(lambda i: i.rsplit('.', 1)[1].lower() in 'pngjpgjpegwavmp3', os.listdir()):

        # Split file into name and extension
        asset_name, asset_ext = asset_file.rsplit('.', 1)

        # Check if image asset
        if asset_ext.lower() in 'pngjpgjpeg':
            variable = f'{asset_name}_icon'
            real_file = f'{asset_name}.{asset_ext}'

        # Check if sound asset
        elif asset_ext.lower() in 'wavmp3':
            variable = f'{asset_name}_sfx'
            real_file = f'{asset_name}.{asset_ext}'
        else:
            continue
        
        # Add to assets.py
        assets_file.write(f'{variable} = {str(get_raw(real_file))}\n\n')