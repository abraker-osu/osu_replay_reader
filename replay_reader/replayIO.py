import datetime
import struct
import lzma
import math
import os

import numpy as np

from .replay import Replay
from .replay_idx import ReplayIdx
from .gamemode import Gamemode
from .mod import Mod



class ReplayException(Exception):
    pass



class ReplayIO():

    __BYTE  = 1
    __SHORT = 2
    __INT   = 4
    __LONG  = 8

    """
    Opens a replay file and reads it

    Args:
        filepath: (string) filepath to the replay file to load
    """
    @staticmethod
    def open_replay(filepath=None):
        with open(filepath, 'rb') as replay_file:
            return ReplayIO.load_replay(replay_file.read())


    """
    Loads replay data

    Args:
        replay_data: (string) contents of the replay file
    """
    @staticmethod
    def load_replay(replay_data):
        replay = Replay()

        ReplayIO.__offset = 0
        ReplayIO.__parse_game_mode_and_version(replay_data, replay)
        ReplayIO.__parse_beatmap_hash(replay_data, replay)
        ReplayIO.__parse_player_name(replay_data, replay)
        ReplayIO.__parse_replay_hash(replay_data, replay)
        ReplayIO.__parse_score_stats(replay_data, replay)
        ReplayIO.__parse_life_bar_data(replay_data, replay)
        replay_length = ReplayIO.__parse_timestamp_and_replay_length(replay_data, replay)
        ReplayIO.__parse_play_data(replay_data, replay, replay_length)
        
        return replay


    """
    Saves replay data to file

    Args:
        replay_data: (string) contents of the replay file
        filepath: (string) filepath where to save the replay data
    """
    @staticmethod
    def save_replay(replay_data, filepath):
        path = os.path.dirname(filepath)
        if not os.path.exists(path):
            os.makedirs(path)
            
        with open(filepath, 'wb') as f:
            f.write(replay_data)


    @classmethod
    def __parse_game_mode_and_version(cls, replay_data, replay):
        fmt = '<bi'
        data = struct.unpack_from(fmt, replay_data, cls.__offset)
        replay.game_mode, replay.game_version = Gamemode(data[0]), data[1]

        cls.__offset += struct.calcsize(fmt)


    @classmethod
    def __parse_beatmap_hash(cls, replay_data, replay):
        replay.beatmap_hash = cls.__parse_string(replay_data)


    @classmethod
    def __parse_player_name(cls, replay_data, replay):
        replay.player_name = cls.__parse_string(replay_data)


    @classmethod
    def __parse_replay_hash(cls, replay_data, replay):
        replay.replay_hash = cls.__parse_string(replay_data)


    @classmethod
    def __parse_score_stats(cls, replay_data, replay):
        fmt = '<hhhhhhih?i'

        (
            replay.num_300s,
            replay.num_100s,
            replay.num_50s,
            replay.gekis,
            replay.katus,
            replay.misses,
            replay.score,
            replay.max_combo,
            replay.is_pf,
            replay.mods
        ) = struct.unpack_from(fmt, replay_data, cls.__offset)
        replay.mods = Mod(replay.mods)

        cls.__offset += struct.calcsize(fmt)


    @classmethod
    def __parse_life_bar_data(cls, replay_data, replay):
        # Apperently there is a special exception if life bar data is blank
        if replay_data[cls.__offset] == 0x0B:
            replay.life_bar_data = cls.__parse_string(replay_data)
        else:
            cls.__offset += ReplayIO.__BYTE

        # I don't even... 
        # A replay that's missing game version number is weird, but
        # until I come across another case like this that doesn't work,
        # this is to allow the Leaf - I replay to load
        if replay.game_version == 0:
            cls.__offset += ReplayIO.__BYTE


    @classmethod
    def __parse_timestamp_and_replay_length(cls, replay_data, replay):
        fmt = '<qi'
        t, replay_length = struct.unpack_from(fmt, replay_data, cls.__offset)
        replay.timestamp = datetime.datetime.min + datetime.timedelta(microseconds=t/10)
        
        cls.__offset += struct.calcsize(fmt)
        return replay_length


    @classmethod
    def __parse_play_data(cls, replay_data, replay, replay_length):
        offset_end = cls.__offset + replay_length
        datastring = lzma.decompress(replay_data[cls.__offset : offset_end], format=lzma.FORMAT_AUTO).decode('ascii')[:-1]
        cls.__offset = offset_end

        events = [ eventstring.split('|') for eventstring in datastring.split(',') ]

        # osu! versions 20130319 or later
        if int(events[-1][0]) == -12345:
            # If rnd value is 0, then something is wrong
            if int(events[-1][3]) == 0:
                raise ReplayException('Replay might be corrupt!')

        if (replay.game_mode == Gamemode.OSU) and replay.mods.has_mod(Mod.HardRock):
            replay.play_data = np.asarray([ 
                [ int(event[ReplayIdx.DT]), float(event[ReplayIdx.PX]), Replay.PLAYFIELD_HEIGHT - float(event[ReplayIdx.PY]), int(event[ReplayIdx.KP]) ] 
                for event in events if int(event[0]) != -12345
            ])
        else:
            replay.play_data = np.asarray([ 
                [ int(event[ReplayIdx.DT]), float(event[ReplayIdx.PX]), float(event[ReplayIdx.PY]), int(event[ReplayIdx.KP]) ] 
                for event in events if int(event[0]) != -12345 
            ])
        
        if replay.game_mode == Gamemode.MANIA:
            # Calculate number of keys used in the replay for mania
            largest_key_event = max(replay.play_data, key=lambda event: event[ReplayIdx.PX])
            replay.mania_keys = int(math.log(largest_key_event[ReplayIdx.PX], 2)/2)


    @classmethod
    def __parse_string(cls, replay_data):
        if replay_data[cls.__offset] == 0x00:
            begin = cls.__offset = cls.__offset + ReplayIO.__BYTE

            while replay_data[cls.__offset] != 0x00: 
                cls.__offset += ReplayIO.__BYTE
            
            cls.__offset += ReplayIO.__BYTE
            return replay_data[begin : cls.__offset - 2].decode("utf-8")
        
        if replay_data[cls.__offset] == 0x0b:
            cls.__offset += ReplayIO.__BYTE
            
            string_length = cls.__decode(replay_data)
            offset_end    = cls.__offset + string_length
            string = replay_data[cls.__offset : offset_end].decode("utf-8")
            
            cls.__offset = offset_end
            return string
        
        raise ReplayException(f'Invalid replay\noffset: {cls.__offset}\nData: {replay_data[cls.__offset]}')


    @classmethod
    def __decode(cls, binarystream):
        result, shift = 0, 0

        while True:
            byte = binarystream[cls.__offset]
            cls.__offset += 1
            
            result |= ((byte & 0b01111111) << shift)
            if (byte & 0b10000000) == 0x00: break
            
            shift += 7

        return result