def conf(object, property):
    return "conf(%s, %s)" % (object, property)


def dims(object, property):
    return "dims(%s, %s)" % (object, property)


def eval_(s):
    return "eval(%s)" % s


def from_(s):
    return "from(%s)" % s


def log(s):
    return "log(%s)" % s


def on(s):
    return "on(s)" % s


def var(s):
    return "var(%s)" % s