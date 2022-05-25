"""
Generates security file
"""

import secrets, os, argparse

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--debug', type=bool, default=False, help=f'False for production, True for testing (default=False)')
parser.add_argument('--rootdir', type=str, default=None, help=f'Root directory of project relative to where genSecurityFile.py was called')
args = parser.parse_args()

if args.rootdir and args.rootdir[-1] == '/':
    rootdir = args.rootdir[:-1]
elif args.rootdir:
    rootdir = args.rootdir
else:
    # Auto detect root directory
    stream = os.popen('git rev-parse --show-toplevel')  # Get root directory of project
    rootdir = stream.read()[:-1]  # Last char of stream should be newline


filename = f'{rootdir}/server/nEDM_server/security.py'

if os.path.exists(filename):
    raise FileExistsError(f'{filename} already exists')

with open(filename, 'w') as file:
    file.write(f"SECRET_KEY = '{secrets.token_urlsafe(16)}'\nDEBUG = {args.debug}")

print(f'Created {filename}')
