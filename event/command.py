def GetCommands(text):
    if not text:
        return None

    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith('@spinnakerbot'):
            command = line[len('@spinnakerbot'):].replace(": :", "::").strip()
            if len(command) > 0:
                yield command.split()
