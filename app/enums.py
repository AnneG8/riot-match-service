from enum import IntEnum, StrEnum


class Platform(StrEnum):
    EUW1 = 'euw1'
    EUN1 = 'eun1'
    RU = 'ru'
    TR1 = 'tr1'
    ME1 = 'me1'

    NA1 = 'na1'
    BR1 = 'br1'
    LA1 = 'la1'
    LA2 = 'la2'

    KR = 'kr'
    JP1 = 'jp1'

    OC1 = 'oc1'
    SG2 = 'sg2'
    TW2 = 'tw2'
    VN2 = 'vn2'


class Region(StrEnum):
    EUROPE = 'europe'
    AMERICAS = 'americas'
    ASIA = 'asia'
    SEA = 'sea'


class QueueId(IntEnum):
    DRAFT_PICK = 400
    SOLOQ = 420
    BLIND_PICK = 430
    FLEX = 440
    ARAM = 450
    CLASH = 700
    ARENA = 1700


class RankedQueueType(StrEnum):
    RANKED_SOLO_5X5 = 'RANKED_SOLO_5X5'
    RANKED_FLEX_SR = 'RANKED_FLEX_SR'
    NORMAL_DRAFT_5x5 = 'NORMAL_DRAFT_5x5'
    NORMAL_BLIND_V5 = 'NORMAL_BLIND_V5'

