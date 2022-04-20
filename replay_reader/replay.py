from osu_interfaces import IReplay
from .replay_idx import ReplayIdx
from .gamemode import Gamemode



class Replay(IReplay):

    PLAYFIELD_WIDTH  = 512  # osu!px
    PLAYFIELD_HEIGHT = 384  # osu!px

    def __init__(self):
        self.game_mode     = None
        self.game_version  = None
        self.beatmap_hash  = None
        self.player_name   = None
        self.replay_hash   = None
        self.num_300s      = None
        self.num_100s      = None
        self.num_50s       = None
        self.gekis         = None
        self.katus         = None
        self.misses        = None
        self.score         = None
        self.max_combo     = None
        self.is_pf         = None
        self.mods          = None
        self.life_bar_data = None
        self.timestamp     = None
        self.play_data     = None
        self.mania_keys    = None
        self.score_id      = None


    def is_md5_match(self, md5_hash):
        return self.beatmap_hash == md5_hash


    def get_name(self):
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
        return self.number_300s + self.gekis + self.katus + self.number_100s + self.number_50s + self.misses


    def get_mods_name(self):
        return str(self.mods)


    def get_time_data(self):
        return self.play_data[:, ReplayIdx.DT]


    def get_press_data(self):
        return self.play_data[:, ReplayIdx.KP]

    
    def get_xpos_data(self):
        return self.play_data[:, ReplayIdx.PX]


    def get_ypos_data(self):
        return self.play_data[:, ReplayIdx.PY]


    def get_mania_keys(self):
        return self.mania_keys


    def get_data_at_time(self, time, selector=None):
        idx = find(self.get_event_times(), time, selector=selector)
        return self.play_data[idx]


    def get_data_at_time_range(self, time_start, time_end, selector=None):
        idx_start = find(self.get_event_times(), time_start, selector=selector)
        idx_end   = find(self.get_event_times(), time_end, selector=selector)
        return self.play_data[idx_start : idx_end]


    def __get_acc_from_hits_std(self):
        score_hits  = 50*self.num_50s + 100*(self.num_100s + self.katus) + 300*(self.num_300s + self.gekis)
        score_total = 300*(self.misses + self.num_50s + (self.num_100s + self.katus) + (self.num_300s + self.gekis))
        return score_hits/score_total

    
    def __get_acc_from_hits_mania(self):
        score_hits  = 50*self.num_50s + 100*self.num_100s + 200*self.katus + 300*(self.num_300s + self.gekis)
        score_total = 300*(self.misses + self.num_50s + self.num_100s + self.katus + (self.num_300s + self.gekis))
        return score_hits/score_total
