import sys
import subprocess
import json
from pathlib import Path, PurePath
from iapsync.config import config
from iapsync.handlers import all_handlers
from iapsync.utils.transporter import transporter_path


def run(params, opts):
    username = params['username']
    password = params['password']
    APPSTORE_PACKAGE_NAME = params['APPSTORE_PACKAGE_NAME']
    tmp_dir = Path(config.TMP_DIR)
    p = tmp_dir.joinpath(APPSTORE_PACKAGE_NAME)

    if not params.get('skip_appstore', False):
        # 初始化etree
        try:
            subprocess.run([
                transporter_path,
                '-m', 'upload', '-u', username, '-p', password, '-f', p.as_posix()])
        except:
            print('上传失败：%s.' % sys.exc_info()[0])
            raise

    with open(config.TMP_PRODUCTS_PERSIST_FILE, 'r') as fp:
        data = json.load(fp)
        all_handlers.handle(data)

