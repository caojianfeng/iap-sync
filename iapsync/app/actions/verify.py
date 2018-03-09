import sys
import subprocess
from pathlib import Path, PurePath
from iapsync.config import config
from iapsync.utils.transporter import transporter_path


def run(params, opts):
    APPSTORE_PACKAGE_NAME = params['APPSTORE_PACKAGE_NAME']
    username = params['username']
    password = params['password']
    tmp_dir = Path(config.TMP_DIR)
    p = tmp_dir.joinpath(APPSTORE_PACKAGE_NAME)
    # 初始化etree
    try:
        subprocess.run([
            transporter_path,
            '-m', 'verify', '-u', username, '-p', password, '-f', p.as_posix()])
    except:
        print('验证失败：%s.' % sys.exc_info()[0])
        raise


