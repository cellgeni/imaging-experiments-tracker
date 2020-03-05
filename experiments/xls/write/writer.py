import uuid

from django.core.files import File


class FileWriter:

    @staticmethod
    def write_file(f: File, filename: str) -> None:
        with open(filename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)


class ExcelFileWriter:

    @staticmethod
    def write_tmp_file(f: File) -> str:
        filename = str(uuid.uuid4()) + ".xlsx"
        FileWriter.write_file(f, filename)
        return filename

    @classmethod
    def dump_file_on_disk(cls, f: File, filename: str = None) -> str:
        if filename:
            FileWriter.write_file(f, filename)
        else:
            return cls.write_tmp_file(f)
