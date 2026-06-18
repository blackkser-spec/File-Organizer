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
        self.current_planned_moves = []

        # レイアウト設定
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Frame配置
        self.toolbar = ctk.CTkFrame(self, corner_radius=0)
        self.path_bar = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.preview_area = ctk.CTkFrame(self, corner_radius=0)
        self.footer = ctk.CTkFrame(self, height=30, corner_radius=0)

        self.toolbar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.path_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.sidebar.grid(row=3, column=0, sticky="nsew")
        self.preview_area.grid(row=3, column=1, sticky="nsew")
        self.footer.grid(row=4, column=0, columnspan=2, sticky="ew")

        self._setup_widgets()

    def set_controller(self, controller):
        self.controller = controller

    def _setup_widgets(self):
        # Dir Bar
        # 画像の読み込みパス設定
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        img_dir = os.path.join(base_path, "resources", "images")

        # アイコンの読み込み
        icon_size = (32, 32)
        self.icon_folder = ctk.CTkImage(light_image=Image.open(os.path.join(img_dir, "dir_select.png")), size=icon_size)
        self.icon_run = ctk.CTkImage(light_image=Image.open(os.path.join(img_dir, "move.png")), size=icon_size)
        self.icon_undo = ctk.CTkImage(light_image=Image.open(os.path.join(img_dir, "undo.png")), size=icon_size)
        self.icon_refresh = ctk.CTkImage(light_image=Image.open(os.path.join(img_dir, "refresh.png")), size=icon_size)
        self.icon_config = ctk.CTkImage(light_image=Image.open(os.path.join(img_dir, "option.png")), size=icon_size)

        # ボタンの共通スタイル設定
        button_style = {"hover_color": "#D0E0FF", "fg_color": "transparent", "text": "", "width": 40, "height": 40}

        self.btn_browse = ctk.CTkButton(self.toolbar, image=self.icon_folder, 
                                        command=lambda: self.controller.select_source_directory(), **button_style)
        self.btn_browse.pack(side="left", padx=2, pady=5)
        CTkToolTip(self.btn_browse, TEXT["gui"]["tooltip_browse_dir"])

        self.btn_move = ctk.CTkButton(self.toolbar, image=self.icon_run, 
                                     command=lambda: self.controller.execute_move(), **button_style)
        self.btn_move.configure(hover_color="#C0FFC0") # 実行は緑色に
        self.btn_move.pack(side="left", padx=2, pady=5)
        CTkToolTip(self.btn_move, TEXT["gui"]["tooltip_move"])

        self.btn_undo = ctk.CTkButton(self.toolbar, image=self.icon_undo, 
                                      command=lambda: self.controller.undo(), **button_style)
        self.btn_undo.pack(side="left", padx=2, pady=5)
        CTkToolTip(self.btn_undo, TEXT["gui"]["tooltip_undo"])

        self.btn_refresh = ctk.CTkButton(self.toolbar, image=self.icon_refresh, 
                                         command=lambda: self.controller.scan(), **button_style)
        self.btn_refresh.pack(side="left", padx=2, pady=5)
        CTkToolTip(self.btn_refresh, TEXT["gui"]["tooltip_refresh"])

        self.btn_config = ctk.CTkButton(self.toolbar, image=self.icon_config, 
                                        command=lambda: self.controller.open_config_editor(), **button_style)
        self.btn_config.pack(side="right", padx=10, pady=5)
        CTkToolTip(self.btn_config, TEXT["gui"]["tooltip_config_rules"])

        # パス表示用ラベルの追加
        self.path_label = ctk.CTkLabel(self.path_bar, text="Folder: -", font=ctk.CTkFont(size=12, slant="italic"))
        self.path_label.pack(side="left", padx=15, pady=2)

        # Sidebar (Extension Filters)
        self._setup_sidebar()
        # Preview (Treeview)
        self._setup_treeview()

    def _setup_sidebar(self):
        self.filter_label = ctk.CTkLabel(self.sidebar, text=TEXT["gui"]["filter_label"], font=ctk.CTkFont(weight="bold"))
        self.filter_label.pack(pady=(10, 5), padx=10)

        self.filter_container = ctk.CTkScrollableFrame(self.sidebar, width=180, fg_color="transparent")
        self.filter_container.pack(expand=True, fill="both", padx=5, pady=5)
        
        self.extension_selection_vars = {}  # {extension: BooleanVar}

    def _toggle_all_extensions(self):
        is_selected = self.master_toggle_var.get()
        for check_state in self.extension_selection_vars.values():
            check_state.set(is_selected)
        self.master_toggle_checkbox.configure(text=TEXT["gui"]["master_toggle_none"] if is_selected else TEXT["gui"]["master_toggle_all"])
        self.update_preview_table()

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
        self.tree_container = ctk.CTkFrame(self.preview_area, fg_color="white")
        self.tree_container.pack(expand=True, fill="both", padx=10, pady=10)

        self.file_tree = ttk.Treeview(self.tree_container, columns=("name", "dest"), show="headings", selectmode="browse")
        self.file_tree.heading("name", text=TEXT["gui"]["col_name"], anchor="w")
        self.file_tree.heading("dest", text=TEXT["gui"]["col_dest"], anchor="w")
        self.file_tree.column("name", width=300, minwidth=100)
        self.file_tree.column("dest", width=300, minwidth=100)
        
        self.file_tree.pack(side="left", expand=True, fill="both")
        self.file_tree.tag_configure("oddrow", background="#F9F9F9")
        self.file_tree.tag_configure("evenrow", background="white")

        # スクロールバー
        self.scrollbar = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        # Footer
        self.status_label = ctk.CTkLabel(self.footer, text="Status: Ready")
        self.status_label.pack(side="left", padx=20)

    # --- View API (ControllerがUIを操作するための公開メソッド) ---
    def update_preview_table(self, planned_moves=None):
        if planned_moves is not None:
            self.current_planned_moves = planned_moves

        self.clear_preview()
        selected_extensions = self.get_active_extensions()

        # 新しい項目を追加
        for i, move in enumerate(self.current_planned_moves):
            extension = move["src"].suffix.lower() or "(no ext)"
            # フィルタリングされている場合は移動先を空白にする
            dest_display = move["dst"].parent.name if extension in selected_extensions else "-"
            
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.file_tree.insert("", "end", values=(move["src"].name, dest_display), tags=(tag,))

    def clear_preview(self):
        self.file_tree.delete(*self.file_tree.get_children())

    def update_path_label(self, path):
        self.path_label.configure(text=f"Folder: {path}")

    def update_status(self, text):
        self.status_label.configure(text=text)

    def update_extension_filters(self, extension_counts):
        # 既存のチェックボックスを削除
        for widget in self.filter_container.winfo_children():
            widget.destroy()
        self.extension_selection_vars = {}

        if not extension_counts:
            return

        self.master_toggle_var = ctk.BooleanVar(value=True)
        self.master_toggle_checkbox = ctk.CTkCheckBox(self.filter_container, text=TEXT["gui"]["master_toggle_none"], 
                                                      variable=self.master_toggle_var, 
                                                      command=self._toggle_all_extensions,
                                                      font=ctk.CTkFont(size=12, weight="bold"))
        self.master_toggle_checkbox.pack(anchor="w", padx=10, pady=(5, 10))

        # 新しい統計に基づいてチェックボックスを作成
        for extension, count in sorted(extension_counts.items()):
            check_state = ctk.BooleanVar(value=True)
            checkbox = ctk.CTkCheckBox(self.filter_container, text=f"{extension} ({count})", 
                                       variable=check_state, font=ctk.CTkFont(size=12),
                                       command=self._on_extension_toggled)
            checkbox.pack(anchor="w", padx=10, pady=5)
            self.extension_selection_vars[extension] = check_state

    def _on_extension_toggled(self):
        # すべてにチェックが入っているか確認
        all_checked = all(var.get() for var in self.extension_selection_vars.values())
        
        # 統合チェックボックスの状態とテキストを更新
        self.master_toggle_var.set(all_checked)
        self.master_toggle_checkbox.configure(text=TEXT["gui"]["master_toggle_none"] if all_checked else TEXT["gui"]["master_toggle_all"])
        
        self.update_preview_table()

    def get_active_extensions(self):
        return {extension for extension, check_state in self.extension_selection_vars.items() if check_state.get()}

    def ask_yes_no(self, title, message):
        return messagebox.askyesno(title, message)

    def ask_directory(self):
        return filedialog.askdirectory()