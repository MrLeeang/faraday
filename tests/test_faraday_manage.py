import os
import subprocess
from faraday.server.config import FARADAY_BASE

try:
    import ConfigParser
except ImportError:
    import faraday.client.configparser as ConfigParser


def test_manage_migrate():
    """
        Run manage migrate with nothing to migrate
        The idea is to catch a broken migration
    """
    if 'POSTGRES_DB' in os.environ:
        # I'm on gitlab ci runner
        # I will overwrite server.ini
        connection_string = 'postgresql+psycopg2://{username}:{password}@postgres/{database}'.format(
            username=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            database=os.environ['POSTGRES_DB'],
        )
        faraday_config = ConfigParser.SafeConfigParser()
        config_path = os.path.expanduser('~/.faraday/config/server.ini')
        faraday_config.read(config_path)
        try:
            faraday_config.add_section('database')
        except ConfigParser.DuplicateSectionError:
            pass
        faraday_config.set('database', 'connection_string', connection_string)
        with open(config_path, 'w') as faraday_config_file:
            faraday_config.write(faraday_config_file)

        command = ['faraday-manage', 'create-tables']
        subproc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   cwd=FARADAY_BASE)  # TODO THIS SHOULD FIXED AND THEN REMOVED ISSUE 5570
        subproc.wait()
        std, err = subproc.communicate()
        assert subproc.returncode == 0, ('Create tables failed!', std, err)

        command = ['faraday-manage', 'migrate']
        subproc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subproc.wait()
        std, err = subproc.communicate()
        print std
        print err
        assert subproc.returncode == 0, ('manage migrate failed!', std, err)
