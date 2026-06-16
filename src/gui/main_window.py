import customtkinter as ctk
from tkinter import filedialog, ttk, messagebox
import tkinter as tk
import os
from PIL import Image
from resources.texts.text import TEXT

class CTkToolTip:
    """マウスオーバー時にツールチップを表示するクラス"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffff", relief='solid', borderwidth=1,
                         font=("Segoe UI", "9", "normal"), padx=5, pady=2)
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        # 外観をライトモードに設定
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("File Organizer GUI")
        self.geometry("900x650")
        self.controller = None

        # レイアウト設定
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Frame配置
        self.cmd_area = ctk.CTkFrame(self, corner_radius=0)
        self.path_bar = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.preview = ctk.CTkFrame(self, corner_radius=0)
        self.footer = ctk.CTkFrame(self, height=30, corner_radius=0)

        self.cmd_area.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.path_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.preview.grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.footer.grid(row=4, column=0, columnspan=2, sticky="ew")

        self._setup_widgets()

    def set_controller(self, controller):
        self.controller = controller

    def _setup_widgets(self):
        # Dir Bar
        # 画像の読み込みパス設定
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        img_dir = os.path.join(base_path, "resources", "images")

        # アイコンの読み込み (ライト/ダーク両対応の設定も可能ですが、今回はライト固定)
        icon_size = (32, 32)
        self.icon_folder = ctk.CTkImage(light_image=Image.open(os.path.join(img_dir, "dir_select.png")), size=icon_size)
        self.icon_run = ctk.CTkImage(light_image=Image.open(os.path.join(img_dir, "move.png")), size=icon_size)
        self.icon_undo = ctk.CTkImage(light_image=Image.open(os.path.join(img_dir, "undo.png")), size=icon_size)

        # ボタンの共通設定: 青白く光るホバーカラー (#D0E0FF)
        hover_cfg = {"hover_color": "#D0E0FF", "fg_color": "transparent", "text": "", "width": 40, "height": 40}

        self.btn_browse = ctk.CTkButton(self.cmd_area, image=self.icon_folder, 
                                        command=lambda: self.controller.select_source_directory(), **hover_cfg)
        self.btn_browse.pack(side="left", padx=2, pady=5)
        CTkToolTip(self.btn_browse, "フォルダの選択")

        self.btn_run = ctk.CTkButton(self.cmd_area, image=self.icon_run, 
                                     command=lambda: self.controller.execute_move(), **hover_cfg)
        self.btn_run.configure(hover_color="#C0FFC0") # 実行は緑色に
        self.btn_run.pack(side="left", padx=2, pady=5)
        CTkToolTip(self.btn_run, "移動を実行")

        self.btn_undo = ctk.CTkButton(self.cmd_area, image=self.icon_undo, 
                                      command=lambda: self.controller.undo(), **hover_cfg)
        self.btn_undo.pack(side="left", padx=2, pady=5)
        CTkToolTip(self.btn_undo, "元に戻す")

        # パス表示用ラベルの追加
        self.path_label = ctk.CTkLabel(self.path_bar, text="Folder: -", font=ctk.CTkFont(size=12, slant="italic"))
        self.path_label.pack(side="left", padx=15, pady=2)

        # Settings
        # Preview (Treeview)
        self._setup_treeview()

    def _setup_treeview(self):
        # Treeviewのスタイル設定
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="white", 
                        foreground="black", 
                        rowheight=25, 
                        fieldbackground="white",
                        borderid=0)
        style.map("Treeview", background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", font=(None, 10, "bold"))

        # Treeview配置用のフレーム
        self.tree_container = ctk.CTkFrame(self.preview, fg_color="white")
        self.tree_container.pack(expand=True, fill="both", padx=10, pady=10)

        self.tree = ttk.Treeview(self.tree_container, columns=("name", "dest"), show="headings", selectmode="browse")
        self.tree.heading("name", text=TEXT["gui"]["col_name"], anchor="w")
        self.tree.heading("dest", text=TEXT["gui"]["col_dest"], anchor="w")
        self.tree.column("name", width=300, minwidth=100)
        self.tree.column("dest", width=300, minwidth=100)
        
        self.tree.pack(side="left", expand=True, fill="both")
        self.tree.tag_configure("oddrow", background="#F9F9F9")
        self.tree.tag_configure("evenrow", background="white")

        # スクロールバー
        self.scrollbar = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        # Footer
        self.status_label = ctk.CTkLabel(self.footer, text="Status: Ready")
        self.status_label.pack(side="left", padx=20)

    # --- View API (ControllerがUIを操作するための公開メソッド) ---
    def update_preview_table(self, planned_moves):
        self.clear_log()

        # 新しい項目を追加
        for i, move in enumerate(planned_moves):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(move["src"].name, move["dst"].parent.name), tags=(tag,))

    def clear_log(self):
        self.tree.delete(*self.tree.get_children())

    def update_path_label(self, path):
        self.path_label.configure(text=f"Folder: {path}")

    def update_status(self, text):
        self.status_label.configure(text=text)

    def ask_yes_no(self, title, message):
        return messagebox.askyesno(title, message)

    def ask_directory(self):
        return filedialog.askdirectory()