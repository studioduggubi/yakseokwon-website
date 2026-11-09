"""One source of truth for domain, base path and the local build directory."""
import json,os,pathlib,re,urllib.parse
ROOT=pathlib.Path(__file__).resolve().parents[1]

def build_settings(environment=None):
 env=os.environ if environment is None else environment
 config=json.loads((ROOT/'content/site.json').read_text())
 profile=env.get('SITE_PROFILE',config['default_profile'])
 if profile not in config['profiles']:raise ValueError('Unknown SITE_PROFILE: '+profile)
 settings=config['profiles'][profile]
 origin=settings['origin'];url=urllib.parse.urlsplit(origin)
 if url.scheme!='https'or not url.hostname or url.path or url.query or url.fragment or url.username or url.password or url.port:raise ValueError('Site origin must be an HTTPS origin without a path')
 base=settings['base_path']
 if not re.fullmatch(r'(?:/[A-Za-z0-9._-]+)*',base)or any(x in['.','..']for x in base.split('/')):raise ValueError('Invalid profile base path')
 # Keep older matching build commands valid, while rejecting mixed deployment targets.
 if 'SITE_BASE_PATH'in env and env['SITE_BASE_PATH'].rstrip('/')!=base:raise ValueError('SITE_BASE_PATH conflicts with SITE_PROFILE; select preview or production')
 output=env.get('SITE_OUTPUT_DIR','dist')
 if not re.fullmatch(r'dist(?:-[a-z0-9][a-z0-9-]*)?',output):raise ValueError('SITE_OUTPUT_DIR must be dist or a dist-* directory in this project')
 return {'profile':profile,'origin':origin,'base_path':base,'output_dir':output}

SETTINGS=build_settings()
PROFILE=SETTINGS['profile'];ORIGIN=SETTINGS['origin'];BASE_PATH=SETTINGS['base_path'];DIST=ROOT/SETTINGS['output_dir']
