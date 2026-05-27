class PlayerNotFoundError(Exception):
    def __init__(self, puuid: str) -> None:
        super().__init__(f'Player {puuid} not found')
        self.puuid = puuid
