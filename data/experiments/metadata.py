
class MetaData:
    def __init__(self,
                 version: str,
                 source: str,
                 description: str):
        self.version: str = version
        self.source: str = source
        self.description: str = description

    def __repr__(self):
        return f"<MetaData version:{self.version} source:{self.source} description:{self.description}>"

