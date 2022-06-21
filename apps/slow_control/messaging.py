"""
Communications with the slow control worker thread
"""
FAKE = True  # for development

# Valid slow control commands
COMMAND = {
    'REFRESH_DEVICES': 'REFRESH_DEVICES',
    'START': 'START',
    'SOFT_STOP': 'SOFT_STOP',
    'HARD_STOP': 'HARD_STOP',
    'CLEAR': 'CLEAR',
    'RUN': 'RUN',
}


def slowControlCmd(msg):
    if not FAKE:
        pass
    else:
        success = True
    return success
