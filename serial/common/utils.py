from serial.common.file_type import FileType


class Utils:
    @staticmethod
    def get_file_type(filename: str) -> FileType:
        if filename.endswith('.yaml'):
            return FileType.YAML
        if filename.endswith('.xlsx'):
            return FileType.EXCEL
        return FileType.INVALID
