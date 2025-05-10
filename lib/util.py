import os, shutil

def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(src):
        os.makedirs(src)

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            if item != '.gitignore':
                shutil.copy2(s, d)