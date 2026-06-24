from PIL import Image
import customtkinter as ctk

from config.paths import IMAGES_DIR

def load_icon(filename: str, size=(32, 32)):
    return ctk.CTkImage(
        light_image=Image.open(IMAGES_DIR / filename),
        size=size,
    )