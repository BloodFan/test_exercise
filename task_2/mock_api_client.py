class MockAPIClient:
    def __init__(self, base_url: str = None):
        self._first_request = True
        self.base_url = base_url
        self.session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def request(self, method, url, params):
        letter = params.get("cmstartsortkeyprefix", "")

        if letter == "Б":
            if self._first_request:
                self._first_request = False
                return {
                    "query": {
                        "categorymembers": [
                            {"title": "Барсук", "pageid": 1},
                            {"title": "Бегемот", "pageid": 2},
                        ]
                    },
                    "continue": {"cmcontinue": "next_batch"},
                }
            else:
                return {
                    "query": {
                        "categorymembers": [
                            {"title": "Буйвол", "pageid": 5},
                        ]
                    }
                }

        elif letter == "Е":
            return {
                "query": {
                    "categorymembers": [
                        {"title": "Ёж", "pageid": 3},
                    ]
                }
            }

        elif letter == "#":
            return {
                "query": {
                    "categorymembers": [
                        {"title": "Łoś", "pageid": 4},
                    ]
                }
            }

        return {"query": {"categorymembers": []}}
