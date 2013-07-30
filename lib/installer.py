# RESOURCE URLS 
KIVY_URL='http://kivy.googlecode.com/files/Kivy-1.7.1-w32.zip'
MATPLOTLIB_URL='https://github.com/downloads/matplotlib/matplotlib/matplotlib-1.2.0.win32-py2.7.exe'

# BINS
SYSTEM_PY='/Python27'
EASY_INSTALL='Python/Scripts/easy_install.exe'
REPLAY_ZIP='Dota2_ReplayParser_v102.zip'

import os
import os.path
import time
import subprocess
import urllib
import shutil
import json
from zipfile import ZipFile
from os.path import join


def patch_distutils():
    """
    Need to remove all instances of -mno-cygwin from cygwinccompiler.py
    as this flag is no longer supported by gcc
    """
    print('\nPatching distutils')
    TARGET='Python/Lib/distutils/cygwinccompiler.py'
    if not os.path.exists(TARGET):
        raise Exception('Failed to pach {}. Not found!'.format(TARGET))

    with open(TARGET, 'r') as infile:
        with open('_temptarget', 'w') as outfile:
            for line in infile.readlines():
                outfile.write(line.replace(' -mno-cygwin',''))
    os.remove(TARGET)
    os.rename('_temptarget', TARGET)
    print('Done')


def install_kivy():
    """
    Download and install kivy package into cwd
    """
    try:
        print('\nDownloading Kivy\n{}'.format(KIVY_URL))
        urllib.urlretrieve(KIVY_URL, 'kivy.zip')
        print('Download complete')
    except Exception as e:
        raise Exception('Error downloading {}\n{}'.format(KIVY_URL, e))

    print('\nInstalling Kivy')
    try:
        kivy = ZipFile('kivy.zip')
        kivy.extractall()
        kivy.close()
    except Exception as e:
        raise Exception('Error unzipping Kivy: {}'.format(e))

    os.remove('kivy.zip')
    os.remove('README.TXT')
    os.remove('kivy.bat')
    os.remove('kivyenv.sh')

    patch_distutils()

    print('\nKivy installed')


def install_matplotlib():
    """
    Download and install matplotlib package into system python
    """

    try:
        print('\nDownloading matplotlib\n{}'.format(MATPLOTLIB_URL))
        urllib.urlretrieve(MATPLOTLIB_URL, 'matplotlib.exe')
        print('Download complete')
    except Exception as e:
        raise Exception('Error downloading {}\n{}'.format(KIVY_URL, e))
    
    subprocess.Popen(['matplotlib.exe']).communicate()

    print("""
!!!!!!!!!!!
! READ ME !
!!!!!!!!!!!

1. Please install matplotlib into your System installed Python (C:\Python27). 

2. Press <enter> only after the installation has been completed

""")

    raw_input()
    print('Copying matplotlib')

    # copy system matplotlib into kiva python
    src_base = join(SYSTEM_PY,'Lib','site-packages')
    dst_base = join('Python','Lib','site-packages')

    shutil.copytree(join(src_base,'dateutil'), join(dst_base,'dateutil'))
    shutil.copytree(join(src_base,'matplotlib'), join(dst_base,'matplotlib'))
    shutil.copytree(join(src_base,'mpl_toolkits'), join(dst_base,'mpl_toolkits'))
    shutil.copytree(join(src_base,'pytz'), join(dst_base,'pytz'))
    shutil.copytree(join(src_base,'numpy-1.7.1-py2.7-win32.egg','numpy'),
                    join(dst_base,'numpy'))

    shutil.copy(join(src_base,'numpy-1.7.1-py2.7-win32.egg','numpy-1.7.1-py2.7.egg-info'),
                join(dst_base,'numpy-1.7.1-py2.7.egg-info'))
    shutil.copy(join(src_base,'matplotlib-1.2.0-py2.7.egg-info'),
                join(dst_base,'matplotlib-1.2.0-py2.7.egg-info'))
    
    os.remove('matplotlib.exe')
    print('\nmatplotlib installed')


def install_sqlalchemy():
    print('\nInstalling SQLAlchemy\n')
    subprocess.Popen([EASY_INSTALL, 'sqlalchemy']).communicate()
    print('\nInstall complete')


def install_demoparser():
    if not os.path.exists(REPLAY_ZIP):
        raise Exception('Compressed replay parser not found: {}'.format(REPLAY_ZIP))

    print('\nDecompressing replay parser')
    try:
        parser = ZipFile(REPLAY_ZIP)
        parser.extractall()
        parser.close()
    except Exception as e:
        raise Exception('Error unzipping parser: {}'.format(e))
    print('Done')


def initial_config():
    import penv
    print('\nInitial configuration:\n')
    steam_id = raw_input('\tSteamID: ')
    api_key = raw_input('\tAPI Key: ')

    cfg = {}
    cfg['replay_path'] = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\dota 2 beta\\dota\\replays"
    cfg['cache_path'] = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp')
    cfg['db_path'] = os.path.join(penv.LIBDIR, '..', 'vault.dat')
    cfg['steam_id'] = steam_id
    cfg['api_key'] = api_key

    with open('config.json', 'w') as cfg_file:
        json.dump(cfg, cfg_file, indent=1)
    print('Configuration saved.\n')


######################
# Perform installation 
######################
if __name__ == '__main__':
    print('\nInstalling and configuring dependencies\n')
    install_kivy()
    install_matplotlib()
    install_sqlalchemy()
    install_demoparser()
    initial_config()

    os.rename('lib/augr.bat', 'augr.bat')

    print('\nInstallation complete.\n\nExecute augr.bat to start the program')
