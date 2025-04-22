def header(text):
    return f"### {text}"


def subheader(text):
    return f"## {text}"


def bold(text):
    return f"**{text}**"


def underline(text):
    return f"__{text}__"


def italic(text):
    return f"*{text}*"


def strikethrough(text):
    return f"~{text}~"


def code(text):
    return f"`{text}`"


def link(text, url):
    return f"[{text}]({url})"


def paragraph(*lines):
    return "\n".join(lines)


def combine(*parts):
    return "".join(parts)
