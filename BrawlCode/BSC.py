import sys
import tkinter as tk
from tkinter import messagebox, ttk

class LongToCodeConverter:
    CONVERSION_CHARS = "0289PYLQGRJCUV"
    HASH_TAG = "#"
    TEAM_CONVERSION_CHARS = "QWERTYUPASDFGHJKLZCVBNM23456789"
    TEAM_TAG = "X"
    
    def __init__(self, is_team_converter=False):
        self.conversion_chars = self.TEAM_CONVERSION_CHARS if is_team_converter else self.CONVERSION_CHARS
        self.code_suffix = self.TEAM_TAG if is_team_converter else self.HASH_TAG

    def to_code(self, high_int, low_int):
        if high_int < 256:
            l = self.to_long(low_int >> 24, high_int | (low_int << 8))
            res = self.convert(l)
            return self.code_suffix + res
        else:
            print("Higher int value too large", file=sys.stderr)
            return None

    def generate_neighbor_codes(self, code, count):
        base_id = self.to_id(code)
        if base_id == -1:
            return

        print("\nPrevious codes:")
        for i in range(base_id - count, base_id):
            if i >= 0:
                parts = self.extract_high_low(i)
                gen_code = self.to_code(parts[0], parts[1])
                if gen_code:
                    print(gen_code)

        print("\nThe following codes:")
        for i in range(base_id + 1, base_id + count + 1):
            parts = self.extract_high_low(i)
            gen_code = self.to_code(parts[0], parts[1])
            if gen_code:
                print(gen_code)

    def extract_high_low(self, value):
        low = value & 0xFFFFFFFF
        high = value >> 32
        return [high, low]

    def convert(self, id):
        tag = []
        length = len(self.conversion_chars)
        while id > 0:
            char_index = id % length
            tag.insert(0, self.conversion_chars[char_index])
            id //= length
        return ''.join(tag)

    def to_id(self, code):
        if not code.startswith(self.code_suffix):
            print(f"Invalid prefix. Expected: {self.code_suffix}", file=sys.stderr)
            return -1

        if len(code) < 14:
            code_substring = code[1:]

            if not code_substring:
                v13 = 0
                lo_int = int(v13 & 0x7FFFFFFF)
                hi_int = 0
            else:
                unk6 = 0
                unk7 = 0

                for i in range(len(code_substring)):
                    sub_str = code_substring[i]
                    sub_str_idx = self.conversion_chars.find(sub_str)
                    if sub_str_idx == -1:
                        print("Invalid character in code", file=sys.stderr)
                        return -1

                    unk12 = unk6 * len(self.conversion_chars) + sub_str_idx
                    unk7 = (self.to_long_s(unk7, unk6) * len(self.conversion_chars) + sub_str_idx) >> 32
                    unk6 = unk12

                if (unk12 & unk7) != -1:
                    v13 = self.to_long_s(unk7, unk12) >> 8
                    lo_int = int(v13 & 0x7FFFFFFF)
                    hi_int = unk6 & 0xFF
                    return self.to_long(hi_int, lo_int)
                hi_int = -1
                lo_int = -1
            return self.to_long(hi_int, lo_int)
        else:
            print("Code too long", file=sys.stderr)
            return -1

    def to_long(self, hi_int, lo_int):
        return (hi_int << 32) | (lo_int & 0xFFFFFFFF)

    def to_long_s(self, hi_int, lo_int):
        return (hi_int << 32) | lo_int

class LongToCodeGUI(tk.Tk):
    def __init__(self, converter):
        super().__init__()
        self.converter = converter
        self.title("Code converter")
        self.geometry("500x400")
        
        self.create_widgets()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        self.mode_var = tk.StringVar(value="1")
        mode_frame = ttk.LabelFrame(self, text="variant")
        mode_frame.pack(pady=10, padx=10, fill="x")
        
        modes = [
            ("Code in ID", "1"),
            ("ID in code", "2"),
            ("neighboring codes", "3")
        ]
        
        for text, mode in modes:
            ttk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.mode_var,
                value=mode,
                command=self.toggle_fields
            ).pack(side="left", padx=5, pady=5)

        self.code_frame = ttk.Frame(self)
        self.code_frame.pack(pady=10, padx=10, fill="x")
        
        ttk.Label(self.code_frame, text="Code:").pack(side="left")
        self.code_entry = ttk.Entry(self.code_frame, width=30)
        self.code_entry.pack(side="left", padx=5)

        self.id_frame = ttk.Frame(self)
        self.id_frame.pack(pady=10, padx=10, fill="x")
        
        ttk.Label(self.id_frame, text="ID:").pack(side="left")
        self.id_entry = ttk.Entry(self.id_frame, width=30)
        self.id_entry.pack(side="left", padx=5)

        self.result_frame = ttk.LabelFrame(self, text="result")
        self.result_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.result_text = tk.Text(self.result_frame, height=10)
        self.result_text.pack(padx=5, pady=5, fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(self.result_text)
        scrollbar.pack(side="right", fill="y")
        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_text.yview)

        self.neighbor_count_frame = ttk.Frame(self)
        self.neighbor_count_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(self.neighbor_count_frame, text="Number of adjacent codes:").pack(side="left")
        
        neighbor_values = [i for i in range(10, 501, 10)]  # Values from 10 to 150 with step of 10
        self.neighbor_count_var = tk.IntVar(value=20)      # Default value is set to 20
        
        neighbor_dropdown = ttk.Combobox(
            self.neighbor_count_frame,
            textvariable=self.neighbor_count_var,
            values=neighbor_values,
            state="readonly"
        )
        
        neighbor_dropdown.pack(side="left", padx=5)

        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(side="bottom", pady=10)

        ttk.Button(self.button_frame, text="enter", command=self.execute).pack(side="left", padx=5)
        ttk.Button(self.button_frame, text="clear", command=self.clear_results).pack(side="left", padx=5)

        self.toggle_fields()

    def toggle_fields(self):
        mode = self.mode_var.get()
        if mode == "1":
            self.code_frame.pack()
            self.id_frame.pack_forget()
            self.neighbor_count_frame.pack_forget()
        elif mode == "2":
            self.id_frame.pack()
            self.code_frame.pack_forget()
            self.neighbor_count_frame.pack_forget()
        elif mode == "3":
            self.code_frame.pack()
            self.id_frame.pack_forget()
            self.neighbor_count_frame.pack()

    def execute(self):
        self.result_text.delete(1.0, tk.END)
        mode = self.mode_var.get()
        
        try:
            if mode == "1":
                code = self.code_entry.get()
                result = self.converter.to_id(code)
                if result != -1:
                    self.result_text.insert(tk.END, f"ID: {result}")
            elif mode == "2":
                try:
                    id_val = int(self.id_entry.get())
                    parts = self.converter.extract_high_low(id_val)
                    code = self.converter.to_code(parts[0], parts[1])
                    if code:
                        self.result_text.insert(tk.END, f"Код: {code}")
                except ValueError:
                    messagebox.showerror("error", "incorrect ID")
            elif mode == "3":
                code = self.code_entry.get()
                neighbor_count = self.neighbor_count_var.get()
                import io
                from contextlib import redirect_stdout
                
                f = io.StringIO()
                with redirect_stdout(f):
                    self.converter.generate_neighbor_codes(code, neighbor_count)
                self.result_text.insert(tk.END, f.getvalue())
        except Exception as e:
            messagebox.showerror("error", str(e))

    def clear_results(self):
        self.result_text.delete(1.0, tk.END)

if __name__ == "__main__":
    converter = LongToCodeConverter(is_team_converter=True)
    app = LongToCodeGUI(converter)
    app.mainloop()
