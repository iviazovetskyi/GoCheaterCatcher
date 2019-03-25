# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from traceback import format_exc
from gomill import sgf, sgf_moves
import string
import os
import threading
import codecs
import sys
import Queue
import time
import ConfigParser


verbose = 0


class GCCException(Exception):
    def __init__(self, msg):
        if type(msg) == type(u"abc"):
            self.utf_msg = msg
            self.str_msg = msg.encode("utf-8", errors='replace')
        else:
            self.str_msg = msg
            self.utf_msg = msg.decode("utf-8", errors='replace')
        log(1, "===")
        log(1, format_exc())
        log(1, "===")
        Exception.__init__(self, self.str_msg)

    def __unicode__(self):
        return self.utf_msg

loglock = threading.Lock()


def process_exists(process_name):
    # print subprocess.check_output('tasklist')
    printable = set(string.printable)
    output = filter(lambda x: x in printable, os.popen("tasklist").read())
    return process_name in output


def log(verbose_level, *args):
    global loglock
    if verbose_level <= verbose:
        loglock.acquire()
        encoding = sys.stdout.encoding
        for arg in args:
            try:
                if type(arg) == type(str('abc')):
                    arg = arg.decode('utf-8', errors='replace')
                elif type(arg) != type(u'abc'):
                    try:
                        arg = str(arg)
                    except:
                        arg = unicode(arg, errors='replace')
                    arg = arg.decode('utf-8', errors='replace')
                arg = arg.encode(encoding, errors='replace')
                print(arg)
            except:
                print ("?" * len(arg))
        loglock.release()


def get_moves_number(move_zero):
    k = 0
    move = move_zero
    while move:
        move = move[0]
        k += 1
    return k


def go_to_move(move_zero, move_number=0):
    if move_number == 0:
        return move_zero
    move = move_zero
    k = 0
    while k != move_number:
        if not move:
            log(1, "The end of the sgf tree was reached before getting to move_number", move_number)
            log(1, "Could only reach move_number", k)
            return False
        move = move[0]
        k += 1
    return move


def gtp2ij(move):
    try:
        letters = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
        return int(move[1:]) - 1, letters.index(move[0])
    except:
        raise GCCException("Cannot convert GTP coordinates " + str(move) + " to grid coordinates!")


def ij2gtp(m):
    # (17,0) => a18
    try:
        if m == None:
            return "pass"
        i, j = m
        letters = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
        return letters[j] + str(i + 1)
    except:
        raise GCCException("Cannot convert grid coordinates " + str(m) + " to GTP coordinates!")


def sgf2ij(m):
    # cj => 8,2
    a, b = m
    letters = "abcdefghjklmnopqrstuvwxyz"
    i = letters.index(b)
    j = letters.index(a)
    return i, j


def ij2sgf(m):
    # (17,0) => ???
    try:
        if m == None:
            return "pass"
        i, j = m
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't']
        return letters[j] + letters[i]
    except:
        raise GCCException("Cannot convert grid coordinates " + str(m) + " to SGF coordinates!")

filelock = threading.Lock()
c = 0

def write_sgf(filename, sgf_content):
    filelock.acquire()
    try:
        log(1, "Saving SGF file", filename)
        if type(sgf_content) == type("abc"):
            content = sgf_content
        else:
            content = sgf_content.serialise()
        filename2 = filename
        if type(filename2) == type(u"abc"):
            if sys.getfilesystemencoding() != "mbcs":
                filename2 = filename2.encode(sys.getfilesystemencoding())
        try:
            new_file = open(filename2, 'w')
            new_file.write(content)
        except:
            new_file = codecs.open(filename2, "w", "utf-8")
            new_file.write(content)

        new_file.close()
        filelock.release()
    except IOError, e:
        filelock.release()
        log(1, "Could not save the SGF file", filename)
        log(1, "=>", e.errno, e.strerror)
        raise GCCException(("Could not save the RSGF file: ") + filename + "\n" + e.strerror)
    except Exception, e:
        filelock.release()
        log(1, "Could not save the RSGF file", filename)
        log(1, "=>", e)
        raise GCCException(("Could not save the SGF file: ") + filename + "\n" + unicode(e))


def convert_sgf_to_utf(content):
    game = sgf.Sgf_game.from_string(content)
    gameroot = game.get_root()
    sgf_moves.indicate_first_player(game)  # adding the PL property on the root
    if node_has(gameroot, "CA"):
        ca = node_get(gameroot, "CA")
        if ca == "UTF-8":
            # the sgf is already in UTF, so we accept it directly
            return game
        else:
            log(2, "Encoding is", ca)
            log(2, "Converting from", ca, "to UTF-8")
            encoding = (
                codecs.lookup(ca).name.replace("_", "-").upper().replace("ISO8859", "ISO-8859"))  # from gomill code
            content = game.serialise()
            content = content.decode(encoding, errors='ignore')  # transforming content into a unicode object
            content = content.replace("CA[" + ca + "]", "CA[UTF-8]")
            game = sgf.Sgf_game.from_string(
                content.encode("utf-8"))  # sgf.Sgf_game.from_string requires str object, not unicode
            return game
    else:
        log(1, "the sgf has no declared encoding, we will enforce UTF-8 encoding")
        content = game.serialise()
        content = content.decode("utf", errors="replace").encode("utf")
        game = sgf.Sgf_game.from_string(content, override_encoding="UTF-8")
        return game


def open_sgf(filename):
    filelock.acquire()
    try:
        # log("Opening SGF file",filename)
        filename2 = filename
        if type(filename2) == type(u"abc"):
            if sys.getfilesystemencoding() != "mbcs":
                filename2 = filename2.encode(sys.getfilesystemencoding())
        txt = open(filename2, 'r')
        content = clean_sgf(txt.read())
        txt.close()
        filelock.release()
        game = convert_sgf_to_utf(content)
        return game
    except IOError, e:
        filelock.release()
        log(1, "Could not open the SGF file", filename)
        log(1, "=>", e.errno, e.strerror)
        raise GCCException(("Could not open the RSGF file: ") + filename + "\n" + e.strerror)
    except Exception, e:
        log(1, "Could not open the SGF file", filename)
        log(1, "=>", e)
        try:
            filelock.release()
        except:
            pass
        raise GCCException(("Could not open the SGF file: ") + filename + "\n" + unicode(e))


def clean_sgf(txt):
    # txt is still of type str here....
    txt = txt.replace(str(";B[  ])"), str(";B[])")).replace(str(";W[  ])"), str(";W[])"))
    txt = txt.replace(str("KM[]"), str(""))
    txt = txt.replace(str("B[**];"), str("B[];")).replace(str("W[**];"), str("W[];"))
    return txt


def get_all_sgf_leaves(root, deep=0):
    if len(root) == 0:
        # this is a leave
        return [(root, deep)]

    leaves = []
    deep += 1
    for leaf in root:
        leaves.extend(get_all_sgf_leaves(leaf, deep))

    return leaves


def keep_only_one_leaf(leaf):
    while 1:
        try:
            parent = leaf.parent
            for other_leaf in parent:
                if other_leaf != leaf:
                    log(1, "deleting...")
                    other_leaf.delete()
            leaf = parent
        except:
            # reached root
            return


def check_selection(selection, nb_moves):
    move_selection = []
    selection = selection.replace(" ", "")
    for sub_selection in selection.split(","):
        if sub_selection:
            try:
                if "-" in sub_selection:
                    a, b = sub_selection.split('-')
                    a = int(a)
                    b = int(b)
                else:
                    a = int(sub_selection)
                    b = a
                if a <= b and a > 0 and b <= nb_moves:
                    move_selection.extend(range(a, b + 1))
            except Exception, e:
                print(e)
                return False
    move_selection = list(set(move_selection))
    move_selection = sorted(move_selection)
    return move_selection


def check_selection_for_color(move_zero, move_selection, color):
    if color == "black":
        new_move_selection = []
        for m in move_selection:
            player_color = guess_color_to_play(move_zero, m)
            if player_color.lower() == 'b':
                new_move_selection.append(m)
        return new_move_selection
    elif color == "white":
        new_move_selection = []
        for m in move_selection:
            player_color = guess_color_to_play(move_zero, m)
            if player_color.lower() == 'w':
                new_move_selection.append(m)
        return new_move_selection
    else:
        return move_selection


def we_are_frozen():
    """Returns whether we are frozen via py2exe.
    This will affect how we find out where we are located."""

    return hasattr(sys, "frozen")


def module_path():
    """ This will get us the program's directory,
    even if we are frozen using py2exe"""

    if we_are_frozen():
        log(1, "Apparently running from the executable.")
        return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding()))

    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding()))

try:
    pathname = module_path()
except:
    pathname = os.path.dirname(__file__)

log(2, 'GCC path:', os.path.abspath(pathname))
config_file = os.path.join(os.path.abspath(pathname), "config.ini")
log(2, 'Config file:', config_file)


log(2, "Checking availability of config file")
conf = ConfigParser.ConfigParser()
try:
    conf.readfp(codecs.open(config_file, "r", "utf-8"))
except Exception, e:
    log(2, "Could not open the config file of Go Cheater Catcher" + "\n" + unicode(e))  # this cannot be translated
    sys.exit()


class MyConfig():
    def __init__(self, config_file):
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)
        self.config_file = config_file

        self.default_values = {}
        self.default_values["general"] = {}
        self.default_values["general"]["language"] = ""
        self.default_values["general"]["sgffolder"] = ""
        self.default_values["general"]["rsgffolder"] = ""
        self.default_values["general"]["pngfolder"] = ""
        self.default_values["general"]["livefolder"] = ""
        self.default_values["general"]["stonesound"] = ""

        self.default_values["analysis"] = {}
        self.default_values["analysis"]["maxvariations"] = "26"
        self.default_values["analysis"]["savecommandline"] = "False"
        self.default_values["analysis"]["stopatfirstresign"] = "False"
        self.default_values["analysis"]["novariationifsamemove"] = "False"
        self.default_values["analysis"]["analyser"] = ""

        self.default_values["review"] = {}
        self.default_values["review"]["fuzzystoneplacement"] = "0.2"
        self.default_values["review"]["realgamesequencedeepness"] = "5"
        self.default_values["review"]["leftgobanratio"] = "0.4"
        self.default_values["review"]["rightgobanratio"] = "0.4"
        self.default_values["review"]["rightpanelratio"] = "0.4"
        self.default_values["review"]["opengobanratio"] = "0.4"
        self.default_values["review"]["maxvariations"] = "26"
        self.default_values["review"]["variationscoloring"] = "blue_for_winning"
        self.default_values["review"]["variationslabel"] = "letter"
        self.default_values["review"]["invertedmousewheel"] = "False"
        self.default_values["review"]["lastgraph"] = ""
        self.default_values["review"]["yellowbar"] = "#F39C12"
        self.default_values["review"]["lastbot"] = ""
        self.default_values["review"]["lastmap"] = ""
        self.default_values["review"]["oneortwopanels"] = "1"

        self.default_values["live"] = {}
        self.default_values["live"]["livegobanratio"] = "0.4"
        self.default_values["live"]["size"] = "19"
        self.default_values["live"]["komi"] = "7.5"
        self.default_values["live"]["handicap"] = "0"
        self.default_values["live"]["nooverlap"] = "False"
        self.default_values["live"]["analyser"] = ""
        self.default_values["live"]["black"] = ""
        self.default_values["live"]["white"] = ""
        self.default_values["live"]["thinkbeforeplaying"] = "0"

    def set(self, section, key, value):
        if type(value) in (type(1), type(0.5), type(True)):
            value = unicode(value)
        if type(section) != type(u"abc"):
            print(section, "Warning: A non utf section string sent to my config:", section)
        if type(key) != type(u"abc"):
            print(key, "A non utf key string sent to my config:", key)
        if type(value) != type(u"abc"):
            print(value, "A non utf value string sent to my config:", value)
        section = unicode(section)
        key = unicode(key)
        value = unicode(value)
        self.config.set(section.encode("utf-8"), key.encode("utf-8"), value.encode("utf-8"))
        self.config.write(open(self.config_file, "w"))

    def get(self, section, key):
        try:
            value = self.config.get(section, key)
            value = value.decode("utf-8")
        except:
            log(3, "Could not read", str(section) + "/" + str(key), "from the config file")
            log(3, "Using default value")
            value = self.default_values[section.lower()][key.lower()]
            self.add_entry(section, key, value)
        return value

    def getint(self, section, key):
        try:
            value = self.config.getint(section, key)
        except:
            log(3, "Could not read", str(section) + "/" + str(key), "from the config file")
            log(3, "Using default value")
            value = self.default_values[section.lower()][key.lower()]
            self.add_entry(section, key, value)
            value = self.config.getint(section, key)
        return value

    def getfloat(self, section, key):
        try:
            value = self.config.getfloat(section, key)
        except:
            log(3, "Could not read", str(section) + "/" + str(key), "from the config file")
            log(3, "Using default value")
            value = self.default_values[section.lower()][key.lower()]
            self.add_entry(section, key, value)
            value = self.config.getfloat(section, key)
        return value

    def getboolean(self, section, key):
        try:
            value = self.config.getboolean(section, key)
        except:
            log(3, "Could not read", str(section) + "/" + str(key), "from the config file")
            log(3, "Using default value")
            value = self.default_values[section.lower()][key.lower()]
            self.add_entry(section, key, value)
            value = self.config.getboolean(section, key)
        return value

    def add_entry(self, section, key, value):
        # normally section/key/value should all be unicode here
        # but just to be sure:
        section = unicode(section)
        key = unicode(key)
        value = unicode(value)
        # then, let's turn every thing in str
        section = section.encode("utf-8")
        key = key.encode("utf-8")
        value = value.encode("utf-8")
        if not self.config.has_section(section):
            log(3, "Adding section", section, "in config file")
            self.config.add_section(section)
        log(3, "Setting", section, "/", key, "in the config file")
        self.config.set(section, key, value)
        self.config.write(open(self.config_file, "w"))

    def get_sections(self):
        return [section.decode("utf-8") for section in self.config.sections()]

    def get_options(self, section):
        return [option.decode("utf-8") for option in self.config.options(section)]

    def remove_section(self, section):
        result = self.config.remove_section(section)
        self.config.write(open(self.config_file, "w"))
        return result


gcc_config = MyConfig(config_file)


class MasterAnalyze():
    def __init__(self, sgfs, start_move, profiles, output=None, force=False, append=True):
        # SGFs variable can be either directory with SGF files or a single .sgf file
        if os.path.isdir(sgfs):
            self.filenames = [os.path.join(sgfs, f) for f in os.listdir(sgfs) if f.endswith(".sgf")]
        elif os.path.isfile(sgfs):
            self.filenames = [sgfs]
        self.sgf_dir = os.path.dirname(os.path.abspath(self.filenames[0]))
        self.start_move = start_move
        self.profiles = profiles.split(",")
        self.output = output
        self.force = force
        self.append = append

        self.bots = []
        for bot in get_available():
            if str(bot["profile"]) in profiles:
                self.bots.append(bot)

    def start(self):
        for filename in self.filenames:
            g = open_sgf(filename)
            move_zero = g.get_root()
            nb_moves = get_moves_number(move_zero)
            if self.start_move > nb_moves:
                log(1, "Start move > number of moves in sgf. Skipping...")
                return 
            komi = g.get_komi()
            intervals = "all moves (both colors)"
            move_selection = range(nb_moves)
            filename_base = os.path.splitext(os.path.basename(filename))[0]

            for bot in self.bots:
                dir_path = os.path.dirname(filename) + "\{0}_{1}\\".format(bot["name"], bot["profile"])
                try:
                    os.makedirs(dir_path)
                except OSError:
                    log(1, "Can't create directory: ", dir_path)
                output_filename = dir_path + filename_base + ".asgf"

                if os.path.exists(output_filename) and not self.force and not self.append:
                    log(1, "{0} already exists, and --force wasn't used and --no-append was used. Skipping...".format(output_filename))
                    continue

                if self.output is not None:
                    output_filename = self.output

                if self.append:
                    if os.path.exists(output_filename):
                        with open(output_filename, 'r') as f:
                            contents = f.readlines()
                            if "Move #" in contents[-1]:
                                self.start_move = int(contents[-1].split("#")[1].split(",")[0]) + 1

                bot['runanalysis']((filename, output_filename),
                                   move_selection[self.start_move:], intervals, 0, komi, bot)


class RunAnalysisBase:
    def __init__(self, filenames, move_range, intervals, variation, komi, profile):
        self.filename = filenames[0]
        self.asgf_filename = filenames[1]
        self.move_range = move_range
        self.update_queue = Queue.Queue(1)
        self.intervals = intervals
        self.variation = variation
        self.komi = komi
        self.profile = profile
        # self.playouts = playouts
        # self.threads = threads
        # self.gpu = gpu
        self.g = None
        self.move_zero = None
        self.current_move = None
        self.time_per_move = None
        self.no_variation_if_same_move = False
        self.error = None
        self.maxvariations = 15

        try:
            self.g = open_sgf(self.filename)
            self.move_zero = self.g.get_root()
            self.max_move = get_moves_number(self.move_zero)

            leaves = get_all_sgf_leaves(self.g.get_root())
            log(1, "keeping only main variation", self.variation)
            keep_only_one_leaf(leaves[self.variation][0])

            size = self.g.get_size()
            self.size = size

            log(1, "Setting new komi")
            node_set(self.g.get_root(), "KM", self.komi)
        except Exception, e:
            self.error = unicode(e)
            self.abort()
            return

        try:
            self.bot = self.initialize_bot()
        except Exception, e:
            log("Error while initializing the GTP bot:")
            self.abort()
            return

        if not self.bot:
            return

        self.total_done = 0
        self.stop_at_first_resign = False
        self.completed = False

        # threading.Thread(target=self.run_all_analysis).start()  # multithread disabled, it's more efficent to compute 1 game with N cores compared to N games with 1 core
        self.run_all_analysis()


    def initialize_bot(self):
        pass

    def run_analysis(self, current_move):
        log(1, "Analysis of move", current_move)
        log(1, "Analysis for this move is completed")

    def play(self, gtp_color, gtp_move):
        if gtp_color == 'w':
            self.bot.place_white(gtp_move)
        else:
            self.bot.place_black(gtp_move)

    def run_all_analysis(self):
        self.current_move = 1

        skip = False
        if os.path.exists(self.asgf_filename):
            with open(str(self.asgf_filename), 'r') as f:
                contents = f.readlines()
                if "Rank of white" in contents[0]:
                    skip = True
            f.close()

        f = file(str(self.asgf_filename), 'a')
        if not skip:
            f.write("Rank of white: {0}, rank of black: {1} \n".format(self.g.get_player_rank('w'), self.g.get_player_rank('b')))
        lost_percent = 0
        previous_best = 47
        position_evaluation = dict()
        if self.current_move in self.move_range and self.current_move > 1:
            answer, next_moves, previous_position_evaluation = self.run_analysis(self.current_move - 1)
            wrs = [pos['value network win rate'] for pos in position_evaluation['variations']]
            previous_best = max([float(wr.strip(' \t\n\r%')) for wr in wrs])
            lost_percent = 0

        while self.current_move <= self.max_move - 1:
            answer = ""
            if self.current_move in self.move_range:
                log(0, "Analysing move {0}/{1}".format(self.current_move, self.max_move))
                parent = go_to_move(self.move_zero, self.current_move - 1)
                if len(parent) > 1:
                    log(1, "Removing existing", len(parent) - 1, "variations")
                    for other_leaf in parent[1:]:
                        other_leaf.delete()
                answer, next_moves, position_evaluation = self.run_analysis(self.current_move)

                self.total_done += 1

                log(1, "For this position,", self.bot.bot_name, "would play:", answer)
                log(1, "Analysis for this move is completed")
            elif self.move_range:
                log(1, "Move", self.current_move, "not in the list of moves to be analysed, skipping")

            if self.current_move in self.move_range:
                game_move = go_to_move(self.move_zero, self.current_move).get_move()[1]

                wrs = [pos['value network win rate'] for pos in position_evaluation['variations']]
                current_best = max([float(wr.strip(' \t\n\r%')) for wr in wrs])
                lost_percent = 100 - previous_best - current_best
                if lost_percent > 0:
                    lost_percent = '+{0}'.format(lost_percent)
                previous_best = current_best
                if self.current_move > self.move_range[0]:
                    if self.current_move % 2 == 1:
                        f.write('Move #{0}, made by w: Played at {1}, {2}% in WR. All stats: {3} \n'.format(
                            str(self.current_move - 1),
                            str(ij2gtp(go_to_move(self.move_zero, self.current_move - 1).get_move()[1])),
                            str(lost_percent), str(previous_position_evaluation)))
                        f.flush()
                    else:
                        f.write('Move #{0}, made by b: Played at {1}, {2}% in WR. All stats: {3} \n'.format(
                            str(self.current_move - 1),
                            str(ij2gtp(go_to_move(self.move_zero, self.current_move - 1).get_move()[1])),
                            str(lost_percent), str(previous_position_evaluation)))
                        f.flush()

                previous_position_evaluation = position_evaluation
                wrs = [pos['value network win rate'] for pos in position_evaluation['variations']]
                current_best = max([float(wr.strip(' \t\n\r%')) for wr in wrs])
                lost_percent = 100 - previous_best - current_best
                previous_best = current_best

                if game_move:
                    if self.no_variation_if_same_move:
                        if ij2gtp(game_move) == answer:
                            log(
                                "Bot move and game move are the same (" + answer + "), removing variations for this move")
                            parent = go_to_move(self.move_zero, self.current_move - 1)
                            for child in parent[1:]:
                                child.delete()

            # if answer == "RESIGN":
            #     log(1, "")
            #     log(1, "The analysis will stop now")
            #     log(1, "")
            #     self.move_range = []
            # the bot has proposed to resign, and resign_at_first_stop is ON
            if self.move_range:
                one_move = go_to_move(self.move_zero, self.current_move)
                player_color, player_move = one_move.get_move()
                if player_color in ('w', "W"):
                    log(2, "now asking " + self.bot.bot_name + " to play the game move: white at", ij2gtp(player_move))
                    self.play('w', ij2gtp(player_move))
                else:
                    log(2, "now asking " + self.bot.bot_name + " to play the game move: black at", ij2gtp(player_move))
                    self.play('b', ij2gtp(player_move))

            self.current_move += 1

        f.close()
        self.terminate_bot()
        self.close()
        return True

    def abort(self):
        log(1, "Leaving follow_anlysis()")

    def terminate_bot(self):
        try:
            log(1, "killing", self.bot.bot_name)
            self.bot.close()
        except Exception, e:
            log(0, e)

    def close(self):
        log(1, "RunAnalysis closed")
        self.completed = True


class BotOpenMove():
    def __init__(self, sgf_g, profile):
        self.name = 'Bot'
        self.bot = None
        self.okbot = False
        self.sgf_g = sgf_g
        self.profile = profile

    def start(self, silentfail=True):
        try:
            result = self.my_starting_procedure(self.sgf_g, profile=self.profile, silentfail=silentfail)
            if result:
                self.bot = result
                self.okbot = True
            else:
                self.okbot = False
        except Exception, e:
            log(0, "Could not launch " + self.name)
            log(0, e)
            self.okbot = False
        return

    def undo(self):
        if self.okbot:
            self.bot.undo()

    def place(self, move, color):
        if self.okbot:
            if not self.bot.place(move, color):
                # self.config(state='disabled')
                return False
            return True

    def quick_evaluation(self, color):
        return self.bot.quick_evaluation(color)

    def click(self, color):
        log(1, self.name, "play")
        n0 = time.time()
        if color == 1:
            move = self.bot.play_black()
        else:
            move = self.bot.play_white()
        log(1, "move=", move, "in", time.time() - n0, "s")
        return move

    def close(self):
        if self.okbot:
            log(0, "killing", self.name)
            self.bot.close()


def bot_starting_procedure(bot_name, bot_gtp_name, bot_gtp, sgf_g, profile, silentfail=False):
    log(1, "Bot starting procedure started with profile =", profile["profile"])
    log(1, "\tbot name:", bot_name)
    log(1, "\tbot gtp name", bot_gtp_name)

    command_entry = profile["command"]
    parameters_entry = profile["parameters"]

    size = sgf_g.get_size()

    try:

        log(1, "Starting " + bot_name + "...")
        try:
            # bot_command_line=[gcc_config.get(bot_name, command_entry)]+gcc_config.get(bot_name, parameters_entry).split()
            bot_command_line = [command_entry] + parameters_entry.split()
            bot = bot_gtp(bot_command_line)
        except Exception, e:
            raise GCCException("Could not run %s using the command from config.ini file:" % bot_name)

        log(1, bot_name + " started")
        log(1, bot_name + " identification through GTP...")
        try:
            answer = bot.name()
        except Exception, e:
            raise GCCException("%s did not reply as expected to the GTP name command:" % bot_name)

        if bot_gtp_name != 'GtpBot':
            if answer != bot_gtp_name:
                raise GCCException("%s did not identify itself as expected:" % bot_name)
        else:
            bot_gtp_name = answer

        log(1, bot_name + " identified itself properly")
        log(1, "Checking version through GTP...")
        try:
            bot_version = bot.version()
        except Exception, e:
            raise GCCException("%s did not reply as expected to the GTP version command:" % bot_name)

        log(1, "Version: " + bot_version)
        try:
            ok = bot.boardsize(size)
        except:
            raise GCCException("Could not set the goboard size using GTP command. Check that %s is running in GTP mode." % bot_name)

        if not ok:
            raise GCCException("%s rejected this board size (%ix%i)" % (bot_name, size, size))

        bot.reset()

        log(1, "Checking for existing stones or handicap stones on the board")
        gameroot = sgf_g.get_root()
        if node_has(gameroot, "HA"):
            nb_handicap = node_get(gameroot, "HA")
            log(1, "The SGF indicates", nb_handicap, "stone(s)")
        else:
            nb_handicap = 0
            log(1, "The SGF does not indicate handicap stone")
        # import pdb; pdb.set_trace()
        board, unused = sgf_moves.get_setup_and_moves(sgf_g)
        nb_occupied_points = len(board.list_occupied_points())
        log(1, "The SGF indicates", nb_occupied_points, "occupied point(s)")

        free_handicap_black_stones_positions = []
        already_played_black_stones_position = []
        already_played_white_stones_position = []

        for color, move in board.list_occupied_points():
            if move != None:
                row, col = move
                move = ij2gtp((row, col))
                if color.lower() == 'b':
                    if nb_handicap > 0:
                        free_handicap_black_stones_positions.append(move)
                        nb_handicap -= 1
                    else:
                        already_played_black_stones_position.append(move)
                else:
                    already_played_white_stones_position.append(move)

        if len(free_handicap_black_stones_positions) > 0:
            log(1, "Setting handicap stones at", " ".join(free_handicap_black_stones_positions))
            bot.set_free_handicap(free_handicap_black_stones_positions)

        for stone in already_played_black_stones_position:
            log(1, "Adding a black stone at", stone)
            bot.place_black(stone)

        for stone in already_played_white_stones_position:
            log(1, "Adding a white stone at", stone)
            bot.place_white(stone)

        log(1, "Setting komi at", sgf_g.get_komi())
        bot.komi(sgf_g.get_komi())

        log(1, bot_name + " initialization completed")

        bot.bot_name = bot_gtp_name
        bot.bot_version = bot_version
    except Exception, e:
        if silentfail:
            log(0, e)
        else:
            log(0, unicode(e))
        return False
    return bot


def opposite_rate(value):
    return str(100 - float(value[:-1])) + "%"


def get_node_number(node):
    return get_moves_number(node)


def get_node(root, number=0):
    if number == 0:
        return root
    node = root
    k = 0
    while k != number:
        if not node:
            return False
        node = node[0]
        k += 1
    return node


def node_set(node, property_name, value):
    if type(value) == type(u"abc"):
        value = value.encode("utf-8")
    if property_name.lower() in ("w", "b"):
        node.set_move(property_name.encode("utf-8"), value)
    elif property_name.upper() in ("TBM", "TWM", "IBM", "IWM"):
        new_list = []
        for ij in value:
            new_list.append(ij2sgf(ij).encode("utf-8"))
        if type(property_name) == type(u"abc"):
            property_name = property_name.encode("utf-8")
        node.set_raw_list(property_name, new_list)
    else:
        if type(property_name) == type(u"abc"):
            property_name = property_name.encode("utf-8")
        node.set(property_name, value)


def node_get(node, property_name):
    if type(property_name) == type(u"abc"):
        property_name = property_name.encode("utf-8")
    value = node.get(property_name)
    if type(value) == type(str("abc")):
        value = value.decode("utf-8")
    return value


def node_has(node, property_name):
    if type(property_name) == type(u"abc"):
        property_name = property_name.encode("utf-8")
    return node.has_property(property_name)


def guess_color_to_play(move_zero, move_number):
    one_move = go_to_move(move_zero, move_number)

    if one_move == False:
        previous_move_color = guess_color_to_play(move_zero, move_number - 1)
        if previous_move_color.lower() == 'b':
            return "w"
        else:
            return "b"

    player_color, unused = one_move.get_move()
    if player_color != None:
        return player_color

    if one_move is move_zero:
        if node_has(move_zero, "PL"):
            if node_get(move_zero, "PL").lower() == "b":
                return "w"
            if node_get(move_zero, "PL").lower() == "w":
                return "b"
        else:
            return "w"

    previous_move_color = guess_color_to_play(move_zero, move_number - 1)

    if previous_move_color.lower() == 'b':
        return "w"
    else:
        return "b"


def get_available():
    from leela_zero_analysis import LeelaZero

    bots = []
    for bot in [LeelaZero]:
        profiles = get_bot_profiles(bot["name"])
        for profile in profiles:
            bot2 = dict(bot)
            bots.append(bot2)
            for key, value in profile.items():
                bot2[key] = value
    return bots


def get_bot_profiles(bot="", withcommand=True):
    sections = gcc_config.get_sections()
    if bot != "":
        bots = [bot]
    else:
        bots = ["LeelaZero"]
    profiles = []
    for section in sections:
        for bot in bots:
            if bot + "-" in section:
                command = gcc_config.get(section, "command")
                if (not command) and (withcommand == True):
                    continue
                data = {"bot": bot, "command": "", "parameters": "", "timepermove": "", "variations": "4",
                        "deepness": "4"}
                for option in gcc_config.get_options(section):
                    value = gcc_config.get(section, option)
                    data[option] = value
                profiles.append(data)

    return profiles
