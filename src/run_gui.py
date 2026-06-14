import customtkinter as ctk
from config.config_loader import load_config, create_config_file
from config.errors import ConfigError

app = ctk.CTk()

# Windowの基本設定
app.title("File Organizer")
app.geometry("800x600")

app.grid_rowconfigure(2, weight=1)
app.grid_columnconfigure(1, weight=1)

# Frame配置
header   = ctk.CTkFrame(app)
dir_bar  = ctk.CTkFrame(app)
settings = ctk.CTkFrame(app)
preview  = ctk.CTkFrame(app)
footer   = ctk.CTkFrame(app, height=50)
footer.grid_propagate(False)

header.grid(row=0, column=0, columnspan=2, sticky="ew")
dir_bar.grid(row=1, column=0, sticky="ew")
settings.grid(row=2, column=0, sticky="ns")
preview.grid(row=2, column=1, sticky="nsew")
footer.grid(row=3, column=0, columnspan=2, sticky="ew")

def startup():
    try:
        config = load_config()
        return config

    except ConfigError as e:
        if e.key == "no_config_file":
            create_config_file()
            config = load_config()
            return config

if __name__ == "__main__":
    startup()
    app.mainloop()