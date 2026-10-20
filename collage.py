import os
import re
from windialog import getdir
from PIL import Image, ImageDraw, ImageFont

FONT_SCALE = 6
FRAME_WIDTH = 10
NUM_COLUMN = 3
NUM_STROKE = 2

def parse_names(text):
    text = text.strip()
    if not text:
        return []

    num_pattern = r'\d+\s*[\)\.\-:]\s*'

    if re.search(num_pattern, text):
        normalized = re.sub(r'\s*(?=' + num_pattern + r')', '\n', text).strip()
        lines = [l.strip() for l in normalized.splitlines() if l.strip()]
        result = []

        for line in lines:
            m = re.match(r'^' + num_pattern + r'(.+)$', line)
            result.append(m.group(1).strip() if m else line.strip())
            
        return result


    lines = [l.strip() for l in text.splitlines() if l.strip()]
    result = lines

    if len(result) == 1 and re.search(r'[,;]', result[0]):
        result = [p.strip() for p in re.split(r'[,;]', result[0]) if p.strip()]

    return result


def natural_key(name):
    return [int(p) if p.isdigit() else p.lower()
            for p in re.split(r'(\d+)', name)]


def get_image_files(folder):
    exts = ('.png', '.jpg', '.jpeg', '.bmp')
    return sorted(
        (f for f in os.listdir(folder)
        if f.lower().endswith(exts) and os.path.isfile(os.path.join(folder, f))),
        key = natural_key
    )


def add_number_and_frame(num, img):
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    font_size = int(height / FONT_SCALE)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    text = str(num)
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    
    padding = 10
    x = width - text_width - padding
    y = padding
    
    draw.text((x, y), text, font=font, fill="white")
    draw.rectangle(xy=(0, 0, width, height), outline="red", width=FRAME_WIDTH)

    return img


def creating_collage(folder):
    canvas_width = 1620
    canvas_height = 1620
    filled_width, filled_height = 0, 0
    collage_count = 1
    max_height = 0

    new_folder = os.path.join(folder, "Коллаж")
    os.makedirs(new_folder, exist_ok=True)

    print("Введите 1, чтобы указать размеры коллажа(ей) и фоток в коллаже\nВведите любую другую цифру, чтобы использовать заводские настройки")
    choice = int(input())
    if choice == 1:
        canvas_width = int(input("Введите ширину коллажа: "))
        canvas_height = int(input("Введите длину коллажа: "))
        photo_width = int(input("Введите ширину картинки: "))
        photo_height = int(input("Введите длину картинки: "))

    collage = Image.new("RGB", (canvas_width, canvas_height), color=(255, 255, 255))
    pw = canvas_width / NUM_COLUMN
    ph = canvas_height / NUM_STROKE

    for index, file in enumerate(get_image_files(folder), 1):
        file_path = os.path.join(folder, file)
        img = Image.open(file_path)

        if choice != 1:
            photo_width, photo_height = img.size
            k_w = pw / photo_width
            k_h = ph / photo_height
            k = min(k_w, k_h)
            photo_width = round(photo_width * k)
            photo_height = round(photo_height * k)

        resized = img.resize((photo_width, photo_height))
        numbered = add_number_and_frame(index, resized)
        max_height = max(max_height, numbered.height)

        if filled_width + numbered.width > canvas_width:
            filled_width = 0
            filled_height += max_height
            max_height = numbered.height

            if filled_height + numbered.height > canvas_height:
                filename = f"collage_file{collage_count}.jpg"
                output_path = os.path.join(new_folder, filename)
                collage.save(output_path)
                collage_count += 1
                collage = Image.new("RGB", (canvas_width, canvas_height), color=(255, 255, 255))
                filled_width = 0
                filled_height = 0
                max_height = numbered.height

        collage.paste(numbered, (filled_width, filled_height))
        filled_width += numbered.width

    filename = f"collage_file{collage_count}.jpg"
    output_path = os.path.join(new_folder, filename)
    collage.save(output_path)


def print_names(folder):
    print("Зайдите в папку \"Коллаж\", возьмите картинку(и) и отправьте её в неросеть с этим текстом: \n")
    print("Классифицируй картинки (только номер и название)\n")
    print("Введите полученный текст: ")

    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)

    text = '\n'.join(lines)
    names_list = parse_names(text)

    if not names_list:
        names_list = [p.strip() for p in re.split(r'[,;]', text) if p.strip()]

    renamed = 0
    skipped = 0

    for index, file in enumerate(get_image_files(folder)):
        if index >= len(names_list):
            continue
        ext = os.path.splitext(file)[1]
        new_name = f"{names_list[index]}{ext}"

        src = os.path.join(folder, file)
        dst = os.path.join(folder, new_name)

        if os.path.abspath(src) == os.path.abspath(dst):
            skipped += 1
            continue

        if os.path.exists(dst):
            print(f"Пропуск: '{new_name}' уже существует.")
            skipped += 1
            continue

        os.rename(src, dst)
        renamed += 1

    print(f"Переименовано: {renamed}, пропущено: {skipped}")
    input()


def main():
    folder = getdir(title="Выберите папку", multi=False)

    if not folder:
        print("Папка не выбрана.")
        return

    folder = folder[0]

    creating_collage(folder)
    print_names(folder)

if __name__ == "__main__":
    main()