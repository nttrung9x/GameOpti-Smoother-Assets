from PIL import Image, ImageFilter
import os
import traceback


def convert_webp_to_png(
    input_dir: str,
    output_dir: str,
    error_file: str,
    size=(32, 32),
    colors=0,  # 0 = không quantize (đẹp nhất), 128/256 = giảm dung lượng
):
    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        if not (file.lower().endswith(".webp") or file.lower().endswith(".png")):
            continue

        webp_path = os.path.join(input_dir, file)
        png_path = os.path.join(output_dir, file.replace(".webp", ".png"))

        try:
            img = Image.open(webp_path).convert("RGBA")

            # 🔥 Tính tỉ lệ để fit vào size (có cả upscale + downscale)
            ratio = min(size[0] / img.width, size[1] / img.height)
            new_w = max(1, int(img.width * ratio))
            new_h = max(1, int(img.height * ratio))

            # 🔥 Resize
            if ratio > 1:
                # upscale → dùng BICUBIC + sharpen
                img = img.resize((new_w, new_h), Image.Resampling.BICUBIC)
                img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=0))
            else:
                # downscale → dùng LANCZOS + sharpen nhẹ
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=0))

            # 🔥 Tạo canvas đúng size (padding)
            new_img = Image.new("RGBA", size, (0, 0, 0, 0))
            x = (size[0] - new_w) // 2
            y = (size[1] - new_h) // 2
            new_img.paste(img, (x, y), img)

            # 🔥 Quantize (optional)
            if colors and colors > 0:
                try:
                    new_img = new_img.quantize(
                        colors=colors,
                        method=Image.Quantize.FASTOCTREE,
                        dither=Image.Dither.FLOYDSTEINBERG
                    ).convert("RGBA")
                except Exception as e:
                    print(f"[QUANTIZE ERROR] {file} -> {e}")

            # 🔥 Save PNG tối ưu
            new_img.save(png_path, "PNG", optimize=True, compress_level=9)

            print(f"[OK] {file} -> {size[0]}x{size[1]}")

        except Exception as e:
            print(f"[ERROR] File: {file} -> {e}")
            traceback.print_exc()

            if error_file:
                with open(error_file, "a", encoding="utf-8") as f:
                    f.write(f"{file} -> {e}\n")


if __name__ == "__main__":
    # 🔥 chỉnh size tại đây
    SIZE = (32, 32)

    convert_webp_to_png("poe1_webp", "poe1", "error_log.txt", size=SIZE, colors=128)
    convert_webp_to_png("poe2_webp", "poe2", "error_log.txt", size=SIZE, colors=128)