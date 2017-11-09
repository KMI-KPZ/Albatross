import math


def classifier(data, num_level):
    step_size = round((max(data) - min(data)) / num_level)
    breaks = [x for x in range(int(min(data)), int(max(data)), int(step_size))]

    ud = []
    for d in data:
        lvl = 0
        for i, b in enumerate(breaks):
            if b <= d:
                lvl = i
            else:
                break
        ud.append(lvl)
    return ud


data = [0, 1, 2, 3, 4, 5, 6, 7, 8, float('nan'), 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
lvls = 4

ud = classifier(data, lvls)

for i in range(0, len(data)):
    print("{}: {}".format(data[i], ud[i]))