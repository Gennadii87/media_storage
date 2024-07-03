from rest_framework.serializers import (
    Serializer,
    SerializerMetaclass,
    FileField,
    CharField
)


class ImageLibrarySerializer(Serializer, metaclass=SerializerMetaclass):
    path = CharField(help_text="путь", required=True, write_only=True)
    file = FileField(help_text="Изображение", required=True)


class DeleteFileSerializer(Serializer, metaclass=SerializerMetaclass):
    path = CharField(required=True)
    filename = CharField(required=True)