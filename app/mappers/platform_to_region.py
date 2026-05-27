from app.enums import Platform, Region


class RegionMapper:
    _platform_to_region = {
        Platform.EUW1: Region.EUROPE,
        Platform.EUN1: Region.EUROPE,
        Platform.RU: Region.EUROPE,
        Platform.TR1: Region.EUROPE,
        Platform.ME1: Region.EUROPE,

        Platform.NA1: Region.AMERICAS,
        Platform.BR1: Region.AMERICAS,
        Platform.LA1: Region.AMERICAS,
        Platform.LA2: Region.AMERICAS,

        Platform.KR: Region.ASIA,
        Platform.JP1: Region.ASIA,

        Platform.OC1: Region.SEA,
        Platform.SG2: Region.SEA,
        Platform.TW2: Region.SEA,
        Platform.VN2: Region.SEA,
    }

    @classmethod
    def from_platform(cls, platform: Platform) -> Region:
        return cls._platform_to_region[platform]