#! /usr/bin/env python
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'stix'
matplotlib.rcParams['font.family'] = 'STIXGeneral'
matplotlib.rcParams['image.origin'] = 'upper'

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Plotting program for Tristan-MP files.')
    parser.add_argument(
        '-n', nargs='?',
        const=-1, default=-1,
        help='Maximum file # to consider')
    parser.add_argument(
        '-framerate', nargs='?',
        const=10, default=10,
        help='FPS for the movie')
    parser.add_argument(
        '-outmovie', nargs='?',
        const='out.mov', default='out.mov',
        help='FPS for the movie')
    parser.add_argument(
        '-O', nargs='+',
        default=[''],
        help='Directory Iseult will open. Default is output')
    parser.add_argument(
        '-p', nargs='?',
        const='Default', default='Default',
        help='''Open Iseult with the given saved view.
              If the name of view contains whitespace,
              either it must be enclosed in quotation marks or given
              with whitespace removed. Name is case sensitive.''')
    parser.add_argument(
        "-b", help="Run Iseult from bash script. Makes a movie.",
        action="store_true")
    parser.add_argument(
        "-name", nargs='+',
        default=[''], help='Plot Title')
    parser.add_argument(
        '--wait',
        help='''Wait until current simulation is finished
             before making movie.''',
        action='store_true')
    cmd_args = parser.parse_args()
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    sys.path.append(
        os.path.join(os.path.dirname(__file__), 'src', 'popup_windows'))
    sys.path.append(
        os.path.join(os.path.dirname(__file__), 'src', 'utils'))
    sys.path.append(
        os.path.join(
            os.path.dirname(__file__), 'src', 'utils', 'spectra_utils'))
    sys.path.append(
        os.path.join(
            os.path.dirname(__file__), 'src', 'utils', 'shock_finders'))
    sys.path.append(
        os.path.join(os.path.dirname(__file__), 'src', 'plots'))

    if not cmd_args.b:
        from main_app import runMe
        runMe(cmd_args)
    else:
        matplotlib.use('Agg')
        pass
