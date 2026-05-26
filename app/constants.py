from enum import IntEnum, StrEnum

PLATFORM_TO_REGION = {
    'euw1': 'europe',
    'eun1': 'europe',
    'ru': 'europe',
    'tr1': 'europe',
    'me1': 'europe',

    'na1': 'americas',
    'br1': 'americas',
    'la1': 'americas',
    'la2': 'americas',

    'kr': 'asia',
    'jp1': 'asia',

    'oc1': 'sea',
    'ph2': 'sea',
    'sg2': 'sea',
    'th2': 'sea',
    'tw2': 'sea',
    'vn2': 'sea',
}


class RankedQueueType(StrEnum):
    RANKED_SOLO_5X5 = 'RANKED_SOLO_5X5'
    RANKED_FLEX_SR = 'RANKED_FLEX_SR'
    NORMAL_DRAFT_5x5 = 'NORMAL_DRAFT_5x5'
    NORMAL_BLIND_V5 = 'NORMAL_BLIND_V5'


class QueueId(IntEnum):
    DRAFT_PICK = 400
    SOLOQ = 420
    BLIND_PICK = 430
    FLEX = 440
    ARAM = 450
    CLASH = 700
    ARENA = 1700
