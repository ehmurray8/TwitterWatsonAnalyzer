class ContentItem:

    def __init__(self, content: str, created: int, id_str: str):
        self.content = content
        self.contenttype = "text/plain"
        self.created = created
        self.id = id_str
        self.language = "en"
