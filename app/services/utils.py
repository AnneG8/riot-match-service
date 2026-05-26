from app.constants import PLATFORM_TO_REGION


def get_region_by_platform(platform: str) -> str:
    try:
        return PLATFORM_TO_REGION[platform]
    except KeyError as err:
        raise ValueError(
            f'Unsupported Riot platform: {platform}',
        ) from err