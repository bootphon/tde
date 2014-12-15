import shutil
import os
import os.path as path
import stat

frozen_dir = '../tde_frozen/'
if path.exists(frozen_dir):
    shutil.rmtree(frozen_dir)

shutil.copytree('build/exe.linux-x86_64-2.7', path.join(frozen_dir, 'resources/'))
shutil.copytree('bin/resources', path.join(frozen_dir, 'resources/resources'))
shutil.copy('bin/eval2', path.join(frozen_dir, 'eval2'))
shutil.copy('bin/resources/sample.classes.example',
            path.join(frozen_dir, 'sample.classes.example'))

os.chmod(path.join(frozen_dir, 'eval2'), stat.S_IRUSR | stat.S_IXUSR)
