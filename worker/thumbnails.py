from io import BytesIO
from pathlib import Path

from PIL import Image

SIZES = {"small": (128, 128), "medium": (256, 256), "large": (512, 512)}


def make_thumbnails(image_bytes: bytes, output_dir: Path) -> list[str]:

    if not output_dir.exists():
        raise FileNotFoundError(f"output dir does not exist: {output_dir}")

    img = Image.open(BytesIO(image_bytes))

    result_paths = []

    for size_name, (x, y) in SIZES.items():
        tmp_img = img.copy()
        tmp_img.thumbnail((x, y))
        tmp_img = tmp_img.convert("RGB")

        tmp_path = output_dir / f"{size_name}.jpg"
        tmp_img.save(tmp_path, "JPEG")

        result_paths.append(tmp_path)

    return [str(path) for path in result_paths]
