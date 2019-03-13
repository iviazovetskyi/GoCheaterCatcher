# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from toolbox import *
from optparse import OptionParser


def params():
    """get options from console"""
    usage = "usage: %prog directory bot threads/gpu [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("--directory",
                      action="store", type="string", dest="sgf_directory", default=None,
                      help="Directory with sgf-files to analysis, doesn't stack with --file")
    parser.add_option("--file",
                      action="store", type="string", dest="sgf_file", default=None,
                      help="Sgf-file to analyze, doesn't stack with --directory")
    parser.add_option("--start_move",
                      action="store", type="int", dest="start_move", default=20,
                      help="Move from which analysis would be done")
    parser.add_option("--force",
                      action="store_true", dest="force", default=False,
                      help="Force to re-compute sgf(s)")
    parser.add_option("--game_id",
                      action="store", type="string", dest="game_id", default=None,
                      help="Game_id of sgf-file")
    parser.add_option("--profiles",
                      action="store", type="string", dest="profiles", default="10k",
                      help="Enter profiles, in a comma-separated way. E.g. 10k, 5k, 2k, ...")
    # parser.add_option("-f", "--file",
    #                   action="store", type="string", dest="sgf_file", default=None,
    #                   help="Указание .sgf-файла, который будет анализироваться и сопоставляться с рефернсными данными")
    # parser.add_option("-r", "--reference",
    #                   action="store", type='string', dest='reference', default=None,
    #                   help="Указание файла с рефернсными данными, накопленынми раннее")
    # parser.add_option("-b", "--bot",
    #                   action="store", type='string', dest='bot', default=None,
    #                   help="Указание бота, который будет анализировать партии")
    # parser.add_option("-t", "--time",
    #                   action="store", type='string', dest='time', default=5,
    #                   help="Указание времени, которое бот будет анализировать каждый ход в партии")
    #parser.add_option("-v", "--visits",
    #                   action="store", type='int', dest='visits', default=10000,
    #                   help="Указание количества плейаутов на ход")
    #parser.add_option("--threads",
    #                  action="store", type='int', dest='threads', default=4,
    #                  help="Указание количество ядер CPU, которое будет использовать бот")
    #parser.add_option("-g", "--gpu",
    #                  action="store", type='int', dest='gpu', default=6,
    #                  help="Указание количество ядер GPU, которое будет использовать бот")

    (options, args) = parser.parse_args()
    return options, args


def main():
    options, args = params()
    dir = options.sgf_directory
    file = options.sgf_file
    start_move = options.start_move
    game_id = options.game_id
    force = options.force
    profiles = options.profiles

    # visits = options.visits
    # threads = options.threads
    # gpu = options.gpu
    if dir is not None:
        if not os.path.exists(dir):
            log("Directory with sgf doesn't exist. Quit now")
            sys.exit()
        else:
            leela = MasterAnalyze(dir, start_move, profiles, game_id, force)
            leela.start()
    elif file is not None:
        if not os.path.exists(file):
            log("Sgf-file doesn't exist. Quit now")
            sys.exit()
        else:
            leela = MasterAnalyze(file, start_move, profiles, game_id, force)
            leela.start()
    else:
        log("Sgf-file or directory with sgf-files wasn't specified. Quit now")
        sys.exit()


def start(sgfs, start_move, profiles, game_id=None, force=False):
    MasterAnalyze(sgfs, start_move, profiles, game_id, force)

if __name__ == '__main__':
    main()

