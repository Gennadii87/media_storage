# media_storage
Сервис хранения изображений <br/>

*Функционал*
<pre>
    - хранение файлов jpg, svg, png
    - автоматическое сжатие для экономии места
    - создание директорий для хранения файлов
    - удаления директорий и файлов
    - мгновенная очистка всей директории
</pre>

Запуск сервиса:
    
    python manage.py runserver

## Пример файла ".env"

```bash
# This is the project ↓

SECRET_KEY = ''
DEBUG = 0
ALLOWED_HOSTS = ''


# This is the components ↓
SERVER_URL = ''
