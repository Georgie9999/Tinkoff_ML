import numpy as np
import ast
import re
import argparse
import pickle

class Check_code:
    def __init__(self, file):
        code_text = open(file, encoding='utf-8').read()

        code_text = re.sub(r'"""[.\w\W]+\"""', '', code_text)
        self.code = code_text
        self.ast = ast.dump(ast.parse(code_text))

    @classmethod
    def Levenshtein_dist(cls, string, string2):
        S1, S2 = ast.dump(ast.parse(string)), ast.dump(ast.parse(string2))
        N, M = len(S1), len(S2)
        D = np.zeros((N, M))
        D[:, 0] = [i for i in range(N)]
        D[0] = [i for i in range(M)]
        for i in range(1, N):
            for j in range(1, M):
                D[i][j] = min(D[i - 1][j] + 1, D[i][j - 1] + 1, D[i - 1][j - 1] + int(S1[i] != S2[j]))
        return D[-1][-1]

    def similarity(self, string2):
        count1 = 0

        S1, S2 = list(ast.walk(ast.parse(self.code)))[1:], list(ast.walk(ast.parse(string2.code)))[1:]
        code_len = 0
        for l in range(min(len(S2), len(S1))):
            code_len += max(len(ast.dump(S1[l])), len(ast.dump(S2[l])))
            if type(S1[l]) != type(S2[l]):
                count1 += self.Levenshtein_dist(S1[l], S2[l])
            else:
                D1, D2 = S1[l].__dict__, S2[l].__dict__
                for x in D1:
                    if type(D1[x]) not in [int, float, list, str, bytes] and D1[x] != None:
                        t1, t2 = ast.dump(D1[x]), ast.dump(D2[x])
                        count1 += self.Levenshtein_dist(D1[x], D2[x])
                    elif type(D1[x]) == list:
                        for (y1, y2) in zip(D1[x], D2[x]):
                            count1 += self.Levenshtein_dist(y1, y2)
        return 1 - count1 / code_len

parser = argparse.ArgumentParser()

parser.add_argument('file_input')
parser.add_argument('file_output')

arg = parser.parse_args()

F1 = open(arg.file_input, encoding='utf-8')
Scores = []
for line in F1:
    line= line.strip('\n')
    f1, f2 = line.split()
    code1, code2 = Check_code(f1), Check_code(f2)
    Scores.append(code1.similarity(code2))
F1.close()
F2 = open(arg.file_output, 'w', encoding='utf-8')
for score in Scores:
    F2.write(f"{score} \n")
F2.close()