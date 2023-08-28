import re
import shutil
import sys
from pathlib import Path

UKRAINIAN_SYMBOLS = "абвгдеєжзиіїйклмнопрстуфхцчшщьюя"
TRANSLATION = (
    "a", "b", "v", "g", "d", "e", "je", "zh", "z", "y", "i",
    "ji", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "ju", "ja",
)


TRANS = {}

images = list()
documents = list()
audio = list()
video = list()
archives = list()
folders = list()
others = list()
unknown = set()
extensions = set()

registered_extensions = {
    "JPEG": images, "PNG": images, "JPG": images, "SVG": images,
    "AVI": video, "MP4": video, "MOV": video, "MKV": video,
    "TXT": documents, "DOC": documents, "DOCX": documents, "PDF": documents, "XLSX": documents, "PPTX": documents,
    "ZIP": archives, "GZ": archives, "TAR": archives,
    "MP3": audio, "OGG": audio, "WAV": audio, "AMR": audio
}

for key, value in zip(UKRAINIAN_SYMBOLS, TRANSLATION):
    TRANS[ord(key)] = value
    TRANS[ord(key.upper())] = value.upper()


def normalize(name):
    name, *extension = name.split(".")
    new_name = name.translate(TRANS)
    new_name = re.sub(r"\W", "_", new_name)
    return f"{new_name}.{'.'.join(extension)}"


def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()


def scan(folder):
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ("images", "documents", "audio", "video", "archives"):
                folders.append(item)
                scan(item)
            continue

        extension = get_extensions(file_name=item.name)
        new_name = folder/item.name
        if not extension:
            others.append(new_name)
        else:
            try:
                container = registered_extensions[extension]
                extensions.add(extension)
                container.append(new_name)
            except KeyError:
                unknown.add(extension)
                others.append(new_name)


def handle_file(path, root_folder, destination):
    target_folder = root_folder / destination
    target_folder.mkdir(exist_ok=True)
    path.replace(target_folder / normalize(path.name))


def handle_archive(path, root_folder, destination):
    target_folder = root_folder / destination
    target_folder.mkdir(exist_ok=True)

    new_name = normalize(path.stem)

    archive_folder = root_folder / destination / new_name
    archive_folder.mkdir(exist_ok=True)

    try:
        shutil.unpack_archive(str(path), str(archive_folder))
        path.unlink()
    except (shutil.ReadError, FileNotFoundError):
        archive_folder.rmdir()
        return


def remove_empty_folders(path):
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            try:
                item.rmdir()
            except OSError:
                pass


def get_folder_objects(root_path):
    for folder in root_path.iterdir():
        if folder.is_dir():
            remove_empty_folders(folder)
            try:
                folder.rmdir()
            except OSError:
                pass


def main():
    path = sys.argv[1]
    print(f"Start in {path}")
    folder_path = Path(path)

    scan(folder_path)


    for file in images:
        handle_file(file, folder_path, "images")

    for file in documents:
        handle_file(file, folder_path, "documents")

    for file in audio:
        handle_file(file, folder_path, "audio")

    for file in video:
        handle_file(file, folder_path, "video")

    for file in archives:
        handle_archive(file, folder_path, "archives")

    get_folder_objects(folder_path)