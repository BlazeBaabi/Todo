import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import tkinter.font as tkfont

# Store tasks.json in the same folder as the script (your Todo folder)
TASKS_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_FILE = os.path.join(TASKS_DIR, "tasks.json")

def load_collections():
    # return a dict mapping collection names to lists of tasks
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return {"Default": []}
        if isinstance(data, dict):
            # ensure all values are lists
            for k, v in list(data.items()):
                if not isinstance(v, list):
                    data[k] = []
            if not data:
                data = {"Default": []}
            return data
        elif isinstance(data, list):
            # backward compatibility
            return {"Default": data}
        else:
            return {"Default": []}
    return {"Default": []}


def save_collections(collections):
    try:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(collections, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showerror("Save Error", f"Could not save tasks: {e}")

def add_task(entry, listbox, tasks):
    title = entry.get().strip()
    if title:
        task = {"title": title, "priority": "Low", "description": "", "completed": False}
        tasks.append(task)
        # simple display until Treeview/dialog enhancements
        listbox.insert(tk.END, f"{title}  [Low]")
        entry.delete(0, tk.END)

def remove_selected(listbox, tasks):
    sel = listbox.curselection()
    if not sel:
        return
    index = sel[0]
    listbox.delete(index)
    try:
        tasks.pop(index)
    except Exception:
        pass

def clear_all(listbox, tasks):
    if messagebox.askyesno("Clear All", "Delete all tasks?"):
        listbox.delete(0, tk.END)
        tasks.clear()

def on_close(root, tasks, collections, current_collection):
    save_collections(collections)
    root.destroy()

def main():
    collections = load_collections()
    # ensure at least one collection exists
    if not collections:
        collections = {"Default": []}
    current_collection = next(iter(collections))
    tasks = collections[current_collection]

    # normalize older string-only tasks to dicts in all collections
    for col, lst in collections.items():
        for i, t in enumerate(lst):
            if isinstance(t, str):
                lst[i] = {"title": t, "priority": "Low", "description": "", "completed": False}
            elif isinstance(t, dict):
                t.setdefault("priority", "Low")
                t.setdefault("description", "")
                t.setdefault("completed", False)

    root = tk.Tk()
    root.title("To-Do List")
    root.geometry("360x420")

    # Fullscreen startup and icon support
    START_FULLSCREEN = True
    if START_FULLSCREEN:
        try:
            root.attributes("-fullscreen", True)
        except Exception:
            try:
                root.state('zoomed')
            except Exception:
                pass

    # fullscreen toggle helpers (F11 to toggle, Esc to exit)
    _fs = {"on": bool(START_FULLSCREEN)}
    def toggle_fullscreen(event=None):
        _fs["on"] = not _fs["on"]
        try:
            root.attributes("-fullscreen", _fs["on"]) 
        except Exception:
            try:
                root.state('zoomed' if _fs["on"] else 'normal')
            except Exception:
                pass

    def exit_fullscreen(event=None):
        _fs["on"] = False
        try:
            root.attributes("-fullscreen", False)
        except Exception:
            try:
                root.state('normal')
            except Exception:
                pass

    root.bind('<F11>', toggle_fullscreen)
    root.bind('<Escape>', exit_fullscreen)

    # Load a custom icon from the script folder. Prefer Todo.ico, then icon.ico, then icon.png
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ico_candidates = [os.path.join(base_dir, name) for name in ("Todo.ico", "icon.ico")]
    png_path = os.path.join(base_dir, "icon.png")
    for ico_path in ico_candidates:
        if os.path.exists(ico_path):
            try:
                root.iconbitmap(ico_path)
                break
            except Exception:
                continue
    else:
        if os.path.exists(png_path):
            try:
                _img = tk.PhotoImage(file=png_path)
                root.iconphoto(False, _img)
                root._icon_img = _img
            except Exception:
                pass

    # Cyber 8-bit theme colors and font
    BG = "#121212"
    FG = "#00FFAB"
    INPUT_BG = "#0b0b0b"
    BTN_BG = "#0d0d0d"
    FONT = tkfont.Font(family="Consolas", size=10)

    root.configure(bg=BG)

    # Top bar with app icon, title, and corner close button (visible when fullscreen)
    topbar = tk.Frame(root, bg=BG)
    topbar.pack(fill=tk.X, side=tk.TOP)

    # Left: load high-quality TodoIcon.png if present and show title
    todo_icon_path = os.path.join(base_dir, "TodoIcon.png")
    if os.path.exists(todo_icon_path):
        try:
            _orig_img = tk.PhotoImage(file=todo_icon_path)
            # Scale down to roughly match the '✕' button height (~16px)
            desired_size = 16
            ow = _orig_img.width()
            oh = _orig_img.height()
            if max(ow, oh) > desired_size:
                factor = max(1, int(max(ow, oh) / desired_size))
                _top_img = _orig_img.subsample(factor, factor)
            else:
                _top_img = _orig_img
            icon_lbl = tk.Label(topbar, image=_top_img, bg=BG)
            icon_lbl.image = _top_img
            icon_lbl.pack(side=tk.LEFT, padx=(6,0), pady=6)
        except Exception:
            pass

    title_font = tkfont.Font(family="Consolas", size=12, weight="bold")
    title_lbl = tk.Label(topbar, text="Todo", bg=BG, fg=FG, font=title_font)
    title_lbl.pack(side=tk.LEFT, padx=(6,0), pady=6)

    close_btn = tk.Button(topbar, text="✕", command=lambda: on_close(root, tasks, collections, current_collection), bg=BG, fg=FG, activebackground=FG, activeforeground=BG, relief='flat', bd=0, font=FONT)
    close_btn.pack(side=tk.RIGHT, padx=6, pady=6)

    frame = tk.Frame(root, bg=BG)
    frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # --- collection selector and management ---
    coll_frame = tk.Frame(frame, bg=BG)
    coll_frame.pack(fill=tk.X, pady=(0,6))
    tk.Label(coll_frame, text="Collection:", bg=BG, fg=FG, font=FONT).pack(side=tk.LEFT)
    coll_var = tk.StringVar(value=current_collection)
    def rebuild_coll_menu():
        menu = coll_menu['menu']
        menu.delete(0, 'end')
        for name in collections.keys():
            menu.add_command(label=name, command=lambda n=name: coll_var.set(n) or switch_collection(n))
    coll_menu = tk.OptionMenu(coll_frame, coll_var, *collections.keys(), command=lambda n: switch_collection(n))
    coll_menu.configure(bg=BTN_BG, fg=FG, highlightthickness=0)
    coll_menu.pack(side=tk.LEFT, padx=6)
    def switch_collection(name):
        nonlocal current_collection, tasks
        if name not in collections:
            return
        current_collection = name
        tasks = collections[current_collection]
        coll_var.set(name)
        # refresh task list
        listbox.delete(0, tk.END)
        for t in tasks:
            listbox.insert(tk.END, get_display_text(t))
        # select first item
        if tasks:
            listbox.selection_set(0)
            show_selected_description()
        else:
            desc_view.configure(state='normal')
            desc_view.delete('1.0', tk.END)
            desc_view.configure(state='disabled')
        hide_form()
    def add_collection():
        name = simpledialog.askstring("New Collection", "Enter collection name:", parent=root)
        if not name:
            return
        if name in collections:
            messagebox.showwarning("Exists", "A collection with that name already exists.")
            return
        collections[name] = []
        rebuild_coll_menu()
        switch_collection(name)
        save_collections(collections)
    def rename_collection():
        nonlocal current_collection
        old = current_collection
        name = simpledialog.askstring("Rename Collection", "New name:", initialvalue=old, parent=root)
        if not name or name == old:
            return
        if name in collections:
            messagebox.showwarning("Exists", "A collection with that name already exists.")
            return
        collections[name] = collections.pop(old)
        current_collection = name
        rebuild_coll_menu()
        coll_var.set(name)
        save_collections(collections)
    def delete_collection():
        nonlocal current_collection, tasks
        if len(collections) == 1:
            messagebox.showwarning("Cannot delete", "At least one collection must remain.")
            return
        if not messagebox.askyesno("Delete Collection", f"Delete '{current_collection}'? This cannot be undone."):
            return
        collections.pop(current_collection, None)
        # pick another
        current_collection = next(iter(collections))
        tasks = collections[current_collection]
        rebuild_coll_menu()
        coll_var.set(current_collection)
        switch_collection(current_collection)
        save_collections(collections)
    tk.Button(coll_frame, text="New", command=add_collection, bg=BTN_BG, fg=FG, font=FONT).pack(side=tk.LEFT, padx=(6,0))
    tk.Button(coll_frame, text="Rename", command=rename_collection, bg=BTN_BG, fg=FG, font=FONT).pack(side=tk.LEFT, padx=(6,0))
    tk.Button(coll_frame, text="Delete", command=delete_collection, bg=BTN_BG, fg=FG, font=FONT).pack(side=tk.LEFT, padx=(6,0))

    entry = tk.Entry(frame, bg=INPUT_BG, fg=FG, insertbackground=FG, relief='flat', font=FONT)
    entry.pack(fill=tk.X, pady=(0, 6))

    listbox = tk.Listbox(frame, height=15, bg=INPUT_BG, fg=FG, selectbackground=FG, selectforeground=BG, activestyle='none', font=FONT)
    listbox.pack(fill=tk.BOTH, expand=True)

    def get_display_text(t):
        if isinstance(t, dict):
            title = t.get("title", "")
            prio = t.get("priority", "")
            completed = t.get("completed", False)
            disp = title
            if prio:
                disp += f"  [{prio}]"
            if completed:
                disp = "✓ " + disp
            return disp
        return str(t)

    for t in tasks:
        listbox.insert(tk.END, get_display_text(t))
        # grey out completed tasks
        if isinstance(t, dict) and t.get("completed"):
            idx = listbox.size() - 1
            try:
                listbox.itemconfig(idx, fg="#777777")
            except Exception:
                pass

    # Description viewer (read-only) shown below the list
    tk.Label(frame, text="Description:", bg=BG, fg=FG, font=FONT).pack(anchor="w", pady=(8,0))
    desc_view = tk.Text(frame, height=6, bg=INPUT_BG, fg=FG, font=FONT, wrap=tk.WORD)
    desc_view.pack(fill=tk.X, pady=(0,6))
    desc_view.configure(state='disabled')

    def show_selected_description(event=None):
        sel = listbox.curselection()
        desc_view.configure(state='normal')
        desc_view.delete('1.0', tk.END)
        if not sel:
            desc_view.configure(state='disabled')
            return
        idx = sel[0]
        try:
            t = tasks[idx]
        except Exception:
            desc_view.configure(state='disabled')
            return
        if isinstance(t, dict):
            desc = t.get('description', '')
        else:
            desc = ''
        desc_view.insert(tk.END, desc)
        desc_view.configure(state='disabled')

    listbox.bind('<<ListboxSelect>>', show_selected_description)
    # select first item initially
    if tasks:
        listbox.selection_set(0)
        show_selected_description()

    def complete_selected(listbox, tasks):
        sel = listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        try:
            t = tasks[idx]
        except Exception:
            return
        if isinstance(t, dict):
            t["completed"] = not t.get("completed", False)
            listbox.delete(idx)
            listbox.insert(idx, get_display_text(t))
            try:
                if t["completed"]:
                    listbox.itemconfig(idx, fg="#777777")
                else:
                    listbox.itemconfig(idx, fg=FG)
            except Exception:
                pass
            save_collections(collections)
        else:
            new = {"title": str(t), "priority": "Low", "description": "", "completed": True}
            tasks[idx] = new
            listbox.delete(idx)
            listbox.insert(idx, get_display_text(new))
            try:
                listbox.itemconfig(idx, fg="#777777")
            except Exception:
                pass
            save_collections(collections)

    btn_frame = tk.Frame(frame, bg=BG)
    btn_frame.pack(fill=tk.X, pady=(6, 0))

    def make_button(text, cmd, side=tk.LEFT, padx=(0,0)):
        b = tk.Button(btn_frame, text=text, command=cmd, bg=BTN_BG, fg=FG, activebackground=FG, activeforeground=BG, relief='flat', font=FONT)
        b.pack(side=side, padx=padx)
        return b

    # Add / Remove / Complete / Clear / Save / Edit
    # inline form (hidden) used for both adding and editing
    editing_index = None
    add_frame = tk.Frame(frame, bg=BG)

    tk.Label(add_frame, text="Title:", bg=BG, fg=FG, font=FONT).grid(row=0, column=0, sticky="w", padx=6, pady=3)
    add_title = tk.Entry(add_frame, bg=INPUT_BG, fg=FG, insertbackground=FG, font=FONT)
    add_title.grid(row=0, column=1, padx=6, pady=3)

    add_title.bind('<Return>', lambda e: on_form_save())

    tk.Label(add_frame, text="Priority:", bg=BG, fg=FG, font=FONT).grid(row=1, column=0, sticky="w", padx=6, pady=3)
    prio_var = tk.StringVar(value="Low")
    prio_opt = tk.OptionMenu(add_frame, prio_var, "Low", "Medium", "High")
    prio_opt.configure(bg=BTN_BG, fg=FG, highlightthickness=0)
    prio_opt.grid(row=1, column=1, sticky="w", padx=6, pady=3)

    tk.Label(add_frame, text="Description:", bg=BG, fg=FG, font=FONT).grid(row=2, column=0, sticky="nw", padx=6, pady=3)
    add_desc = tk.Text(add_frame, height=4, width=30, bg=INPUT_BG, fg=FG, font=FONT)
    add_desc.grid(row=2, column=1, padx=6, pady=3)

    def show_form():
        try:
            add_frame.pack(fill=tk.X, pady=(6,0), before=btn_frame)
        except Exception:
            add_frame.pack(fill=tk.X, pady=(6,0))

    def hide_form():
        nonlocal editing_index
        add_frame.pack_forget()
        editing_index = None
        add_title.delete(0, tk.END)
        prio_var.set("Low")
        add_desc.delete("1.0", tk.END)
        save_btn_form.configure(text="Save")

    def on_form_save():
        nonlocal editing_index
        title = add_title.get().strip()
        if not title:
            messagebox.showwarning("Missing Title", "Please enter a title.")
            return
        if editing_index is None:
            # add new task
            new = {"title": title, "priority": prio_var.get(), "description": add_desc.get("1.0", "end").strip(), "completed": False}
            tasks.append(new)
            listbox.insert(tk.END, get_display_text(new))
            listbox.selection_clear(0, tk.END)
            last = listbox.size() - 1
            listbox.selection_set(last)
            show_selected_description()
            save_collections(collections)
            hide_form()
        else:
            t = tasks[editing_index]
            t["title"] = title
            t["priority"] = prio_var.get()
            t["description"] = add_desc.get("1.0", "end").strip()
            listbox.delete(editing_index)
            listbox.insert(editing_index, get_display_text(t))
            if t.get("completed"):
                try:
                    listbox.itemconfig(editing_index, fg="#777777")
                except Exception:
                    pass
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(editing_index)
            show_selected_description()
            save_collections(collections)
            hide_form()

    def start_edit():
        nonlocal editing_index
        sel = listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        t = tasks[idx]
        if isinstance(t, dict):
            add_title.delete(0, tk.END)
            add_title.insert(0, t.get("title", ""))
            prio_var.set(t.get("priority", "Low"))
            add_desc.delete("1.0", tk.END)
            add_desc.insert("1.0", t.get("description", ""))
        else:
            add_title.delete(0, tk.END)
            add_title.insert(0, str(t))
            prio_var.set("Low")
            add_desc.delete("1.0", tk.END)
        editing_index = idx
        save_btn_form.configure(text="Update")
        show_form()

    def toggle_add_frame():
        if add_frame.winfo_ismapped():
            hide_form()
        else:
            if editing_index is None:
                add_title.delete(0, tk.END)
                prio_var.set("Low")
                add_desc.delete("1.0", tk.END)
            show_form()

    # buttons will call these helpers

    add_btn = make_button("Add", toggle_add_frame, side=tk.LEFT)
    edit_btn = make_button("Edit", start_edit, side=tk.LEFT, padx=(6,0))
    save_btn_form = tk.Button(add_frame, text="Save", command=on_form_save, bg=BTN_BG, fg=FG, font=FONT)
    save_btn_form.grid(row=3, column=0, pady=6, padx=(6,3))
    tk.Button(add_frame, text="Cancel", command=lambda: hide_form(), bg=BTN_BG, fg=FG, font=FONT).grid(row=3, column=1, pady=6, padx=(3,6))
    def remove_and_update():
        remove_selected(listbox, tasks)
        save_collections(collections)
        # clear selection and description
        try:
            listbox.selection_clear(0, tk.END)
            if listbox.size() > 0:
                listbox.selection_set(0)
        except Exception:
            pass
        show_selected_description()

    def clear_and_update():
        clear_all(listbox, tasks)
        save_collections(collections)
        show_selected_description()

    remove_btn = make_button("Remove", remove_and_update, side=tk.LEFT, padx=(6,0))
    complete_btn = make_button("Complete", lambda: (complete_selected(listbox, tasks), show_selected_description()), side=tk.LEFT, padx=(6,0))
    clear_btn = make_button("Clear All", clear_and_update, side=tk.LEFT, padx=(6,0))
    save_btn = make_button("Save", lambda: save_collections(collections), side=tk.RIGHT)

    def on_enter(event):
        add_task(entry, listbox, tasks)
        save_collections(collections)
        # select the newly added item and show description (it has empty description)
        try:
            last = listbox.size() - 1
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(last)
        except Exception:
            pass
        show_selected_description()

    entry.bind('<Return>', on_enter)

    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root, tasks, collections, current_collection))
    root.mainloop()

if __name__ == "__main__":
    main()
