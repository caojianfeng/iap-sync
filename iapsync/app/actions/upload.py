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

    def check_update(data):
        if not data or len(data) <= 0:
            return False
        for data_item in data:
            result = data_item.get('result', None)
            if not result:
                continue
            if len(result.get('updated', [])) > 0 or len(result.get('added', [])) > 0:
                return True
        return False

    has_update = False
    with open(config.TMP_PRODUCTS_PERSIST_FILE, 'r') as fp:
        data = json.load(fp)
        has_update = check_update(data)
        if has_update:
            all_handlers.handle(data, params)

    if has_update and not params.get('skip_appstore', False) and not params['dry_run']:
        # 初始化etree
        try:
            subprocess.run([
                transporter_path,
                '-m', 'upload', '-u', username, '-p', password, '-f', p.as_posix()])
        except:
            print('上传失败：%s.' % sys.exc_info()[0])
            raise


