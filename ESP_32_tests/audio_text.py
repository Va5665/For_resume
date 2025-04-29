import whisper
import os

# Загружаем модель (можно заменить на 'medium' или 'large' для лучшего качества)
model = whisper.load_model("base")

# Путь к аудиофайлу
# audio_path = "C:\\Users\\Asus\\Downloads\\audioA.ogg"
audio_path ="C:\\Users\\Asus\\Downloads\\audio_2.ogg"
# Получаем имя файла без расширения
base_name = os.path.splitext(os.path.basename(audio_path))[0]

# Создаём путь к папке txt в том же каталоге
txt_dir = os.path.join(os.path.dirname(audio_path), "txt")
os.makedirs(txt_dir, exist_ok=True)

# Полный путь к файлу для сохранения текста
txt_file_path = os.path.join(txt_dir, f"{base_name}.txt")

# Распознаём речь
print("Распознаю речь, подожди немного...")
result = model.transcribe(audio_path, language="ru")

# Сохраняем текст в файл
with open(txt_file_path, "w", encoding="utf-8") as f:
    f.write(result["text"])

# Выводим текст
print("\n--- Распознанный текст ---\n")
print(result["text"])
print(f"\nРезультат сохранён в: {txt_file_path}")
