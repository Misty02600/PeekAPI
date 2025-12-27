import io
import mss
from PIL import Image, ImageFilter

def screenshot(radius, main_screen_only):
    with mss.mss() as sct:
        if main_screen_only:
            monitor = sct.monitors[1]
        else:
            monitor = sct.monitors[0]

        img = sct.grab(monitor)

    img_pil = Image.frombytes("RGB", img.size, img.rgb)

    if radius > 0:
        img_pil = img_pil.filter(ImageFilter.GaussianBlur(radius=radius))

    img_byte = io.BytesIO()
    img_pil.save(img_byte, format="JPEG", quality=95)
    return img_byte.getvalue()

if __name__ == "__main__":
    all_screens_data = screenshot(radius=3, main_screen_only=False)
    with open("screenshot_all.jpg", "wb") as f:
        f.write(all_screens_data)
    print("已保存: screenshot_all.jpg")

    main_screen_data = screenshot(radius=3, main_screen_only=True)
    with open("screenshot_main.jpg", "wb") as f:
        f.write(main_screen_data)
    print("已保存: screenshot_main.jpg")
