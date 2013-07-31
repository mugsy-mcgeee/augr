# URLs
DIST_URL='http://python-distribute.org/distribute_setup.py'
KIVY_URL='http://kivy.googlecode.com/files/Kivy-1.7.1-w32.zip'
MATPLOTLIB_URL='https://github.com/downloads/matplotlib/matplotlib/matplotlib-1.2.0.win32-py2.7.exe'

import sys
import os
import os.path
import json
import shutil
import urllib
from zipfile import ZipFile
from os.path import join as pjoin
from subprocess import Popen, PIPE


def rcopy(src_base, dst_base, name):
    shutil.copytree( pjoin(src_base,name),pjoin(dst_base,name) )
def copy(src_base, dst_base, name):
    shutil.copy( pjoin(src_base,name),pjoin(dst_base,name) )


def setup_python():
    py_bin = pjoin('/Python27','python.exe')
    easy_bin = pjoin('/Python27','Scripts','easy_install.exe')

    print '\nConfiguring python'
    urllib.urlretrieve(DIST_URL, 'distribute_setup.py')
    Popen([py_bin, 'distribute_setup.py'], stdout=PIPE, stderr=PIPE).communicate()
    os.remove('distribute_setup.py')
    print 'Installing numpy'
    Popen([easy_bin,'numpy'], stdout=PIPE, stderr=PIPE).communicate()


def matplotlib_present():
    src_base = pjoin('/Python27','Lib','site-packages')

    return all([os.path.exists(pjoin(src_base, 'dateutil' )),
                os.path.exists(pjoin(src_base, 'pytz')),
                os.path.exists(pjoin(src_base, 'matplotlib')),
                os.path.exists(pjoin(src_base, 'matplotlib-1.2.0-py2.7.egg-info')),
                os.path.exists(pjoin(src_base, 'mpl_toolkits')),
                os.path.exists(pjoin(src_base, 'numpy-1.7.1-py2.7-win32.egg')),
                os.path.exists(pjoin(src_base, 'numpy-1.7.1-py2.7-win32.egg'))])


def install_kivy():
    print '\nInstalling kivy'

    print '\tDownloading {}'.format(KIVY_URL)
    urllib.urlretrieve(KIVY_URL, 'kivy.zip')
    print '\tInstalling kivy'
    try:
        kivy = ZipFile('kivy.zip')
        kivy.extractall()
        kivy.close()
        os.remove('kivy.zip')
    except Exception, e:
        print '\n!! Error unzipping kivy : {}'.format(e)
        sys.exit(1)

    os.remove('README.txt')
    os.remove('kivy.bat')
    os.remove('kivyenv.sh')
    print 'Kivy installed'


def install_matplotlib():
    print '\nInstalling matplotlib'

    if matplotlib_present():
        print '\tmatplotlib found, skipping download'
    else:
        print '\tDownloading {}'.format(MATPLOTLIB_URL)
        urllib.urlretrieve(MATPLOTLIB_URL, 'matplotlib.exe')
        print '\tRunning installer'
        Popen(['matplotlib.exe']).communicate()
        raw_input('\nAfter installation is complete, press <enter> to continue..')
        os.remove('matplotlib.exe')

    print '\tFinalizing matplotlib installation'
    src_base = pjoin('/Python27','Lib','site-packages')
    dst_base = pjoin('Python','Lib','site-packages')

    rcopy(src_base, dst_base, 'dateutil')
    rcopy(src_base, dst_base, 'pytz')
    rcopy(src_base, dst_base, 'matplotlib')
    copy(src_base, dst_base, 'matplotlib-1.2.0-py2.7.egg-info')
    rcopy(src_base, dst_base, 'mpl_toolkits')
    rcopy(pjoin(src_base,'numpy-1.7.1-py2.7-win32.egg'),dst_base,'numpy')
    copy(pjoin(src_base,'numpy-1.7.1-py2.7-win32.egg'),dst_base,'numpy-1.7.1-py2.7.egg-info')
   
    print 'matplotlib installed'


def install_sqlalchemy():
    print '\nInstalling SQLAlchemy'

    INST_BIN = pjoin('Python','Scripts','easy_install.exe')
    sout,serr = Popen([INST_BIN, 'sqlalchemy'], stdout=PIPE, stderr=PIPE).communicate()
    errors = [l for l in serr.split('\n') if 'warning' not in l 
                                          and 'zip_safe' not in l
                                          and 'doc' not in l
                                          and l.strip() != '']
    if len(errors) > 0:
        print '!! Error installing SQLAlchemy\n{}'.format('\n'.join(errors))
        sys.exit(1)

    print '\nSQLAlchemy installed'


def install_replayparser():
    print '\nUnpacking replay parser'

    try:
        replay = ZipFile('Dota2_ReplayParser_v102.zip')
        replay.extractall()
        replay.close()
    except Exception, e:
        print '\n!! Error unzipping Dota2_ReplayParser_v102.zip : {}'.format(e)
        sys.exit(1)

    print 'Done'


def initial_config():
    print '\nInitial configuration:\n'
    cfg = {}
    cfg['steam_id'] = raw_input('\tSteam ID: ')
    cfg['api_key'] = raw_input('\tAPI Key: ')
    cfg['db_path'] = 'vault.dat'
    cfg['replay_path'] = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\dota 2 beta\\dota\\replays'
    with open('config.json', 'w') as cfg_file:
        json.dump(cfg, cfg_file, indent=1)


if __name__ == '__main__':
    setup_python()
    install_kivy()
    install_matplotlib()
    install_sqlalchemy()
    install_replayparser()

    initial_config()
    copy('lib','.','augr.bat')
