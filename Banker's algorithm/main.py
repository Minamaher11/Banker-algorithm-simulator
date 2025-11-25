import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

def parse_matrix(text, expected_rows=None, expected_cols=None):
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()!='']
    mat = []
    for ln in lines:
        parts = ln.split()
        row = []
        for p in parts:
            try:
                row.append(int(p))
            except:
                raise ValueError(f"Non-integer value: '{p}'")
        mat.append(row)
    if expected_rows is not None and len(mat) != expected_rows:
        raise ValueError(f"Expected {expected_rows} rows, got {len(mat)}")
    if expected_cols is not None:
        for i,r in enumerate(mat):
            if len(r) != expected_cols:
                raise ValueError(f"Row {i} expected {expected_cols} cols, got {len(r)}")
    return mat

def parse_vector(text, expected_len=None):
    parts = [p for p in text.strip().split() if p!='']
    vec = []
    for p in parts:
        try:
            vec.append(int(p))
        except:
            raise ValueError(f"Non-integer value: '{p}'")
    if expected_len is not None and len(vec) != expected_len:
        raise ValueError(f"Expected vector length {expected_len}, got {len(vec)}")
    return vec

def safety_algorithm(available, alloc, _max):
    n = len(alloc)
    m = len(available)
    need = [[_max[i][j] - alloc[i][j] for j in range(m)] for i in range(n)]
    work = available.copy()
    finish = [False]*n
    sequence = []
    changed = True
    while changed:
        changed = False
        for i in range(n):
            if not finish[i]:
                if all(need[i][j] <= work[j] for j in range(m)):
                    # can allocate
                    for j in range(m):
                        work[j] += alloc[i][j]
                    finish[i] = True
                    sequence.append(i)
                    changed = True
    safe = all(finish)
    return safe, sequence, need

def on_check():
    try:
        n = int(entry_n.get())
        m = int(entry_m.get())
        alloc = parse_matrix(text_alloc.get("1.0","end"), expected_rows=n, expected_cols=m)
        _max = parse_matrix(text_max.get("1.0","end"), expected_rows=n, expected_cols=m)
        avail = parse_vector(text_avail.get("1.0","end"), expected_len=m)
    except Exception as e:
        messagebox.showerror("Input error", str(e))
        return

    # basic validation
    for i in range(n):
        for j in range(m):
            if alloc[i][j] < 0 or _max[i][j] < 0 or avail[j] < 0:
                messagebox.showerror("Input error", "Negative numbers not allowed.")
                return
            if alloc[i][j] > _max[i][j]:
                messagebox.showerror("Input error", f"Allocation > Max at P{i}, R{j}")
                return

    safe, seq, need = safety_algorithm(avail.copy(), alloc, _max)
    out = ""
    if safe:
        out += "System is SAFE.\nSafe sequence (process indices): " + " -> ".join(f"P{p}" for p in seq) + "\n\nDetailed Need matrix:\n"
    else:
        out += "System is NOT safe (UNSAFE).\n\nDetailed Need matrix:\n"
    for i in range(n):
        out += f"P{i}: " + " ".join(str(x) for x in need[i]) + "\n"
    text_output.config(state='normal')
    text_output.delete("1.0","end")
    text_output.insert("end", out)
    text_output.config(state='disabled')

def on_request():
    """Handle a resource request: input fields: process index and request vector"""
    try:
        n = int(entry_n.get())
        m = int(entry_m.get())
        alloc = parse_matrix(text_alloc.get("1.0","end"), expected_rows=n, expected_cols=m)
        _max = parse_matrix(text_max.get("1.0","end"), expected_rows=n, expected_cols=m)
        avail = parse_vector(text_avail.get("1.0","end"), expected_len=m)
        p_index = int(entry_req_proc.get())
        req = parse_vector(entry_req_vec.get(), expected_len=m)
    except Exception as e:
        messagebox.showerror("Input error", str(e))
        return
    if p_index < 0 or p_index >= n:
        messagebox.showerror("Input error", "Process index out of range")
        return

    # compute need
    need = [_max[i][j] - alloc[i][j] for j in range(m)]

    # Check request <= need
    if any(req[j] > (_max[p_index][j] - alloc[p_index][j]) for j in range(m)):
        messagebox.showinfo("Request check", "Request exceeds the process's declared maximum need. Reject.")
        return
    # Check request <= available
    if any(req[j] > avail[j] for j in range(m)):
        messagebox.showinfo("Request check", "Not enough available resources now. Process must wait.")
        return

    # Tentatively allocate
    new_avail = avail.copy()
    new_alloc = [row.copy() for row in alloc]
    for j in range(m):
        new_avail[j] -= req[j]
        new_alloc[p_index][j] += req[j]

    safe, seq, _ = safety_algorithm(new_avail, new_alloc, _max)
    if safe:
        msg = f"After granting request, system is SAFE. Safe sequence: " + " -> ".join(f"P{s}" for s in seq)
        # Update the text areas to reflect the granted request
        text_avail.delete("1.0","end")
        text_avail.insert("end", " ".join(str(x) for x in new_avail))
        # update allocation text
        text_alloc.delete("1.0","end")
        for row in new_alloc:
            text_alloc.insert("end", " ".join(str(x) for x in row) + "\n")
    else:
        msg = "After tentative allocation, system would be UNSAFE. Request is denied."
    text_output.config(state='normal')
    text_output.delete("1.0","end")
    text_output.insert("end", msg)
    text_output.config(state='disabled')

# GUI
root = tk.Tk()
root.title("Banker's Algorithm - Checker (Python)")

frame_top = ttk.Frame(root, padding=10)
frame_top.grid(row=0, column=0, sticky="nsew")

ttk.Label(frame_top, text="Number of processes (n):").grid(row=0, column=0, sticky="w")
entry_n = ttk.Entry(frame_top, width=5); entry_n.grid(row=0, column=1, sticky="w")
entry_n.insert(0,"3")

ttk.Label(frame_top, text="Number of resource types (m):").grid(row=0, column=2, sticky="w", padx=(10,0))
entry_m = ttk.Entry(frame_top, width=5); entry_m.grid(row=0, column=3, sticky="w")
entry_m.insert(0,"3")

ttk.Label(frame_top, text="Allocation matrix (each row per process):").grid(row=1, column=0, columnspan=2, sticky="w", pady=(8,0))
text_alloc = scrolledtext.ScrolledText(frame_top, width=35, height=6)
text_alloc.grid(row=2, column=0, columnspan=2, pady=(0,8))
text_alloc.insert("end", "0 1 0\n2 0 0\n3 0 2\n")  # example

ttk.Label(frame_top, text="Max matrix:").grid(row=1, column=2, columnspan=2, sticky="w", pady=(8,0))
text_max = scrolledtext.ScrolledText(frame_top, width=35, height=6)
text_max.grid(row=2, column=2, columnspan=2, pady=(0,8))
text_max.insert("end", "7 5 3\n3 2 2\n9 0 2\n")  # example

ttk.Label(frame_top, text="Available vector:").grid(row=3, column=0, sticky="w")
text_avail = scrolledtext.ScrolledText(frame_top, width=20, height=1)
text_avail.grid(row=3, column=1, sticky="w")
text_avail.insert("end", "3 3 2")

btn_check = ttk.Button(frame_top, text="Check Safety", command=on_check)
btn_check.grid(row=3, column=2, sticky="w", padx=(10,0))

# Request area
frame_req = ttk.LabelFrame(root, text="Resource Request (simulate)", padding=10)
frame_req.grid(row=1, column=0, sticky="nsew", padx=10, pady=8)

ttk.Label(frame_req, text="Process index (0-based):").grid(row=0, column=0, sticky="w")
entry_req_proc = ttk.Entry(frame_req, width=5); entry_req_proc.grid(row=0, column=1, sticky="w")
entry_req_proc.insert(0,"1")
ttk.Label(frame_req, text="Request vector:").grid(row=0, column=2, sticky="w", padx=(10,0))
entry_req_vec = ttk.Entry(frame_req, width=25); entry_req_vec.grid(row=0, column=3, sticky="w")
entry_req_vec.insert(0,"1 0 2")

btn_req = ttk.Button(frame_req, text="Submit Request", command=on_request)
btn_req.grid(row=0, column=4, padx=(10,0))

# Output log
frame_out = ttk.LabelFrame(root, text="Output", padding=10)
frame_out.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0,10))
text_output = scrolledtext.ScrolledText(frame_out, width=85, height=12, state='disabled')
text_output.grid(row=0, column=0)

root.mainloop()
