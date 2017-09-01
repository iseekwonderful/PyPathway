from IPython.display import HTML
import os
import time


__VERSION__ = 0.23


def iframe(source, ratio=10 / 16):
    with open(os.path.dirname(os.path.abspath(__file__)) + "/template.html") as fp:
        con = fp.read()
    con = con.replace("{{time}}", str(int(time.time()))).replace("{{ratio}}", str(ratio)).replace("{{path}}", source)
    return HTML(con)