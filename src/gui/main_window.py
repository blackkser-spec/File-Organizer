import customtkinter as ctk
from tkinter import filedialog, ttk, messagebox
import tkinter as tk
from resources.texts.text import TEXT
from gui.gui_utils import load_icon

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
        self.geometry("800x600")
        self.controller = None
        self.current_planned_moves = []

        # レイアウト設定
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Frame配置
        self.toolbar = ctk.CTkFrame(self, corner_radius=0, border_width=2, border_color="#C8C8C8")
        self.path_bar = ctk.CTkFrame(self, corner_radius=0, fg_color="#F8F8F8", border_width=2, border_color="#D0D0D0")
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, border_width=2, border_color="#C8C8C8")
        self.preview_area = ctk.CTkFrame(self, corner_radius=0, border_width=2, border_color="#C8C8C8")
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
        # アイコンの読み込み
        icon_size = (32, 32)
        self.icon_folder = load_icon("dir_select.png", size=icon_size)
        self.icon_run = load_icon("move.png", size=icon_size)
        self.icon_undo = load_icon("undo.png", size=icon_size)
        self.icon_refresh = load_icon("refresh.png", size=icon_size)
        self.icon_config = load_icon("option.png", size=icon_size)

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
                                      command=lambda: self.controller.execute_undo(), **button_style)
        self.btn_undo.pack(side="left", padx=2, pady=5)
        CTkToolTip(self.btn_undo, TEXT["gui"]["tooltip_undo"])

        self.btn_refresh = ctk.CTkButton(self.toolbar, image=self.icon_refresh, 
                                         command=lambda: self.controller.execute_refresh(), **button_style)
        self.btn_refresh.pack(side="left", padx=2, pady=5)
        CTkToolTip(self.btn_refresh, TEXT["gui"]["tooltip_refresh"])

        self.btn_config = ctk.CTkButton(self.toolbar, image=self.icon_config, 
                                        command=lambda: self.controller.open_config_editor(), **button_style)
        self.btn_config.pack(side="right", padx=10, pady=5)
        CTkToolTip(self.btn_config, TEXT["gui"]["tooltip_config_rules"])

        # パス表示用ラベルの追加
        self.path_label = ctk.CTkLabel(self.path_bar, text=TEXT["gui"]["path_label_default"], )
        self.path_label.pack(side="left", padx=15, pady=2)

        # Sidebar (Extension Filters)
        self._setup_sidebar()
        # Preview (Treeview)
        self._setup_treeview()

    def _setup_sidebar(self):
        self.filter_label = ctk.CTkLabel(self.sidebar, text=TEXT["gui"]["filter_label"], font=ctk.CTkFont(weight="bold"))
        self.filter_label.pack(pady=(10, 5), padx=10)
        self.filter_container = ctk.CTkScrollableFrame(self.sidebar, width=180, fg_color="#FAFAFA", border_width=1, border_color="#DDDDDD")
        self.filter_container.pack(expand=True, fill="both", padx=5, pady=5)
        
        self.extension_selection_vars = {}  # {extension: BooleanVar}

    def _toggle_all_extensions(self):
        is_selected = self.master_toggle_var.get()
        for check_state in self.extension_selection_vars.values():
            check_state.set(is_selected)
        self.master_toggle_checkbox.configure(text=TEXT["gui"]["master_toggle_none"] if is_selected else TEXT["gui"]["master_toggle_all"])
        self.controller.refresh_preview()

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
        self.file_tree.heading("dest", text=TEXT["gui"]["col_destination"], anchor="w")
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
        # 移動予定のアイテム総数
        self.move_item_count = ctk.CTkLabel(self.footer, text="0 items", width=190, anchor="w")
        self.move_item_count.pack(side="left", padx=(10, 5))
        # 区切り
        self.separator1 = ctk.CTkLabel(self.footer, text="|")
        self.separator1.pack(side="left", padx=5)
        # ステータスエリア
        self.status_label = ctk.CTkLabel(self.footer, text=TEXT["gui"]["footer_status_default"])
        self.status_label.pack(side="left", padx=5)
        # Undoが実行可能か
        self.undo_status = ctk.CTkLabel(self.footer, text="Undo: -")
        self.undo_status.pack(side="right", padx=10)
        # 区切り
        self.separator2 = ctk.CTkLabel(self.footer, text="|")
        self.separator2.pack(side="right", padx=5)

    # --- View API (ControllerがUIを操作するための公開メソッド) ---
    def update_preview_table(self, rows):
        self.clear_preview()

        for i, row in enumerate(rows):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.file_tree.insert("", "end", values=(row["name"], row["destination"]), tags=(tag,))

    def clear_preview(self):
        self.file_tree.delete(*self.file_tree.get_children())

    def update_path_label(self, path):
        self.path_label.configure(text=TEXT["gui"]["folder_display"].format(path=path))

    def update_move_item_count(self, move: int, total: int):
        self.move_item_count.configure(text=TEXT["gui"]["footer_move_item_count"].format(move=move, total=total))

    def update_status(self, text):
        self.status_label.configure(text=text)

    def update_undo_status(self, available: bool):
        text = TEXT["gui"]["footer_undo_available"] if available else TEXT["gui"]["footer_undo_unavailable"]
        self.undo_status.configure(text=text)

    def update_extension_filters(self, extension_counts):
        # 既存のチェックボックスを削除
        for widget in self.filter_container.winfo_children():
            widget.destroy()
        self.extension_selection_vars = {}

        if not extension_counts:
            return

        # 「すべて選択/解除」
        self.master_toggle_var = ctk.BooleanVar(value=True)
        self.master_toggle_checkbox = ctk.CTkCheckBox(
            self.filter_container,
            text=TEXT["gui"]["master_toggle_none"],
            variable=self.master_toggle_var,
            command=self._toggle_all_extensions,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.master_toggle_checkbox.pack(fill="x", padx=5, pady=(5, 10))

        # 拡張子一覧
        for extension, count in sorted(extension_counts.items()):
            row = ctk.CTkFrame(
                self.filter_container,
                fg_color="#F8F8F8",
            )
            row.pack(fill="x", padx=5, pady=2)

            check_state = ctk.BooleanVar(value=True)

            checkbox = ctk.CTkCheckBox(
                row,
                text=extension,
                variable=check_state,
                command=self._on_extension_toggled,
                font=ctk.CTkFont(size=12),
            )
            checkbox.pack(side="left", anchor="w")

            count_label = ctk.CTkLabel(
                row,
                text=f"({count})",
                font=ctk.CTkFont(size=12),
            )
            count_label.pack(side="right", padx=(0, 5))

            self.extension_selection_vars[extension] = check_state

    def _on_extension_toggled(self):
        # すべてにチェックが入っているか確認
        all_checked = all(var.get() for var in self.extension_selection_vars.values())
        
        self.master_toggle_var.set(all_checked)
        self.master_toggle_checkbox.configure(text=TEXT["gui"]["master_toggle_none"] if all_checked else TEXT["gui"]["master_toggle_all"])
        
        self.controller.refresh_preview()

    def get_active_extensions(self):
        return {extension for extension, check_state in self.extension_selection_vars.items() if check_state.get()}

    def ask_yes_no(self, title, message):
        return messagebox.askyesno(title, message)

    def ask_directory(self):
        return filedialog.askdirectory()