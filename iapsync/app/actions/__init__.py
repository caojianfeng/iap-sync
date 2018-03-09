from ..actions import sync
from ..actions import upload
from ..actions import verify

actions = {
    'sync': sync.run,
    'upload': upload.run,
    'verify': verify.run,
}