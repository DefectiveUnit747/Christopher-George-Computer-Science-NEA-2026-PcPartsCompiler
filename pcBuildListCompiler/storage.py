class Storage:
    gameData = {}
    buildPreferences = {}

    @classmethod
    def resetValues(cls):
        cls.gameData.clear()
        cls.buildPreferences.clear()

