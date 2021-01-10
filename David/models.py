import sys
from datetime import datetime, timezone

class Log():
    COLOR_BLACK =30
    COLOR_RED=31
    COLOR_GREEN=32
    COLOR_YELLOW=33
    COLOR_BLUE=34
    COLOR_MAGENTA=35
    COLOR_CYAN=36
    COLOR_WHITE=37

    def write(self, text, color):
        sys.stdout.write('\x1b[%s;1m%s\x1b[0m' % (color, text))

class Post():
    def __init__(self, id, created, title, nbVotes, nbComments):
        self.id = str(id)
        self.created = int(created)
        self.title = str(title).replace(" ", "").replace("\n", "")
        self.nbVotes = str(nbVotes)
        self.nbComments = str(nbComments).split(" ")[0]

    def __str__(self):
        Log().write('id=' + self.id + ' (', Log.COLOR_BLACK)
        if self.created:
            Log().write('created=' + datetime.fromtimestamp(self.created, timezone.utc).strftime("%Y-%m-%d %H:%M:%S") + ') : ', Log.COLOR_BLACK)
        Log().write('title=' + self.title + ' | ', Log.COLOR_GREEN)
        Log().write('nbVotes=' + self.nbVotes + ', ', Log.COLOR_BLUE)
        Log().write('nbComments=' + self.nbComments, Log.COLOR_RED)
        return ""

