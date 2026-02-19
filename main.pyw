import tkinter as tk
from tkinter import messagebox
import json
import os
import tkinter.font as tkfont

# Store tasks.json in the same folder as the script (your Todo folder)
TASKS_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_FILE = os.path.join(TASKS_DIR, "tasks.json")

def load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_tasks(tasks):
    try:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
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

def on_close(root, tasks):
    save_tasks(tasks)
    root.destroy()

def main():
    tasks = load_tasks()

    # normalize older string-only tasks to dicts
    for i, t in enumerate(tasks):
        if isinstance(t, str):
            tasks[i] = {"title": t, "priority": "Low", "description": "", "completed": False}
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

    close_btn = tk.Button(topbar, text="✕", command=lambda: on_close(root, tasks), bg=BG, fg=FG, activebackground=FG, activeforeground=BG, relief='flat', bd=0, font=FONT)
    close_btn.pack(side=tk.RIGHT, padx=6, pady=6)

    frame = tk.Frame(root, bg=BG)
    frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

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
            save_tasks(tasks)
        else:
            new = {"title": str(t), "priority": "Low", "description": "", "completed": True}
            tasks[idx] = new
            listbox.delete(idx)
            listbox.insert(idx, get_display_text(new))
            try:
                listbox.itemconfig(idx, fg="#777777")
            except Exception:
                pass
            save_tasks(tasks)

    btn_frame = tk.Frame(frame, bg=BG)
    btn_frame.pack(fill=tk.X, pady=(6, 0))

    def make_button(text, cmd, side=tk.LEFT, padx=(0,0)):
        b = tk.Button(btn_frame, text=text, command=cmd, bg=BTN_BG, fg=FG, activebackground=FG, activeforeground=BG, relief='flat', font=FONT)
        b.pack(side=side, padx=padx)
        return b

    # Add / Remove / Complete / Clear / Save
    def add_task_dialog():
        dlg = tk.Toplevel(root)
        dlg.title("Add Task")
        dlg.configure(bg=BG)

        tk.Label(dlg, text="Title:", bg=BG, fg=FG, font=FONT).grid(row=0, column=0, sticky="w", padx=6, pady=6)
        title_e = tk.Entry(dlg, bg=INPUT_BG, fg=FG, insertbackground=FG, font=FONT)
        title_e.grid(row=0, column=1, padx=6, pady=6)

        tk.Label(dlg, text="Priority:", bg=BG, fg=FG, font=FONT).grid(row=1, column=0, sticky="w", padx=6)
        prio_var = tk.StringVar(value="Low")
        prio_opt = tk.OptionMenu(dlg, prio_var, "Low", "Medium", "High")
        prio_opt.configure(bg=BTN_BG, fg=FG, highlightthickness=0)
        prio_opt.grid(row=1, column=1, sticky="w", padx=6)

        tk.Label(dlg, text="Description:", bg=BG, fg=FG, font=FONT).grid(row=2, column=0, sticky="nw", padx=6, pady=6)
        desc_t = tk.Text(dlg, height=6, width=30, bg=INPUT_BG, fg=FG, font=FONT)
        desc_t.grid(row=2, column=1, padx=6, pady=6)

        def on_save():
            title = title_e.get().strip()
            if not title:
                messagebox.showwarning("Missing Title", "Please enter a title.")
                return
            new = {"title": title, "priority": prio_var.get(), "description": desc_t.get("1.0", "end").strip(), "completed": False}
            tasks.append(new)
            listbox.insert(tk.END, get_display_text(new))
            # select the new item and show its description
            listbox.selection_clear(0, tk.END)
            last = listbox.size() - 1
            listbox.selection_set(last)
            show_selected_description()
            save_tasks(tasks)
            dlg.destroy()

        tk.Button(dlg, text="Save", command=on_save, bg=BTN_BG, fg=FG, font=FONT).grid(row=3, column=0, columnspan=2, pady=6)

    add_btn = make_button("Add", add_task_dialog, side=tk.LEFT)
    def remove_and_update():
        remove_selected(listbox, tasks)
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
        show_selected_description()

    remove_btn = make_button("Remove", remove_and_update, side=tk.LEFT, padx=(6,0))
    complete_btn = make_button("Complete", lambda: (complete_selected(listbox, tasks), show_selected_description()), side=tk.LEFT, padx=(6,0))
    clear_btn = make_button("Clear All", clear_and_update, side=tk.LEFT, padx=(6,0))
    save_btn = make_button("Save", lambda: save_tasks(tasks), side=tk.RIGHT)

    def on_enter(event):
        add_task(entry, listbox, tasks)
        # select the newly added item and show description (it has empty description)
        try:
            last = listbox.size() - 1
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(last)
        except Exception:
            pass
        show_selected_description()

    entry.bind('<Return>', on_enter)

    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root, tasks))
    root.mainloop()

if __name__ == "__main__":
    main()