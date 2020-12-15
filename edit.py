import os
import subprocess
import tempfile


def edit(editor: str = None, extension: str = ".md"):

    editor = editor if editor else os.environ.get("EDITOR")
    if not editor:
        raise RuntimeError(
            "Editor not found, please specify or set EDITOR environment variable"
        )

    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", suffix=extension) as f:
        cmd = f"{editor} {f.name}"
        subprocess.run(cmd, shell=True, check=True)
        contents = f.read()
    return contents


# for testing only
if __name__ == "__main__":
    print(edit())
