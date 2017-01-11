import shutil
import os
import os.path as path
import stat


if __name__ == '__main__':
    import argparse
    def parse_args():
        parser = argparse.ArgumentParser(
            prog='move_build.py',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='move built code into its own directory',
            epilog="""Example usage:

$ python move_build english /path/to/out/

makes a new directory (will overwrite if it exists!) and moves the code
for the evaluation of the english dataset there.
""")
        parser.add_argument('corpus', metavar='CORPUS',
                            nargs=1,
                            choices=['french', 'english', 'mandarin'],
                            help='build code for which corpus')
        parser.add_argument('output', metavar='OUTDIR',
                            nargs=1,
                            help='output directory (will be overwritten if it exists)')
        return vars(parser.parse_args())
    args = parse_args()
    corpus = args['corpus'][0]
    output = args['output'][0]

    if path.exists(output):
        shutil.rmtree(output)

    shutil.copytree('build/exe.linux-x86_64-2.7', path.join(output, 'resources/'))
    shutil.copytree('bin/resources', path.join(output, 'resources/resources'))
    if corpus == 'french':
        shutil.copy('french_eval2', path.join(output, 'french_eval2'))
        shutil.copy('bin/resources/french.classes', path.join(output, 'french.classes'))
        os.chmod(path.join(output, 'french_eval2'), stat.S_IRUSR | stat.S_IXUSR)
    elif corpus == 'english':
        shutil.copy('english_eval2', path.join(output, 'english_eval2'))
        os.chmod(path.join(output, 'english_eval2'), stat.S_IRUSR | stat.S_IXUSR)
    else:
        shutil.copy('mandarin_eval2', path.join(output, 'mandarin_eval2'))
        os.chmod(path.join(output, 'mandarin_eval2'), stat.S_IRUSR | stat.S_IXUSR)
