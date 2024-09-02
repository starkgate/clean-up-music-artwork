import os
import shutil
from PIL import Image
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC


def is_music_file(filename):
    return filename.lower().endswith(('.flac', '.mp3'))


def has_embedded_artwork(file_path):
    if file_path.lower().endswith('.flac'):
        audio = FLAC(file_path)
        return len(audio.pictures) > 0
    elif file_path.lower().endswith('.mp3'):
        audio = MP3(file_path, ID3=ID3)
        return any(isinstance(tag, APIC) for tag in audio.tags.values())
    return False


def remove_embedded_artwork(file_path, dry_run=False):
    if file_path.lower().endswith('.flac'):
        audio = FLAC(file_path)
        if dry_run:
            print(f"Would remove embedded artwork from {file_path}")
        else:
            audio.clear_pictures()
            audio.save()
    elif file_path.lower().endswith('.mp3'):
        audio = MP3(file_path, ID3=ID3)
        if dry_run:
            print(f"Would remove embedded artwork from {file_path}")
        else:
            audio.tags.delall('APIC')
            audio.save()


def extract_embedded_artwork(file_path, output_path, dry_run=False):
    if file_path.lower().endswith('.flac'):
        audio = FLAC(file_path)
        for picture in audio.pictures:
            if dry_run:
                print(f"Would extract artwork from {file_path} to {output_path}")
            else:
                if not os.path.exists(output_path):
                    with open(output_path, 'wb') as img:
                        img.write(picture.data)
            break
    elif file_path.lower().endswith('.mp3'):
        audio = MP3(file_path, ID3=ID3)
        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                if dry_run:
                    print(f"Would extract artwork from {file_path} to {output_path}")
                else:
                    if not os.path.exists(output_path):
                        with open(output_path, 'wb') as img:
                            img.write(tag.data)
                break


def convert_png_to_jpg(png_path, jpg_path, dry_run=False):
    with Image.open(png_path) as img:
        if dry_run:
            print(f"Would convert {png_path} to {jpg_path} with quality 90%")
        else:
            img.convert('RGB').save(jpg_path, 'JPEG', quality=90)


def process_folder(folder_path, dry_run=False):
    cover_jpg_path = None
    folder_jpg_path = None
    cover_png_path = None
    music_files = []

    for entry in os.scandir(folder_path):
        if entry.is_file():
            lower_name = entry.name.lower()
            if lower_name == 'cover.jpg':
                cover_jpg_path = entry.path
            elif lower_name == 'folder.jpg':
                folder_jpg_path = entry.path
            elif lower_name == 'cover.png':
                cover_png_path = entry.path
            elif is_music_file(entry.name):
                music_files.append(entry.path)

    # 1. Handle cover.png
    if cover_png_path:
        if cover_jpg_path:
            with Image.open(cover_png_path) as img_png:
                png_size = img_png.size
            with Image.open(cover_jpg_path) as img_jpg:
                jpg_size = img_jpg.size
            if png_size > jpg_size:
                convert_png_to_jpg(cover_png_path, cover_jpg_path, dry_run=dry_run)
        else:
            jpg_path = os.path.join(folder_path, 'cover.jpg')
            convert_png_to_jpg(cover_png_path, jpg_path, dry_run=dry_run)

        if not dry_run:
            os.remove(cover_png_path)
        else:
            print(f"Would remove {cover_png_path}")

    # 2. Handle folder.jpg
    if folder_jpg_path:
        if cover_jpg_path:
            with Image.open(folder_jpg_path) as img_folder:
                folder_size = img_folder.size
            with Image.open(cover_jpg_path) as img_jpg:
                jpg_size = img_jpg.size
            if folder_size > jpg_size:
                if dry_run:
                    print(f"Would overwrite {cover_jpg_path} with {folder_jpg_path}")
                else:
                    shutil.move(folder_jpg_path, cover_jpg_path)
            else:
                if dry_run:
                    print(f"Would remove {folder_jpg_path}")
                else:
                    os.remove(folder_jpg_path)
        else:
            if dry_run:
                print(f"Would rename {folder_jpg_path} to cover.jpg")
            else:
                shutil.move(folder_jpg_path, os.path.join(folder_path, 'cover.jpg'))

    # 3. Handle cover.jpg and embedded artwork
    if cover_jpg_path:
        for music_file in music_files:
            remove_embedded_artwork(music_file, dry_run=dry_run)
    else:
        for music_file in music_files:
            if has_embedded_artwork(music_file):
                extract_embedded_artwork(music_file, os.path.join(folder_path, 'cover.jpg'), dry_run=dry_run)
                for mf in music_files:
                    remove_embedded_artwork(mf, dry_run=dry_run)
                break



def process_path(root_path, dry_run=False):
    for entry in os.scandir(root_path):
        if entry.is_dir():
            process_folder(entry.path, dry_run=dry_run)
            process_path(entry.path, dry_run=dry_run)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process music folders to manage cover images and embedded artwork.")
    parser.add_argument('path', type=str, help='Root path to start processing.')
    parser.add_argument('--dry-run', action='store_true', help='Show what changes would be made without applying them.')

    args = parser.parse_args()

    process_path(args.path, dry_run=args.dry_run)
