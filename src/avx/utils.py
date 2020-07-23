import os
import json


STATE_DIR = '/var/lib/avx'


def _ensure_state_dir():
    if not os.path.exists(STATE_DIR):
        try:
            os.mkdir(STATE_DIR)
        except OSError:
            print 'Unable to create state directory {}!'.format(STATE_DIR)


def loadState(key, default=None):
    try:
        filename = os.path.join(STATE_DIR, key)
        with open(filename, 'r') as f:
            return json.load(f)
    except IOError:
        return default


def saveState(key, data):
    _ensure_state_dir()
    try:
        filename = os.path.join(STATE_DIR, key)
        with open(filename, 'w') as f:
            json.dump(data, f)
    except IOError:
        print('Unable to save state file. Check permissions on {}'.format(STATE_DIR))
