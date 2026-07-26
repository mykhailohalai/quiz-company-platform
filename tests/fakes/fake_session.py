class FakeSession:
    def __init__(self):
        self.added = []

    def add(self, instance):
        self.added.append(instance)

    async def flush(self):
        pass

    async def refresh(self, instance):
        pass
