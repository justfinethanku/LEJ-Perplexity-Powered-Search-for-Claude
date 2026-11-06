#!/usr/bin/env python3
"""Write Markdown from stdin to a new, private project research file (POSIX)."""

import os
import re
import sys
import uuid


def save_research(prefix, content):
    if not re.fullmatch(r"[A-Za-z0-9-]{1,100}", prefix):
        raise ValueError("Invalid research filename prefix")

    directory = ".perplexity-research"
    try:
        os.mkdir(directory, 0o700)
    except FileExistsError:
        pass

    # O_NOFOLLOW rejects even an existing directory symlink. Keep this fd open:
    # replacing the directory pathname afterwards cannot redirect the file open.
    directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        filename = f"{prefix}-{uuid.uuid4().hex}.md"
        file_fd = os.open(
            filename,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=directory_fd,
        )
        try:
            with os.fdopen(file_fd, "w", encoding="utf-8") as output:
                output.write(content)
        except BaseException:
            os.unlink(filename, dir_fd=directory_fd)
            raise
    finally:
        os.close(directory_fd)
    return f"{directory}/{filename}"


def main():
    try:
        filename = save_research(sys.argv[1], sys.stdin.read())
    except (OSError, ValueError):
        print("Research not saved: unsafe or inaccessible research path.", file=sys.stderr)
        return 1
    print(f"Research saved to {filename}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
