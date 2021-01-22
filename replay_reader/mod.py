
class Mod():

    NoMod          = 0
    NoFail         = 1
    Easy           = 2
    NoVideo        = 4
    Hidden         = 8
    HardRock       = 16
    SuddenDeath    = 32
    DoubleTime     = 64
    Relax          = 128
    HalfTime       = 256
    Nightcore      = 512
    Flashlight     = 1024
    Autoplay       = 2048
    SpunOut        = 4096
    Autopilot      = 8192
    Perfect        = 16384
    Key4           = 32768
    Key5           = 65536
    Key6           = 131072
    Key7           = 262144
    Key8           = 524288
    keyMod         = 1015808
    FadeIn         = 1048576
    Random         = 2097152
    LastMod        = 4194304
    TargetPractice = 8388608
    Key9           = 16777216
    Coop           = 33554432
    Key1           = 67108864
    Key3           = 134217728
    Key2           = 268435456
    ScoreV2        = 536870912
    Mirror         = 1073741824

    data = {
        NoMod          : 'NM',  # NoMod         
        NoFail         : 'NF',  # NoFail        
        Easy           : 'EZ',  # Easy          
        NoVideo        : 'NV',  # NoVideo       
        Hidden         : 'HD',  # Hidden        
        HardRock       : 'HR',  # HardRock      
        SuddenDeath    : 'SD',  # SuddenDeath   
        DoubleTime     : 'DT',  # DoubleTime    
        Relax          : 'RX',  # Relax         
        HalfTime       : 'HT',  # HalfTime      
        Nightcore      : 'NC',  # Nightcore     
        Flashlight     : 'FL',  # Flashlight    
        Autoplay       : 'AU',  # Autoplay      
        SpunOut        : 'SP',  # SpunOut       
        Autopilot      : 'AP',  # Autopilot     
        Perfect        : 'PF',  # Perfect       
        Key4           : 'K4',  # Key4          
        Key5           : 'K5',  # Key5          
        Key6           : 'K6',  # Key6          
        Key7           : 'K7',  # Key7          
        Key8           : 'K8',  # Key8          
        keyMod         : 'KM',  # keyMod        
        FadeIn         : 'FI',  # FadeIn        
        Random         : 'RD',  # Random        
        LastMod        : 'LM',  # LastMod       
        TargetPractice : 'TP',  # TargetPractice
        Key9           : 'K9',  # Key9          
        Coop           : 'CP',  # Coop          
        Key1           : 'K1',  # Key1          
        Key3           : 'K3',  # Key3          
        Key2           : 'K2',  # Key2          
        ScoreV2        : 'S2',  # ScoreV2       
        Mirror         : 'MR',  # Mirror
    }

    def __init__(self, value):
        if self.__is_valid(value):
            self.value = value
            return
        
        raise ValueError(f'Invalid mod   value = {value}')


    def __repr__(self):
        return ' '.join(self.get_mods_txt())


    def has_mod(self, mod):
        if not mod in Mod.data:
            raise ValueError(f'Invalid mod   value = {value}')

        if mod == Mod.NoMod:
            return self.value == 0
            
        return self.value & mod > 0


    def add_mod(self, mod):
        if not mod in Mod.data:
            raise ValueError(f'Invalid mod   value = {value}')

        self.value |= mod


    def rmv_mod(self, mod):
        if not mod in Mod.data:
            raise ValueError(f'Invalid mod   value = {value}')

        self.value &= ~mod


    def get_mods_txt(self):
        if self.value == 0:
            return [ ]

        mods_txt = []
        for mod, txt in Mod.data.items():
            if self.value & mod > 0:
                mods_txt.append(txt)

        return mods_txt


    def __is_valid(self, value):
        for mod in Mod.data.keys():
            value &= ~mod
            
        return (value == 0)