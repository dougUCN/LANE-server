"""
Generates security file
"""

import secrets, os, argparse

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--debug', type=bool, default=False, help=f'False for production, True for testing (default=False)')
parser.add_argument('--rootdir', type=str, default=None, help=f'Where to put the security.py file')
args = parser.parse_args()

if args.rootdir and args.rootdir[-1] == '/':
    rootdir = args.rootdir[:-1]
else:
    rootdir = args.rootdir


filename = f'{rootdir}/security.py'

if os.path.exists(filename):
    raise FileExistsError(f'{filename} already exists')

with open(filename, 'w') as file:
    file.write(f"SECRET_KEY = '{secrets.token_urlsafe(16)}'\nDEBUG = {args.debug}")

print(f'Created {filename}')
