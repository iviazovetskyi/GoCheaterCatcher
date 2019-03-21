from os import listdir, walk
from os.path import isfile, join
# import numpy as np


# intersection of two lists
def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


# find intersection of games which was calculated by all available
def get_intersection_sgfs(path_to_sgfs="Z:\sgf\\"):
    sgf_directories = [x[0] for x in walk(path_to_sgfs)][1:]
    united_sgf_list = [f for f in listdir(sgf_directories[0]) if isfile(join(sgf_directories[0], f))]
    for dir in sgf_directories[1:]:
        united_sgf_list = intersection(united_sgf_list, [f for f in listdir(dir) if isfile(join(dir, f))])
    return sgf_directories, united_sgf_list


# parser of sgf
class ASGFAnalyzer:
    def __init__(self, sgf):
        self.sgf = sgf
        self.w_rank = "?"
        self.b_rank = "?"
        self.moves = dict()
        self.parse_sgf()

    def parse_sgf(self):
        with open(self.sgf, 'r') as f:
            contents = f.readlines()

        for line in contents:
            if line.startswith("Rank"):
                w_rank = line.split(" ")[3][:-1].strip()
                b_rank = line.split(" ")[7].strip()
            if line.startswith("Move"):
                self.parse_move_data(line)

        # try:
        #     print w_rank + " " + b_rank
        # except Exception:
        #     print "no rank specified in: " + self.sgf

    @staticmethod
    def parse_move_data(move_data):
        move_number = move_data.split("#")[1].split(",")[0]
        if "made by b" in move_data:
            move_color = "b"
        else:
            move_color = "w"

        move_coordinates = move_data.split(",")[1][-3:].strip()  # coordinates with KGS style (skipping 'i' letter)

        # print move_data
        move = {"number"     : move_number,
                "color"      : move_color,
                "coordinates": move_coordinates}
        print(move)
        return move


# Move #20, made by b: Played at M6, -2.83% in WR.
# All stats: {u'max reading depth': 32, u'variations':
# [{u'value network win rate': u'57.82%', u'policy network value': u'41.60%', u'sequence': u'Q7 M6 G3 C14 R14 P8 P7 O7 O8 P9 N8 L8 N10 P11 R9 Q14 L10 J8 Q13 P14', u'playouts': u'7617', u'first move': u'Q7'},
# {u'value network win rate': u'57.27%', u'policy network value': u'27.91%', u'sequence': u'Q8 M6 G3 C14 R14 Q14 Q13 P14 S15 R17 P13 O13 O12 N12 O11 N11 O10 N10 O9 N9 O8', u'playouts': u'1968', u'first move': u'Q8'},
# {u'value network win rate': u'54.61%', u'policy network value': u'23.45%', u'sequence': u'M6 Q7 M8 N7 M7 O9 R14 R12 R17 R16 Q17 P16 S16 S15 S17', u'playouts': u'407', u'first move': u'M6'},
# {u'value network win rate': u'52.61%', u'policy network value': u'0.78%', u'sequence': u'O2 N2 Q7 M6 G3 P8', u'playouts': u'9', u'first move': u'O2'}], u'average reading depth': 11.2}




dirs, sgfs = get_intersection_sgfs()
ASGFAnalyzer(dirs[0] + "\\" + sgfs[0])