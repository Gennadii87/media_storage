import os
import shutil
from urllib.parse import urljoin

from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from .serializers import ImageLibrarySerializer, DeleteFileSerializer

from PIL import Image
import xml.etree.ElementTree as et


@csrf_exempt
def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({'csrf_token': token})


@extend_schema(tags=["Media Storage"])
class FileUploadViewSet(viewsets.ViewSet):
    serializer_class = ImageLibrarySerializer
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="Все файлы и каталоги в папке media.",
        description="Возвращает иерархическую структуру JSON всех файлов и каталогов в корневом каталоге носителя.",
        responses={
            200: OpenApiResponse(description='Иерархическое дерево файлов в папке media'),
        }
    )
    @csrf_exempt
    def list(self, request):
        def get_tree(path):
            result = {
                "folder": os.path.basename(path),
                "content": []
            }
            try:
                for entry in os.listdir(path):
                    full_path = os.path.join(path, entry)
                    if os.path.isdir(full_path):
                        result["content"].append(get_tree(full_path))
                    else:
                        result["content"].append({
                            "file": entry
                        })
            except PermissionError:
                return {"folder": os.path.basename(path), "content": []}
            return result

        media_root = settings.MEDIA_ROOT
        file_tree = get_tree(media_root)
        return Response(file_tree, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Сохранить файл.",
        description="Необходимо указать папку и загрузить файл",
    )
    @csrf_exempt
    def create(self, request):
        path = request.data.get('path', 'Default')

        if not path:
            return Response({'error': 'Path parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not path.endswith('/'):
            path += '/'

        media_root = settings.MEDIA_ROOT
        full_path = os.path.join(media_root, path)

        if not os.path.exists(full_path):
            os.makedirs(full_path)

        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            if not self._is_valid_image(uploaded_file):
                return Response({'error': 'Invalid image file'}, status=status.HTTP_400_BAD_REQUEST)

            file_path = os.path.join(full_path, uploaded_file.name)

            with default_storage.open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            server_url = settings.SERVER_URL
            url = urljoin(server_url, f"{settings.MEDIA_URL}{path}{uploaded_file}")
            return Response({'file': url}, status=status.HTTP_201_CREATED)

        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def _is_valid_image(file):
        try:
            tree = et.parse(file)
            root = tree.getroot()
            if root.tag.lower() == "{http://www.w3.org/2000/svg}svg":
                return True
        except Exception as svg_error:
            print(f"Error parsing SVG file: {svg_error}")

        try:
            image = Image.open(file)
            valid_formats = ["JPEG", "PNG"]
            if image.format.upper() in valid_formats:
                return True
            else:
                print(f"Invalid image format: {image.format.upper()}")
        except Exception as image_error:
            print(f"Error opening image: {image_error}")

        return False


@extend_schema(tags=["Media Storage"])
class FileDeleteViewSet(viewsets.ViewSet):
    serializer_class = DeleteFileSerializer

    @extend_schema(
        examples=[
            OpenApiExample(
                name=f"request example",
                value=serializer_class({"path": "folder", "filename": "image.jpg"}).data,
                request_only=True,
            )
        ],
        summary="Удалить.",
        description="Необходимо указать папку где храниться файл и название файла с расширением",
        responses={
            204: OpenApiResponse(description='File deleted successfully'),
            400: OpenApiResponse(description='Invalid request data'),
            404: OpenApiResponse(description='File not found')
        }
    )
    @csrf_exempt
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        path = serializer.validated_data['path']
        filename = serializer.validated_data['filename']

        if not path.endswith('/'):
            path += '/'

        file_path = os.path.join(settings.MEDIA_ROOT, path, filename)

        if not os.path.exists(file_path):
            return Response({'detail': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

        default_storage.delete(file_path)
        return Response({'message': 'File deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Media Storage"])
class FileDeleteAllViewSet(viewsets.ViewSet):

    @extend_schema(
        summary="Удаление всей папки media.",
        description="Удаляет всю папку media и все её содержимое.",
        responses={
            204: OpenApiResponse(description='Directory deleted successfully'),
            500: OpenApiResponse(description='Internal Server Error')
        }
    )
    @csrf_exempt
    @action(methods=['delete'], detail=False)
    def delete_all(self, request):
        media_root = settings.MEDIA_ROOT

        try:
            # Удаление директории и всего её содержимого
            shutil.rmtree(media_root)
            return Response({'message': 'Directory deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            # Возврат ошибки, если что-то пошло не так
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
