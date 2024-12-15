import numpy as np
import datetime

from osu_interfaces import IReplay
from osu_interfaces import Gamemode, Mod

from .replay_idx import ReplayIdx



class Replay(IReplay):

    PLAYFIELD_WIDTH  = 512  # osu!px
    PLAYFIELD_HEIGHT = 384  # osu!px

    def __init__(self):
        self.game_mode     = None
        self.game_version  = None
        self.beatmap_hash  = ''
        self.player_name   = ''
        self.replay_hash   = ''
        self.num_300s      = None
        self.num_100s      = None
        self.num_50s       = None
        self.gekis         = None
        self.katus         = None
        self.misses        = None
        self.score         = None
        self.max_combo     = None
        self.is_pf         = None
        self.mods          = Mod(0)
        self.life_bar_data = ''
        self.timestamp     = datetime.datetime.min
        self.data          = np.empty(0)
        self.mania_keys    = None
        self.score_id      = None


    def __repr__(self):
        txt = (
            f'{self.get_name()}\n'
            f'data:\n'
            f'{str(self.data.astype(np.int32))}'
        )
        return txt


    def is_md5_match(self, md5_hash):
        return self.beatmap_hash == md5_hash


    def get_name(self):
        assert self.num_300s is not None
        assert self.num_100s is not None
        assert self.num_50s  is not None
        assert self.gekis    is not None
        assert self.katus    is not None
        assert self.misses   is not None

        player_mods = f'{self.player_name} {self.get_mods_name()}'
        score_acc   = f'{self.score} (x{self.max_combo}, {self.get_acc()}%)'
        hits_misses = f'{self.num_300s + self.gekis}/{self.num_100s + self.katus}/{self.num_50s}/{self.misses}'
        return f'{player_mods} - {score_acc} | {hits_misses}'


    def get_acc(self):
        if self.game_mode == Gamemode.OSU:
            acc = 100*self.__get_acc_from_hits_std()

        if self.game_mode == Gamemode.TAIKO:
            acc = -1
            # TODO
            pass

        if self.game_mode == Gamemode.CATCH:
            acc = -1
            # TODO
            pass

        if self.game_mode == Gamemode.MANIA:
            acc = 100*self.__get_acc_from_hits_mania()

        return round(acc, 3)


    def get_num_hits(self):
        assert self.num_300s is not None
        assert self.num_100s is not None
        assert self.num_50s  is not None
        assert self.gekis    is not None
        assert self.katus    is not None
        assert self.misses   is not None

        return self.num_300s + self.gekis + self.katus + self.num_100s + self.num_50s + self.misses


    def get_mods_name(self):
        return str(self.mods)


    def get_time_data(self):
        return self.data[:, ReplayIdx.DT]


    def get_press_data(self):
        return self.data[:, ReplayIdx.KP]


    def get_xpos_data(self):
        return self.data[:, ReplayIdx.PX]


    def get_ypos_data(self):
        return self.data[:, ReplayIdx.PY]


    def get_mania_keys(self):
        return self.mania_keys


    def get_data_at_time(self, time: int):
        time_data = self.data[:, ReplayIdx.DT]
        idx = np.searchsorted(time_data, time)

        if idx == 0:
            return self.data[0]

        if idx == time_data.shape[0]:
            return self.data[-1]

        if abs(time_data[idx] - time) > abs(time_data[idx - 1] - time):
            return self.data[idx]

        return self.data[idx - 1]


    def get_data_at_time_range(self, time_start: int, time_end: int, selector=None):
        time_data = self.data[:, ReplayIdx.DT]
        sel = (time_start <= time_data) & (time_data <= time_end)
        return np.where(sel)[0]


    def __get_acc_from_hits_std(self):
        assert self.num_300s is not None
        assert self.num_100s is not None
        assert self.num_50s  is not None
        assert self.gekis    is not None
        assert self.katus    is not None
        assert self.misses   is not None

        score_hits  = 50*self.num_50s + 100*(self.num_100s + self.katus) + 300*(self.num_300s + self.gekis)
        score_total = 300*(self.misses + self.num_50s + (self.num_100s + self.katus) + (self.num_300s + self.gekis))
        return score_hits/score_total


    def __get_acc_from_hits_mania(self):
        assert self.num_300s is not None
        assert self.num_100s is not None
        assert self.num_50s  is not None
        assert self.gekis    is not None
        assert self.katus    is not None
        assert self.misses   is not None

        score_hits  = 50*self.num_50s + 100*self.num_100s + 200*self.katus + 300*(self.num_300s + self.gekis)
        score_total = 300*(self.misses + self.num_50s + self.num_100s + self.katus + (self.num_300s + self.gekis))
        return score_hits/score_total
