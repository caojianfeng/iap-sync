import sys
import subprocess
from pathlib import Path, PurePath
from iapsync.config import config
from iapsync.handlers import all_handlers
from iapsync.utils.transporter import transporter_path


def run(params, opts, data_to_upload):
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

    has_update = params.get('force_update', False)
    has_update = has_update or check_update(data_to_upload)

    if has_update and params['dry_run']:
        print('dry_run, so will skip uploading to appstore')

    if has_update and not params['dry_run']:
        # 初始化etree
        try:
            subprocess.run([
                transporter_path,
                '-m', 'upload', '-u', username, '-p', password, '-f', p.as_posix()])
        except:
            print('上传失败：%s.' % sys.exc_info()[0])
            raise

    if has_update:
        if params['dry_run']:
            print('if not dry_run will send data: %s\n\n, params: %s\n\n' % (data_to_upload, params))
        all_handlers.handle(data_to_upload, params)

