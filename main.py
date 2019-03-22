# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from optparse import OptionParser
import os
import toolbox
import sys


def params():
    """get options from console"""
    usage = "usage: %prog --directory/--file --profiles [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("--directory",
                      action="store", type="string", dest="sgf_directory", default=None,
                      help="Directory with sgf-files to analysis, doesn't stack with --file")
    parser.add_option("--file",
                      action="store", type="string", dest="sgf_file", default=None,
                      help="Sgf-file to analyze, doesn't stack with --directory")
    parser.add_option("--start_move",
                      action="store", type="int", dest="start_move", default=1,
                      help="Move from which analysis would be done. Default is 1")
    parser.add_option("--force",
                      action="store_true", dest="force", default=False,
                      help="Force to re-compute sgf(s). Default is false")
    parser.add_option("--profiles",
                      action="store", type="string", dest="profiles", default="10k",
                      help="Enter profiles, in a comma-separated way. E.g. 10k, 5k, 2k, ... Default is 10k")
    parser.add_option("--output",
                      action="store", type="string", dest="output", default=None,
                      help="Enter output filename, better use .asgf extension")
    parser.add_option("--verbose",
                      action="store", type="int", dest="verbose", default=0,
                      help="Reduces output data, max verbose level = 2")
    # parser.add_option("-f", "--file",
    #                   action="store", type="string", dest="sgf_file", default=None,
    #                   help="Указание .sgf, который будет анализироваться и сопоставляться с рефернсными данными")
    # parser.add_option("-r", "--reference",
    #                   action="store", type='string', dest='reference', default=None,
    #                   help="Указание файла с рефернсными данными, накопленынми раннее")
    # parser.add_option("-t", "--time",
    #                   action="store", type='string', dest='time', default=5,
    #                   help="Указание времени, которое бот будет анализировать каждый ход в партии")

    (options, args) = parser.parse_args()
    return options, args


def main():

    options, args = params()
    dir = options.sgf_directory
    file = options.sgf_file
    start_move = options.start_move
    force = options.force
    profiles = options.profiles
    output = options.output
    toolbox.verbose = options.verbose

    if dir is not None:
        if not os.path.exists(dir):
            toolbox.log(1, "Directory with sgf doesn't exist. Quit now")
            sys.exit()
        else:
            leela = toolbox.MasterAnalyze(dir, start_move, profiles, output, force)
            leela.start()
    elif file is not None:
        if not os.path.exists(file):
            toolbox.log(1, "Sgf-file doesn't exist. Quit now")
            sys.exit()
        else:
            leela = toolbox.MasterAnalyze(file, start_move, profiles, output, force)
            leela.start()
    else:
        toolbox.log(1, "Sgf-file or directory with sgf-files wasn't specified. Quit now")
        sys.exit()


def start(sgfs, start_move=20, profiles="10k", output=None, force=False):
    toolbox.MasterAnalyze(sgfs, start_move, profiles, output, force)

if __name__ == '__main__':
    main()

