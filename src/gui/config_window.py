import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import os
import copy
from resources.texts.text import TEXT
from gui.gui_utils import load_icon
from config.default import DEFAULT_CONFIG


class ConfigWindow(ctk.CTkToplevel):
    def __init__(self, parent, config_data, detected_extensions, on_save_callback):
        super().__init__(parent)

        self.title(TEXT["gui"]["config_window_title"])
        self.geometry("600x400")
        self.original_config = copy.deepcopy(config_data)
        self.working_config = copy.deepcopy(config_data)
        self.detected_extensions = detected_extensions
        self.on_save_callback = on_save_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 画像の読み込みパス設定
        self.icon_folder = load_icon("dir_select.png", size=(20, 20))

        # --- ルール追加エリア ---
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # --- 入力エリア一段目 ---
        self.row1_frame = ctk.CTkFrame(self.input_frame)
        self.row1_frame.pack(fill="x", padx=5, pady=(5, 2))
        # 拡張子entry
        self.lbl_ext = ctk.CTkLabel(self.row1_frame, text=TEXT["gui"]["col_extension"], width=100, anchor="w")
        self.lbl_ext.pack(side="left")
        extension_values = [ext.lstrip(".") for ext in sorted(self.detected_extensions.keys())]
        self.combo_ext = ctk.CTkComboBox(self.row1_frame, values=extension_values, width=180)
        self.combo_ext.pack(side="left", padx=5)
        self.combo_ext.set("")

        # 追加ボタン
        self.btn_add = ctk.CTkButton(self.row1_frame, text=TEXT["gui"]["cfg_add_rule"], 
                                     command=self._add_rule, fg_color="#1f538d", width=100)
        self.btn_add.pack(side="right", padx=10)

        # --- 入力エリア二段目 ---
        self.row2_frame = ctk.CTkFrame(self.input_frame)
        self.row2_frame.pack(fill="x", padx=5, pady=(2, 5))
        # 移動先entry
        self.lbl_dest = ctk.CTkLabel(self.row2_frame, text=TEXT["gui"]["col_destination"], width=100, anchor="w")
        self.lbl_dest.pack(side="left")
        self.entry_dest = ctk.CTkEntry(self.row2_frame, placeholder_text=TEXT["gui"]["cfg_destination_example"], width=160)
        self.entry_dest.pack(side="left", padx=5, fill="x", expand=True)
        # フォルダ参照ボタン
        self.btn_browse_dest = ctk.CTkButton(self.row2_frame, image=self.icon_folder, text="",
                                             command=self._pick_dest, width=32, height=32,
                                             fg_color="transparent", hover_color="#D0E0FF")
        self.btn_browse_dest.pack(side="left", padx=5)

        # --- ルール一覧表示 ---
        self._setup_treeview()
        self._refresh_list()

        # --- 操作ボタンエリア (編集・削除) ---
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.btn_edit = ctk.CTkButton(self.action_frame, text=TEXT["gui"]["cfg_edit_rule"], 
                                      command=self._edit_selected_rule, fg_color="#65A53B")
        self.btn_edit.pack(side="left", padx=5, expand=True, fill="x")

        self.btn_remove = ctk.CTkButton(self.action_frame, text=TEXT["gui"]["cfg_remove_rule"], 
                                        command=self._remove_selected_rule, fg_color="#a33333")
        self.btn_remove.pack(side="left", padx=5, expand=True, fill="x")

        # --- 初期化,保存ボタン ---
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        self.btn_reset = ctk.CTkButton(self.bottom_frame, text=TEXT["gui"]["cfg_reset_config"], 
                                       command=self._reset_config, fg_color="#606060")
        self.btn_reset.pack(side="left", padx=5, expand=True, fill="x")
        self.btn_save = ctk.CTkButton(self.bottom_frame, text=TEXT["gui"]["cfg_save_config"], 
                                      command=self._save_and_close)
        self.btn_save.pack(side="left", padx=5, expand=True, fill="x")

        # モーダル化
        self.transient(parent)
        self.grab_set()

        # Xボタン操作
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_treeview(self):
        style = ttk.Style()
        style.configure("Config.Treeview", background="white", rowheight=25)
        style.map("Config.Treeview", background=[('selected', '#1f538d')])

        self.tree_container = ctk.CTkFrame(self, fg_color="white")
        self.tree_container.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        self.tree = ttk.Treeview(self.tree_container, columns=("ext", "dest"), 
                                 show="headings", style="Config.Treeview", selectmode="browse")
        self.tree.heading("ext", text=TEXT["gui"]["col_extension"], anchor="w")
        self.tree.heading("dest", text=TEXT["gui"]["col_destination"], anchor="w")
        self.tree.column("ext", width=100)
        self.tree.column("dest", width=350)
        
        self.tree.pack(side="left", expand=True, fill="both")
        self.tree.tag_configure("oddrow", background="#F9F9F9")
        self.tree.tag_configure("evenrow", background="white")

        self.scrollbar = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")


    def _pick_dest(self):
        path = filedialog.askdirectory()
        if path:
            source_dir = self.working_config.get("source_directory")
            dest_path = path
            if source_dir:
                try:
                    # source_directoryからの相対パスを計算
                    abs_source = os.path.abspath(source_dir)
                    abs_dest = os.path.abspath(path)
                    
                    if abs_dest.startswith(abs_source):
                        dest_path = os.path.relpath(abs_dest, abs_source)
                except Exception:
                    pass

            # 入力欄にパスを反映
            self.entry_dest.delete(0, "end")
            self.entry_dest.insert(0, dest_path)

    def _add_rule(self):
        ext = self.combo_ext.get().strip().lower()
        dest = self.entry_dest.get().strip()
        if not ext:
            messagebox.showwarning("Error", TEXT["error"]["ext_required"], parent=self)
            return
        if not ext.startswith("."):
            ext = "." + ext
        if not dest:
            messagebox.showwarning("Error", TEXT["error"]["dest_required"], parent=self)
            return

        # 既存ルールがあれば上書き、なければ追加
        existing_rules = self.working_config.get("rules", [])
        target_rule = next((r for r in existing_rules if r["extension"].lower() == ext), None)
        
        if target_rule:
            target_rule["destination"] = dest
        else:
            new_rule = {"extension": ext, "destination": dest}
            if "rules" not in self.working_config:
                self.working_config["rules"] = []
            self.working_config["rules"].append(new_rule)

        self.combo_ext.set("")
        self.entry_dest.delete(0, "end")
        self._refresh_list()

    def _edit_selected_rule(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        ext, dest = item['values']
        
        self.combo_ext.delete(0, "end")
        self.combo_ext.insert(0, ext)
        self.entry_dest.delete(0, "end")
        self.entry_dest.insert(0, dest)

    def _remove_selected_rule(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        ext = self.tree.item(selected[0])['values'][0]
        self.working_config["rules"] = [r for r in self.working_config["rules"] if r["extension"] != ext]
        self._refresh_list()

    def _reset_config(self):
        if messagebox.askyesno(TEXT["gui"]["dialog_title_confirm"], TEXT["gui"]["cfg_dialog_reset_confirm"], parent=self):
            self.working_config = copy.deepcopy(DEFAULT_CONFIG)
            self._refresh_list()
            self.combo_ext.set("")
            self.entry_dest.delete(0, "end")

    def _refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        for i, rule in enumerate(self.working_config.get("rules", [])):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(rule['extension'], rule['destination']), tags=(tag,))

    def _save_and_close(self):
        self.on_save_callback(self.working_config)
        self.destroy()

    def _on_closing(self):
        if self.working_config == self.original_config:
            self.destroy()
            return
        
        result = messagebox.askyesnocancel(TEXT["gui"]["dialog_title_confirm"], TEXT["gui"]["cfg_close_without_save"], parent=self)
        if result is True:
            self._save_and_close()
        elif result is False:
            self.destroy()