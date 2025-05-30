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

def check_create_path(path):
    if not os.path.exists(path):
        print(f"path %s not found",path)
        try:
            os.makedirs(path)
        except Exception as e:
            print("Error creating path")
            print(e)
            raise
        finally:
            return 1
    else:
        return 0
