
class MetaData:
    """
    Metadata for an experiment file
    """
    def __init__(self,
                 version: str,
                 source: str,
                 description: str):
        """
        Constructor
        :param version: version number of the experiment file
        :param source: information on where the data was sourced
        :param description: a description of the experiment file
        """
        self.version: str = version
        self.source: str = source
        self.description: str = description

    def __repr__(self):
        return f"<MetaData version:{self.version} source:{self.source} description:{self.description}>"

