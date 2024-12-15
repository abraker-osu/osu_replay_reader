"""
Data representation of opened replay

NOTE: If changes were made, run refresh.bat to apply replay_reader changes to venv
"""
from replay_reader import ReplayIO


if __name__ == "__main__":
    replay = ReplayIO.open_replay('tests/data/replays/osu/abraker - Mutsuhiko Izumi - Red Goose [ERT Basic] (2019-08-24) Osu.osr')
    print(replay)
