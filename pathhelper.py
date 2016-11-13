import os

def valid(path):
    path = path.split(os.path.sep)
    for i, bit in enumerate(path):
        if not bit:
            continue
        path[i] = bit + (os.path.sep if bit[-1] == ':' else '')
    return os.path.join(*path)

def user_friendly(path):
    path = computer_friendly(path)
    return valid(path).replace(os.path.expanduser('~'), '~').replace(os.path.sep, '/')

def computer_friendly(path):
    path = path.replace('~', os.path.expanduser('~'))
    path = path.replace('/', os.path.sep)
    path = valid(path)
    return path
