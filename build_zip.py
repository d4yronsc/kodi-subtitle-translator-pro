import zipfile
import os

addon_id = 'service.subtitletranslator.tamabin'
version = '1.0.18'
zip_name = f'{addon_id}-{version}.zip'
base_dir = r'C:\Claude\Kodi'

include_dirs = ['lib', 'resources']
include_files = ['addon.xml', 'service.py', 'force_translate.py', 'LICENSE']
exclude = {'.git', '__pycache__', '.pyc', '_ziptemp', '_zt', 'kodi-repo', 'build_zip.py', '.zip'}

with zipfile.ZipFile(os.path.join(base_dir, zip_name), 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in include_files:
        fp = os.path.join(base_dir, f)
        if os.path.exists(fp):
            zf.write(fp, f'{addon_id}/{f}')

    for d in include_dirs:
        dp = os.path.join(base_dir, d)
        for root, dirs, files in os.walk(dp):
            dirs[:] = [x for x in dirs if x not in ('__pycache__', '.git')]
            for file in files:
                if file.endswith('.pyc'):
                    continue
                full = os.path.join(root, file)
                arc = os.path.join(addon_id, os.path.relpath(full, base_dir))
                zf.write(full, arc)

print(f'Created {zip_name}: {os.path.getsize(os.path.join(base_dir, zip_name))} bytes')
