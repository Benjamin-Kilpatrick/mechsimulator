from serial.common.file_type import FileType


class Reader:

    @staticmethod
    def get_file_type(filename: str) -> FileType:
        if filename.endswith('.yaml'):
            return FileType.YAML
        if filename.endswith('.xlsl'):
            return FileType.EXCEL
        return FileType.INVALID
