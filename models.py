import sys
import utils


class Log():
    COLOR_BLACK = 30
    COLOR_RED = 31
    COLOR_GREEN = 32
    COLOR_YELLOW = 33
    COLOR_BLUE = 34
    COLOR_MAGENTA = 35
    COLOR_CYAN = 36
    COLOR_WHITE = 37

    def write(self, text, color):
        sys.stdout.write('\x1b[%s;1m%s\x1b[0m' % (color, text))


class Post():
    def __init__(self, id, created, title, score, upVoteRatio, nbComments):
        self.id = str(id)
        self.intCreated = int(created)
        self.strCreated = utils.timestamp_to_string(int(created))
        self.title = str(title).replace("\n", "").strip()
        self.score = int(score)
        self.upVoteRatio = int(upVoteRatio)
        self.nbComments = str(nbComments).split(" ")[0]

    def __str__(self):
        Log().write('id=' + self.id + ' (', Log.COLOR_BLACK)
        if self.intCreated:
            Log().write('created=' + self.strCreated + ') : ', Log.COLOR_BLACK)
        Log().write('title=' + self.title + ' | ', Log.COLOR_GREEN)
        Log().write('score=' + str(self.score) + ', ', Log.COLOR_BLUE)
        Log().write('upVoteRatio=' + str(self.upVoteRatio) + ', ', Log.COLOR_BLUE)
        Log().write('nbComments=' + self.nbComments, Log.COLOR_RED)
        return ""

    def to_dict(self):
        return {
            'id': self.id,
            'intCreated': self.intCreated,
            'strCreated': self.strCreated,
            'title': self.title,
            'score': self.score,
            'upVoteRatio': self.upVoteRatio,
            'nbComments': self.nbComments,
        }
