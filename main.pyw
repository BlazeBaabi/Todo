import time
import requests
import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import tkinter.font as tkfont
from datetime import datetime, timezone

REF_RATE = 1000

BASE_URL = "https://blazeblade.pythonanywhere.com"


def api_request(method, endpoint, json_data=None):
    try:
        response = requests.request(method, BASE_URL + endpoint, json=json_data, timeout=10)
    except requests.RequestException as exc:
        messagebox.showerror("API Error", f"Could not connect to server:\n{exc}")
        return None

    try:
        data = response.json()
    except ValueError:
        data = None

    if not response.ok:
        message = None
        if isinstance(data, dict):
            message = data.get("error") or data.get("message")
        if not message:
            message = response.text or f"HTTP {response.status_code}"
        messagebox.showerror("API Error", message)
        return None

    return data


def get_all_data():
    return api_request("GET", "/collections")


def create_collection_api(name):
    return api_request("POST", "/collections", json_data={"name": name})


def delete_collection_api(name):
    return api_request("DELETE", f"/collections/{name}")


def add_task_api(collection, title, description="", priority="Low", deadline="", attachment=""):
    return api_request(
        "POST",
        f"/tasks/{collection}",
        json_data={
            "title": title,
            "description": description,
            "priority": priority,
            "deadline": deadline,
            "attachment": attachment,
        },
    )


def update_task_api(task_id, **updates):
    return api_request("PUT", f"/tasks/{task_id}", json_data=updates)


def delete_task_api(task_id):
    return api_request("DELETE", f"/tasks/{task_id}")


def set_complete_api(task_id, completed=True):
    return api_request("PATCH", f"/tasks/{task_id}/complete", json_data={"completed": completed})


def normalize_task(task):
    if not isinstance(task, dict):
        return {
            "id": None,
            "title": str(task),
            "priority": "Low",
            "description": "",
            "completed": False,
            "deadline": "",
            "attachment": "",
            "time_created": "",
        }
    task.setdefault("id", None)
    task.setdefault("title", "")
    task.setdefault("priority", "Low")
    task.setdefault("description", "")
    task.setdefault("completed", False)
    task.setdefault("deadline", "")
    task.setdefault("attachment", "")
    task.setdefault("time_created", "")
    return task


def format_time_created(value):
    if not value:
        return ""
    if isinstance(value, str):
        try:
            # Handle ISO 8601 strings with or without timezone info
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            try:
                dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                dt = dt.replace(tzinfo=timezone.utc)
            except ValueError:
                return value
        try:
            local_dt = dt.astimezone() if dt.tzinfo else dt.replace(tzinfo=timezone.utc).astimezone()
            return local_dt.strftime("%b %d %Y %H:%M")
        except Exception:
            return value
    return str(value)


def on_close(root, tasks, collections, current_collection):
    root.destroy()


def main():
    collections = get_all_data()
    if not isinstance(collections, dict) or not collections:
        collections = {"Default": []}

    for col, lst in list(collections.items()):
        if not isinstance(lst, list):
            collections[col] = []
            continue
        for i, t in enumerate(lst):
            collections[col][i] = normalize_task(t)

    if not collections:
        collections = {"Default": []}

    current_collection = next(iter(collections))
    tasks = collections[current_collection]

    root = tk.Tk()
    root.title("To-Do List")
    root.geometry("360x420")

    
    START_FULLSCREEN = True
    if START_FULLSCREEN:
        try:
            root.attributes("-fullscreen", True)
        except Exception:
            try:
                root.state('zoomed')
            except Exception:
                pass

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

    
    BG = "#121212"
    FG = "#00FFAB"
    INPUT_BG = "#0b0b0b"
    BTN_BG = "#0d0d0d"
    FONT = tkfont.Font(family="Consolas", size=10)

    root.configure(bg=BG)

    
    topbar = tk.Frame(root, bg=BG)
    topbar.pack(fill=tk.X, side=tk.TOP)

    
    todo_icon_path = os.path.join(base_dir, "TodoIcon.png")
    if os.path.exists(todo_icon_path):
        try:
            _orig_img = tk.PhotoImage(file=todo_icon_path)
            
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

    coll_frame = tk.Frame(frame, bg=BG)
    coll_frame.pack(fill=tk.X, pady=(0, 6))
    tk.Label(coll_frame, text="Collection:", bg=BG, fg=FG, font=FONT).pack(side=tk.LEFT)
    coll_var = tk.StringVar(value=current_collection)

    def rebuild_coll_menu():
        menu = coll_menu["menu"]
        menu.delete(0, "end")
        for name in collections.keys():
            menu.add_command(label=name, command=lambda n=name: coll_var.set(n) or switch_collection(n))

    def refresh_collections():
        nonlocal collections, tasks, current_collection
        data = get_all_data()
        if data is None:
            return False
        if not isinstance(data, dict):
            data = {}
        for col, lst in list(data.items()):
            if not isinstance(lst, list):
                data[col] = []
            else:
                for i, t in enumerate(lst):
                    data[col][i] = normalize_task(t)
        if not data:
            data = {"Default": []}
        collections = data
        if current_collection not in collections:
            current_collection = next(iter(collections))
        tasks = collections[current_collection]
        rebuild_coll_menu()
        coll_var.set(current_collection)
        switch_collection(current_collection)
        return True

    def switch_collection(name):
        nonlocal current_collection, tasks
        if name not in collections:
            return
        current_collection = name
        tasks = collections[current_collection]
        coll_var.set(name)

        listbox.delete(0, tk.END)
        for t in tasks:
            listbox.insert(tk.END, get_display_text(t))

        if tasks:
            listbox.selection_set(0)
            show_selected_description()
        else:
            desc_view.configure(state="normal")
            desc_view.delete("1.0", tk.END)
            desc_view.configure(state="disabled")
        hide_form()

    def add_collection():
        name = simpledialog.askstring("New Collection", "Enter collection name:", parent=root)
        if not name:
            return
        if name in collections:
            messagebox.showwarning("Exists", "A collection with that name already exists.")
            return
        if create_collection_api(name) is None:
            return
        refresh_collections()
        switch_collection(name)

    def rename_collection():
        nonlocal current_collection
        old = current_collection
        name = simpledialog.askstring("Rename Collection", "New name:", initialvalue=old, parent=root)
        if not name or name == old:
            return
        if name in collections:
            messagebox.showwarning("Exists", "A collection with that name already exists.")
            return
        if create_collection_api(name) is None:
            return
        for task in list(collections.get(old, [])):
            add_result = add_task_api(
                name,
                task.get("title", ""),
                task.get("description", ""),
                task.get("priority", "Low"),
                task.get("deadline", ""),
                task.get("attachment", ""),
            )
            if add_result is None:
                continue
            if task.get("completed"):
                new_id = add_result.get("id")
                if new_id is not None:
                    set_complete_api(new_id, True)
        if delete_collection_api(old) is None:
            messagebox.showwarning(
                "Partial Rename",
                "The new collection was created, but the old collection could not be deleted.",
            )
        refresh_collections()
        switch_collection(name)

    def delete_collection():
        nonlocal current_collection, tasks
        if len(collections) == 1:
            messagebox.showwarning("Cannot delete", "At least one collection must remain.")
            return
        if not messagebox.askyesno("Delete Collection", f"Delete '{current_collection}'? This cannot be undone."):
            return
        if delete_collection_api(current_collection) is None:
            return
        refresh_collections()
        current_collection = next(iter(collections))
        switch_collection(current_collection)

    coll_menu = tk.OptionMenu(coll_frame, coll_var, *collections.keys(), command=lambda n: switch_collection(n))
    coll_menu.configure(bg=BTN_BG, fg=FG, highlightthickness=0)
    coll_menu.pack(side=tk.LEFT, padx=6)
    tk.Button(coll_frame, text="New", command=add_collection, bg=BTN_BG, fg=FG, font=FONT).pack(side=tk.LEFT, padx=(6, 0))
    tk.Button(coll_frame, text="Rename", command=rename_collection, bg=BTN_BG, fg=FG, font=FONT).pack(side=tk.LEFT, padx=(6, 0))
    tk.Button(coll_frame, text="Delete", command=delete_collection, bg=BTN_BG, fg=FG, font=FONT).pack(side=tk.LEFT, padx=(6, 0))

    entry = tk.Entry(frame, bg=INPUT_BG, fg=FG, insertbackground=FG, relief='flat', font=FONT)
    entry.pack(fill=tk.X, pady=(0, 6))

    listbox = tk.Listbox(frame, height=15, bg=INPUT_BG, fg=FG, selectbackground=FG, selectforeground=BG, activestyle='none', font=FONT)
    listbox.pack(fill=tk.BOTH, expand=True)

    def get_display_text(t):
        if isinstance(t, dict):
            title = t.get("title", "")
            prio = t.get("priority", "")
            deadline = t.get("deadline", "")
            completed = t.get("completed", False)
            disp = title
            if prio:
                disp += f"  [{prio}]"
            if deadline:
                disp += f"  (due {deadline})"
            if completed:
                disp = "✓ " + disp
            return disp
        return str(t)

    for t in tasks:
        listbox.insert(tk.END, get_display_text(t))
        
        if isinstance(t, dict) and t.get("completed"):
            idx = listbox.size() - 1
            try:
                listbox.itemconfig(idx, fg="#777777")
            except Exception:
                pass

    tk.Label(frame, text="Description:", bg=BG, fg=FG, font=FONT).pack(anchor="w", pady=(8, 0))
    desc_view = tk.Text(frame, height=6, bg=INPUT_BG, fg=FG, font=FONT, wrap=tk.WORD)
    desc_view.pack(fill=tk.X, pady=(0, 6))
    desc_view.configure(state="disabled")

    def render_task_description(t):
        if not isinstance(t, dict):
            return ""
        desc = t.get("description", "")
        meta = []
        if t.get("time_created"):
            meta.append(f"Created: {format_time_created(t['time_created'])}")
        if t.get("deadline"):
            meta.append(f"Deadline: {t['deadline']}")
        if t.get("attachment"):
            meta.append(f"Attachment: {t['attachment']}")
        if meta:
            if desc:
                desc += "\n\n"
            desc += "\n".join(meta)
        return desc

    def show_selected_description(event=None):
        sel = listbox.curselection()
        desc_view.configure(state="normal")
        desc_view.delete("1.0", tk.END)
        if not sel:
            desc_view.configure(state="disabled")
            return
        idx = sel[0]
        try:
            t = tasks[idx]
        except Exception:
            desc_view.configure(state="disabled")
            return
        desc_view.insert(tk.END, render_task_description(t))
        desc_view.configure(state="disabled")

    listbox.bind('<<ListboxSelect>>', show_selected_description)
    
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
        if not isinstance(t, dict):
            messagebox.showerror("Task Error", "Selected item is not a valid task.")
            return
        task_id = t.get("id")
        if task_id is None:
            messagebox.showerror("Task Error", "This task has no ID and cannot be updated.")
            return
        new_completed = not t.get("completed", False)
        if set_complete_api(task_id, new_completed) is None:
            return
        refresh_collections()
        show_selected_description()

    btn_frame = tk.Frame(frame, bg=BG)
    btn_frame.pack(fill=tk.X, pady=(6, 0))

    def make_button(text, cmd, side=tk.LEFT, padx=(0,0)):
        b = tk.Button(btn_frame, text=text, command=cmd, bg=BTN_BG, fg=FG, activebackground=FG, activeforeground=BG, relief='flat', font=FONT)
        b.pack(side=side, padx=padx)
        return b

    
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

    tk.Label(add_frame, text="Deadline:", bg=BG, fg=FG, font=FONT).grid(row=2, column=0, sticky="w", padx=6, pady=3)
    deadline_entry = tk.Entry(add_frame, bg=INPUT_BG, fg=FG, insertbackground=FG, font=FONT)
    deadline_entry.grid(row=2, column=1, padx=6, pady=3)

    tk.Label(add_frame, text="Description:", bg=BG, fg=FG, font=FONT).grid(row=3, column=0, sticky="nw", padx=6, pady=3)
    add_desc = tk.Text(add_frame, height=4, width=30, bg=INPUT_BG, fg=FG, font=FONT)
    add_desc.grid(row=3, column=1, padx=6, pady=3)

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
        deadline_entry.delete(0, tk.END)
        add_desc.delete("1.0", tk.END)
        save_btn_form.configure(text="Save")

    def on_form_save():
        nonlocal editing_index
        title = add_title.get().strip()
        if not title:
            messagebox.showwarning("Missing Title", "Please enter a title.")
            return
        description = add_desc.get("1.0", "end").strip()
        priority = prio_var.get()
        deadline = deadline_entry.get().strip()
        if editing_index is None:
            new_task = add_task_api(current_collection, title, description, priority, deadline, "")
            if new_task is None:
                return
            new_task = normalize_task(new_task)
            tasks.append(new_task)
            listbox.insert(tk.END, get_display_text(new_task))
            listbox.selection_clear(0, tk.END)
            last = listbox.size() - 1
            listbox.selection_set(last)
            show_selected_description()
            hide_form()
        else:
            t = tasks[editing_index]
            task_id = t.get("id")
            if task_id is None:
                messagebox.showerror("Task Error", "This task has no ID and cannot be updated.")
                return
            result = update_task_api(task_id, title=title, description=description, priority=priority, deadline=deadline)
            if result is None:
                return
            result = normalize_task(result)
            tasks[editing_index] = result
            listbox.delete(editing_index)
            listbox.insert(editing_index, get_display_text(result))
            if result.get("completed"):
                try:
                    listbox.itemconfig(editing_index, fg="#777777")
                except Exception:
                    pass
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(editing_index)
            show_selected_description()
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
            deadline_entry.delete(0, tk.END)
            deadline_entry.insert(0, t.get("deadline", ""))
            add_desc.delete("1.0", tk.END)
            add_desc.insert("1.0", t.get("description", ""))
        else:
            add_title.delete(0, tk.END)
            add_title.insert(0, str(t))
            prio_var.set("Low")
            deadline_entry.delete(0, tk.END)
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
                deadline_entry.delete(0, tk.END)
                add_desc.delete("1.0", tk.END)
            show_form()


    add_btn = make_button("Add", toggle_add_frame, side=tk.LEFT)
    edit_btn = make_button("Edit", start_edit, side=tk.LEFT, padx=(6, 0))
    save_btn_form = tk.Button(add_frame, text="Save", command=on_form_save, bg=BTN_BG, fg=FG, font=FONT)
    save_btn_form.grid(row=4, column=0, pady=6, padx=(6, 3))
    tk.Button(add_frame, text="Cancel", command=lambda: hide_form(), bg=BTN_BG, fg=FG, font=FONT).grid(row=4, column=1, pady=6, padx=(3, 6))

    def remove_and_update():
        sel = listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        task = tasks[idx]
        task_id = task.get("id") if isinstance(task, dict) else None
        if task_id is None:
            messagebox.showerror("Task Error", "This task has no ID and cannot be removed.")
            return
        if delete_task_api(task_id) is None:
            return
        refresh_collections()
        try:
            listbox.selection_clear(0, tk.END)
            if listbox.size() > 0:
                listbox.selection_set(0)
        except Exception:
            pass
        show_selected_description()

    def clear_and_update():
        if not messagebox.askyesno("Clear All", "Delete all tasks?"):
            return
        for task in list(tasks):
            task_id = task.get("id") if isinstance(task, dict) else None
            if task_id is not None:
                delete_task_api(task_id)
        refresh_collections()
        show_selected_description()

    remove_btn = make_button("Remove", remove_and_update, side=tk.LEFT, padx=(6, 0))
    complete_btn = make_button("Complete", lambda: (complete_selected(listbox, tasks), show_selected_description()), side=tk.LEFT, padx=(6, 0))
    clear_btn = make_button("Clear All", clear_and_update, side=tk.LEFT, padx=(6, 0))
    save_btn = make_button("Refresh", refresh_collections, side=tk.RIGHT)

    def on_enter(event):
        title = entry.get().strip()
        if not title:
            return
        new_task = add_task_api(current_collection, title, "", "Low", "", "")
        if new_task is None:
            return
        new_task = normalize_task(new_task)
        tasks.append(new_task)
        listbox.insert(tk.END, get_display_text(new_task))
        entry.delete(0, tk.END)
        try:
            last = listbox.size() - 1
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(last)
        except Exception:
            pass
        show_selected_description()

    entry.bind("<Return>", on_enter)

    def schedule_refresh():
        try:
            refresh_collections()
        except Exception:
            pass
        root.after(REF_RATE, schedule_refresh)
    
    schedule_refresh()
    
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()

if __name__ == "__main__":
    main()
