from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class PrivateDocumentStorage(FileSystemStorage):
    def __init__(self) -> None:
        super().__init__(location=None, base_url=None)

    @property
    def location(self) -> str:
        return str(settings.PRIVATE_DOCUMENT_ROOT)

    def url(self, name: str) -> str:
        raise ValueError("Private document files do not have public URLs.")
