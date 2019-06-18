from os import listdir, walk
from os.path import isfile, join
import sys
import ast
import matplotlib.pyplot as plt
import numpy as np


# intersection of two lists
def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


# find intersection of games which was calculated by all available
def get_intersection_sgfs(path_to_sgfs):
    sgf_directories = [x[0] for x in walk(path_to_sgfs)][1:]
    united_sgf_list = [f for f in listdir(sgf_directories[0]) if isfile(join(sgf_directories[0], f))]
    for dir in sgf_directories[1:]:
        united_sgf_list = intersection(united_sgf_list, [f for f in listdir(dir) if isfile(join(dir, f))])
    return sgf_directories, united_sgf_list


def get_asgfs(path_to_sgfs):
    sgf_directories = [x[0] for x in walk(path_to_sgfs)]
    united_sgf_list = [f for f in listdir(sgf_directories[0]) if isfile(join(sgf_directories[0], f))]
    for dir in sgf_directories[1:]:
        united_sgf_list = intersection(united_sgf_list, [f for f in listdir(dir) if isfile(join(dir, f))])
    return sgf_directories, united_sgf_list


# Move #20, made by b: Played at M6, -2.83% in WR.
# All stats: {u'max reading depth': 32, u'variations':
# [{u'value network win rate': u'57.82%', u'policy network value': u'41.60%', u'sequence': u'Q7 M6 G3 C14 R14 P8 P7 O7 O8 P9 N8 L8 N10 P11 R9 Q14 L10 J8 Q13 P14', u'playouts': u'7617', u'first move': u'Q7'},
# {u'value network win rate': u'57.27%', u'policy network value': u'27.91%', u'sequence': u'Q8 M6 G3 C14 R14 Q14 Q13 P14 S15 R17 P13 O13 O12 N12 O11 N11 O10 N10 O9 N9 O8', u'playouts': u'1968', u'first move': u'Q8'},
# {u'value network win rate': u'54.61%', u'policy network value': u'23.45%', u'sequence': u'M6 Q7 M8 N7 M7 O9 R14 R12 R17 R16 Q17 P16 S16 S15 S17', u'playouts': u'407', u'first move': u'M6'},
# {u'value network win rate': u'52.61%', u'policy network value': u'0.78%', u'sequence': u'O2 N2 Q7 M6 G3 P8', u'playouts': u'9', u'first move': u'O2'}], u'average reading depth': 11.2}

# parser of sgf
class ASGFAnalyzer:
    def __init__(self, asgf):
        self.asgf = asgf
        self.w_rank = "?"
        self.b_rank = "?"
        self.moves = list()
        self.start_move = 0
        self.nb_moves = 0
        self.parse_sgf()

        self.style_w = ""
        self.style_b = ""
        self.w_moves = list()
        self.w_winrate_drop = list()
        self.b_moves = list()
        self.b_winrate_drop = list()
        self.get_wr_drop()

    def parse_sgf(self):
        with open(self.asgf, 'r') as f:
            contents = f.readlines()

        for line in contents:
            if line.startswith("Rank"):
                self.w_rank = line.split(" ")[3][:-1].strip()
                self.b_rank = line.split(" ")[7].strip()
            if line.startswith("Move"):
                data = self.parse_move_data(line)
                self.moves.append(data)

        try:
            if contents[1].startswith("Move"):
                self.start_move = int(contents[1].split("#")[1].split(",")[0])
            if contents[-1].startswith("Move"):
                self.nb_moves = int(contents[-1].split("#")[1].split(",")[0])
        except IndexError:
            print (".asgf file is too short for analysis, quit now...")
            print self.asgf
            sys.exit()
        f.close()

    @staticmethod
    def parse_move_data(move_data):
        move_number = move_data.split("#")[1].split(",")[0]
        if "made by b" in move_data:
            move_color = "b"
        else:
            move_color = "w"

        move_coordinates = move_data.split(",")[1][-3:].strip()  # coordinates with KGS style (skipping 'i' letter)
        move_winrate_drop = move_data.split(",")[2].split("%")[0].strip()
        move_variations = move_data.split("All stats: ")[1].strip()

        # print move_data
        move = {"number"     : int(move_number),
                "color"      : move_color,
                "coordinates": move_coordinates,
                "wr_drop"    : float(move_winrate_drop),
                "variations" : ast.literal_eval(move_variations)["variations"]}
        return move

    @staticmethod
    def get_mse(wr_drop):
        return (np.array(wr_drop)).mean()
        # print np.array(wr_drop)
        # print np.array(wr_drop).mean()
        # print (np.square(np.array(wr_drop)))
        # print (np.square(np.array(wr_drop))).mean()
        # print "-------------------------------"
        # return (np.square(np.array(wr_drop))).mean()

    def get_wr_drop(self):
        self.w_moves = [i for i in range(self.start_move, self.nb_moves + 1) if i % 2 == 0]
        self.w_winrate_drop = [move["wr_drop"] for move in self.moves if move["number"] in self.w_moves]
        self.b_moves = [i for i in range(self.start_move, self.nb_moves + 1) if i % 2 == 1]
        self.b_winrate_drop = [move["wr_drop"] for move in self.moves if move["number"] in self.b_moves]

if __name__ == '__main__':
    # dirs, sgfs = get_intersection_sgfs("Z:\sgf\LeelaZero_100\\")
    dirs, sgfs = get_asgfs("Z:\\results\\")
    fig = plt
    ranks = list()
    mse_ranks = dict()
    x_by_ranks = dict()
    for i in range(1, 16):
        mse_ranks[str(i) + "k"] = list()
        x_by_ranks[str(i) + "k"] = 16 - i
        ranks.append(str(11-i) + "k")
    for i in range(1, 10):
        mse_ranks[str(i) + "d"] = list()
        x_by_ranks[str(i) + "d"] = i + 10
        ranks.append(str(i) + "d")
    mse_ranks["?"] = list()

    mses = dict()
    for sgf in sgfs:
        mses[sgf] = list()
        for dir in sorted(dirs):
            asgf = ASGFAnalyzer(dir + "\\" + sgf)
            mse_ranks[asgf.w_rank].append(asgf.get_mse(asgf.w_winrate_drop))
            mse_ranks[asgf.b_rank].append(asgf.get_mse(asgf.b_winrate_drop))
            mses[sgf].append(dir.split("\\")[-1] + " w:{0}, b:{1}".format(asgf.get_mse(asgf.w_winrate_drop), asgf.get_mse(asgf.b_winrate_drop)))
            # if "10k" in dir:
                # asgf.set_line_style("co", "bo")
                # asgf.set_line_style("bo", "bo")
            # if "2k" in dir:
                # asgf.set_line_style("ko", "ro")
                # asgf.set_line_style("g*", "go")
            # if "5k" in dir:
                # asgf.set_line_style("yo", "go")
                # asgf.set_line_style("rp", "ro")
            # asgf.get_wr_drop(fig)
            if asgf.w_rank != "?":
                # if "10k" in dir or "100" in dir:
                fig.plot(x_by_ranks[asgf.w_rank], asgf.get_mse(asgf.w_winrate_drop), marker='o', markersize=6, color="blue")
                if "2k" in dir:
                    fig.plot(x_by_ranks[asgf.w_rank], asgf.get_mse(asgf.w_winrate_drop), marker='*', markersize=6, color="green")
                if "5k" in dir:
                    fig.plot(x_by_ranks[asgf.w_rank], asgf.get_mse(asgf.w_winrate_drop), marker='p', markersize=6, color="red")
            if asgf.b_rank != "?":
                # if "10k" in dir or "100" in dir:
                fig.plot(x_by_ranks[asgf.b_rank], asgf.get_mse(asgf.b_winrate_drop), marker='o', markersize=6, color="blue")
                if "2k" in dir:
                    fig.plot(x_by_ranks[asgf.b_rank], asgf.get_mse(asgf.b_winrate_drop), marker='*', markersize=6, color="green")
                if "5k" in dir:
                    fig.plot(x_by_ranks[asgf.b_rank], asgf.get_mse(asgf.b_winrate_drop), marker='p', markersize=6, color="red")
            # fig.legend(["10k", "2k", "5k"])

    fig.xticks(range(1, 25), ranks)
    print mses

    fig.show()
