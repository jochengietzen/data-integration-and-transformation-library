import subprocess
from pathlib import Path

CURRENT_FILE = Path(__file__)
ROOT = CURRENT_FILE.parent.parent

EXAMPLES = ROOT / "examples"

BORDER = "====="


def test_examples():
    entry_points = list(EXAMPLES.iterdir())

    for entry_point in entry_points:
        print(BORDER, "Running tests on directory", entry_point.name, BORDER)

        executables = []
        for root, _, files in (entry_point / "src").walk():
            for file in files:
                if not file.endswith(".py"):
                    continue
                file_path = root / file
                # print(BORDER*2, file_path, BORDER*2)
                with open(file_path, encoding="utf-8") as file:
                    if 'if __name__ == "__main__":' in file.read():
                        executables.append(file_path)

        for executable in executables:
            print([str(entry_point / ".venv/bin/python"), str(executable)])
            subprocess.check_output([str(entry_point / ".venv/bin/python"), str(executable)])


if __name__ == "__main__":
    test_examples()
