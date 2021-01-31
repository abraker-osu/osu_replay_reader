import unittest
import numpy as np

from replay_reader.replayIO import ReplayIO
from replay_reader.replayIO import ReplayException


class TestReplay(unittest.TestCase):

    def load_replay(self, filepath):
        replay = ReplayIO.open_replay(filepath)

        print()
        print(replay.get_name())
        print(f'Player: {replay.player_name}')
        print(f'Score: {replay.score}   Combo: {replay.max_combo}   PF: {replay.is_pf}   Mods: {str(replay.mods)}')
        print(f'Hits: {replay.num_300s}/{replay.gekis}/{replay.num_100s}/{replay.katus}/{replay.num_50s}/{replay.misses}')
        print()


    def test_replay_loading(self):
        self.load_replay('unit_tests\\replays\\osu\\abraker - Mutsuhiko Izumi - Red Goose [ERT Basic] (2019-08-24) Osu.osr')
        self.load_replay('unit_tests\\replays\\osu\\LeaF - I (Maddy) [Terror] replay_0.osr')
        self.load_replay('unit_tests\\replays\\osu\\so bad - Nakamura Meiko - Aka no Ha [Extra] (2020-03-01) std Osu.osr')
        self.load_replay('unit_tests\\replays\\osu\\so bad - Nakamura Meiko - Aka no Ha [Extra] (2020-03-01) std ripple.osr')
        self.load_replay('unit_tests\\replays\\osu\\Toy - Within Temptation - The Unforgiving [Marathon] (2018-02-06) Osu.osr')


    def test_replay_press(self):
        replay = ReplayIO.open_replay('unit_tests\\replays\\osu\\LeaF - I (Maddy) [Terror] replay_0.osr')
        key_presses = replay.get_press_data()
        self.assertEqual(np.all(key_presses == 0), False, 'Blank replay data!')
        
        replay = ReplayIO.open_replay('unit_tests\\replays\\osu\\abraker - Mutsuhiko Izumi - Red Goose [ERT Basic] (2019-08-24) Osu.osr')
        key_presses = replay.get_press_data()
        self.assertEqual(np.all(key_presses == 0), False, 'Blank replay data!')

        with self.assertRaises(ReplayException):
            replay = ReplayIO.open_replay('unit_tests\\replays\\mania\\osu!topus! - DJ Genericname - Dear You [S.Star\'s 4K HD+] (2019-05-29) OsuMania.osr')