import re


# Returns the command in a given text. The commands are matched as tokens
# between spaces, between single quotes or between double quotes.
# For example:
#    @spinnakerbot add-label foo "bar baz"
# will return a generator with three commands:
#    ['do-something', 'foo', 'bar baz']
def GetCommands(text):
    if not text:
        return None

    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith('@spinnakerbot'):
            command = line[len('@spinnakerbot'):].replace(": :", "::").strip()
            if len(command) > 0:
                tokens = re.split("\ |\"(.*)\"|'(.*)'", command)
                yield [t for t in tokens if t is not None and t != ""]

