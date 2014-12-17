import shutil
import os
import os.path as path
import stat

# frozen_dir = '../tde_frozen/'
# if path.exists(frozen_dir):
#     shutil.rmtree(frozen_dir)

# shutil.copytree('build/exe.linux-x86_64-2.7', path.join(frozen_dir, 'resources/'))
# shutil.copytree('bin/resources', path.join(frozen_dir, 'resources/resources'))
# shutil.copy('bin/eval2', path.join(frozen_dir, 'eval2'))
# shutil.copy('bin/resources/sample.classes.example',
#             path.join(frozen_dir, 'sample.classes.example'))

# os.chmod(path.join(frozen_dir, 'eval2'), stat.S_IRUSR | stat.S_IXUSR)

if __name__ == '__main__':
    import argparse
    def parse_args():
        parser = argparse.ArgumentParser(
            prog='move_build.py',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='move built code into its own repository',
            epilog="""Example usage:

$ python move_build sample_eval2_frozen_dir english_eval2_frozen_dir

makes two new directories (will overwrite if they exist!) and moves the code there.
""")
        parser.add_argument('sample_dir', metavar='SAMPLEDIR',
                            nargs=1,
                            help='output directory for sample_eval2 (will overwrite if exists!)')
        parser.add_argument('english_dir', metavar='ENGLISHDIR',
                            nargs=1,
                            help='output directory for english_eval2 (will overwrite if exists!)')
        return vars(parser.parse_args())
    args = parse_args()

    sample_dir = args['sample_dir'][0]
    english_dir = args['english_dir'][0]

    if path.exists(sample_dir):
        shutil.rmtree(sample_dir)
    if path.exists(english_dir):
        shutil.rmtree(english_dir)

    # sample_eval2
    shutil.copytree('build/exe.linux-x86_64-2.7', path.join(sample_dir, 'resources/'))
    shutil.copytree('bin/resources', path.join(sample_dir, 'resources/resources'))
    shutil.copy('sample_eval2', path.join(sample_dir, 'sample_eval2'))
    shutil.copy('bin/resources/sample.classes.example',
                path.join(sample_dir, 'sample.classes.example'))
    os.chmod(path.join(sample_dir, 'sample_eval2'), stat.S_IRUSR | stat.S_IXUSR)

    shutil.copytree('build/exe.linux-x86_64-2.7', path.join(english_dir, 'resources/'))
    shutil.copytree('bin/resources', path.join(english_dir, 'resources/resources'))
    shutil.copy('english_eval2', path.join(english_dir, 'english_eval2'))
    os.chmod(path.join(english_dir, 'english_eval2'), stat.S_IRUSR | stat.S_IXUSR)
