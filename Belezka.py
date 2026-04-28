import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys


class Beleznica:
    def __init__(self, root):
        self.root = root
        self.filename = None
        self.kodiranje = "utf-8"
        self.spreminjanje_v_teku = False
        self.prikazi_stevilke_vrstic = tk.BooleanVar(value=True)

        self.root.geometry("1000x700")
        self.root.minsize(600, 400)

        self.ustvari_vmesnik()
        self.ustvari_meni()
        self.povezi_bljiznjice()

        self.posodobi_naslov()
        self.posodobi_status()
        self.posodobi_stevilke_vrstic()

        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def ustvari_vmesnik(self):
        glavni_okvir = tk.Frame(self.root)
        glavni_okvir.pack(expand=True, fill="both")

        vsebinski_okvir = tk.Frame(glavni_okvir)
        vsebinski_okvir.pack(expand=True, fill="both")

        self.scrollbar_y = tk.Scrollbar(vsebinski_okvir, orient="vertical")
        self.scrollbar_y.pack(side="right", fill="y")

        self.scrollbar_x = tk.Scrollbar(glavni_okvir, orient="horizontal")
        self.scrollbar_x.pack(side="bottom", fill="x")

        self.stevilke_vrstic = tk.Text(
            vsebinski_okvir,
            width=4,
            padx=2,
            takefocus=0,
            border=0,
            state="disabled",
            wrap="none",
            background="#f0f0f0",
            foreground="black"
        )
        self.stevilke_vrstic.pack(side="left", fill="y")

        self.text_area = tk.Text(
            vsebinski_okvir,
            undo=True,
            wrap="none",
            yscrollcommand=self.on_textscroll,
            xscrollcommand=self.scrollbar_x.set
        )
        self.text_area.pack(side="left", expand=True, fill="both")

        self.scrollbar_y.config(command=self.on_scrollbar_y)
        self.scrollbar_x.config(command=self.text_area.xview)

        self.status_label = tk.Label(
            self.root,
            text="Vrstica 1, Stolpec 1 | Kodiranje: UTF-8",
            anchor="e",
            relief="sunken"
        )
        self.status_label.pack(side="bottom", fill="x")

        self.text_area.bind("<<Modified>>", self.on_modified)
        self.text_area.bind("<KeyRelease>", self.on_cursor_move)
        self.text_area.bind("<ButtonRelease-1>", self.on_cursor_move)
        self.text_area.bind("<MouseWheel>", self.on_mousewheel)
        self.text_area.bind("<Configure>", self.on_cursor_move)

    def ustvari_meni(self):
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        meni_datoteka = tk.Menu(self.menu, tearoff=0)
        meni_datoteka.add_command(label="Nova", command=self.new_file, accelerator="Ctrl+N")
        meni_datoteka.add_command(label="Odpri", command=self.open_file, accelerator="Ctrl+O")
        meni_datoteka.add_command(label="Shrani", command=self.save_file, accelerator="Ctrl+S")
        meni_datoteka.add_command(label="Shrani kot", command=self.save_as, accelerator="Ctrl+Shift+S")
        meni_datoteka.add_separator()
        meni_datoteka.add_command(label="Izhod", command=self.exit_app)
        self.menu.add_cascade(label="Datoteka", menu=meni_datoteka)

        meni_uredi = tk.Menu(self.menu, tearoff=0)
        meni_uredi.add_command(label="Razveljavi", command=self.undo, accelerator="Ctrl+Z")
        meni_uredi.add_command(label="Ponovi", command=self.redo, accelerator="Ctrl+Y")
        meni_uredi.add_separator()
        meni_uredi.add_command(label="Izreži", command=lambda: self.text_area.event_generate("<<Cut>>"), accelerator="Ctrl+X")
        meni_uredi.add_command(label="Kopiraj", command=lambda: self.text_area.event_generate("<<Copy>>"), accelerator="Ctrl+C")
        meni_uredi.add_command(label="Prilepi", command=lambda: self.text_area.event_generate("<<Paste>>"), accelerator="Ctrl+V")
        meni_uredi.add_separator()
        meni_uredi.add_command(label="Izberi vse", command=self.select_all, accelerator="Ctrl+A")
        self.menu.add_cascade(label="Uredi", menu=meni_uredi)

        meni_pogled = tk.Menu(self.menu, tearoff=0)
        meni_pogled.add_checkbutton(
            label="Prikaži številke vrstic",
            variable=self.prikazi_stevilke_vrstic,
            command=self.preklopi_stevilke_vrstic
        )
        self.menu.add_cascade(label="Pogled", menu=meni_pogled)

        meni_pomoc = tk.Menu(self.menu, tearoff=0)
        meni_pomoc.add_command(label="O programu", command=self.show_about)
        self.menu.add_cascade(label="Pomoč", menu=meni_pomoc)

    def povezi_bljiznjice(self):
        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-S>", lambda event: self.save_as())
        self.root.bind("<Control-a>", lambda event: self.select_all())
        self.root.bind("<Control-z>", lambda event: self.undo())
        self.root.bind("<Control-y>", lambda event: self.redo())

    def on_textscroll(self, *args):
        self.scrollbar_y.set(*args)
        self.stevilke_vrstic.yview_moveto(args[0])

    def on_scrollbar_y(self, *args):
        self.text_area.yview(*args)
        self.stevilke_vrstic.yview(*args)

    def on_mousewheel(self, event=None):
        self.root.after_idle(self.posodobi_stevilke_vrstic)

    def preklopi_stevilke_vrstic(self):
        if self.prikazi_stevilke_vrstic.get():
            self.stevilke_vrstic.pack(side="left", fill="y", before=self.text_area)
            self.posodobi_stevilke_vrstic()
        else:
            self.stevilke_vrstic.pack_forget()

    def posodobi_naslov(self):
        ime = os.path.basename(self.filename) if self.filename else "Neimenovano"
        oznaka = "*" if self.text_area.edit_modified() else ""
        self.root.title(f"{oznaka}{ime} - Beležka")

    def posodobi_status(self):
        indeks = self.text_area.index("insert")
        vrstica, stolpec = indeks.split(".")
        prikaz_kodiranja = "ANSI" if self.kodiranje.lower() == "cp1250" else "UTF-8"
        self.status_label.config(
            text=f"Vrstica {vrstica}, Stolpec {int(stolpec) + 1} | Kodiranje: {prikaz_kodiranja}"
        )

    def posodobi_stevilke_vrstic(self):
        if not self.prikazi_stevilke_vrstic.get():
            return

        zadnja_vrstica = int(self.text_area.index("end-1c").split(".")[0])
        vsebina = "\n".join(str(i) for i in range(1, zadnja_vrstica + 1))

        self.stevilke_vrstic.config(state="normal")
        self.stevilke_vrstic.delete("1.0", tk.END)
        self.stevilke_vrstic.insert("1.0", vsebina)
        self.stevilke_vrstic.config(state="disabled")

        self.stevilke_vrstic.yview_moveto(self.text_area.yview()[0])

    def on_cursor_move(self, event=None):
        self.posodobi_status()
        self.posodobi_stevilke_vrstic()

    def on_modified(self, event=None):
        if self.spreminjanje_v_teku:
            return

        self.spreminjanje_v_teku = True
        self.posodobi_naslov()
        self.posodobi_status()
        self.posodobi_stevilke_vrstic()
        self.text_area.edit_modified(self.text_area.edit_modified())
        self.spreminjanje_v_teku = False

    def izberi_kodiranje(self):
        okno = tk.Toplevel(self.root)
        okno.title("Izbira kodiranja")
        okno.resizable(False, False)
        okno.transient(self.root)
        okno.grab_set()

        rezultat = {"kodiranje": None}

        tk.Label(okno, text="Izberi kodiranje za shranjevanje:", padx=20, pady=15).pack()

        gumbi = tk.Frame(okno)
        gumbi.pack(pady=(0, 15))

        def izberi_utf8():
            rezultat["kodiranje"] = "utf-8"
            okno.destroy()

        def izberi_ansi():
            rezultat["kodiranje"] = "cp1250"
            okno.destroy()

        tk.Button(gumbi, text="UTF-8", width=12, command=izberi_utf8).pack(side="left", padx=8)
        tk.Button(gumbi, text="ANSI", width=12, command=izberi_ansi).pack(side="left", padx=8)

        self.root.wait_window(okno)
        return rezultat["kodiranje"]

    def new_file(self):
        if self.confirm_save():
            self.text_area.delete("1.0", tk.END)
            self.filename = None
            self.kodiranje = "utf-8"
            self.text_area.edit_modified(False)
            self.posodobi_naslov()
            self.posodobi_status()
            self.posodobi_stevilke_vrstic()

    def open_file(self):
        if not self.confirm_save():
            return

        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Besedilne datoteke", "*.txt"), ("Vse datoteke", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                vsebina = file.read()
            self.kodiranje = "utf-8"
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="cp1250") as file:
                    vsebina = file.read()
                self.kodiranje = "cp1250"
            except Exception as e:
                messagebox.showerror("Napaka", f"Pri odpiranju datoteke je prišlo do napake:\n{e}")
                return
        except Exception as e:
            messagebox.showerror("Napaka", f"Pri odpiranju datoteke je prišlo do napake:\n{e}")
            return

        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", vsebina)
        self.filename = file_path
        self.text_area.edit_modified(False)
        self.posodobi_naslov()
        self.posodobi_status()
        self.posodobi_stevilke_vrstic()

    def save_file(self):
        if not self.filename:
            return self.save_as()

        try:
            vsebina = self.text_area.get("1.0", "end-1c")
            with open(self.filename, "w", encoding=self.kodiranje) as file:
                file.write(vsebina)

            self.text_area.edit_modified(False)
            self.posodobi_naslov()
            self.posodobi_status()
            return True

        except Exception as e:
            messagebox.showerror("Napaka", f"Pri shranjevanju datoteke je prišlo do napake:\n{e}")
            return False

    def save_as(self):
        file_path = filedialog.asksaveasfilename(
            initialfile="Neimenovano.txt",
            defaultextension=".txt",
            filetypes=[("Besedilne datoteke", "*.txt"), ("Vse datoteke", "*.*")]
        )

        if not file_path:
            return False

        izbrano_kodiranje = self.izberi_kodiranje()
        if izbrano_kodiranje is None:
            return False

        self.filename = file_path
        self.kodiranje = izbrano_kodiranje
        return self.save_file()

    def confirm_save(self):
        if not self.text_area.edit_modified():
            return True

        response = messagebox.askyesnocancel(
            "Shrani spremembe",
            "Ali želite pred nadaljevanjem shraniti spremembe?"
        )

        if response is None:
            return False

        if response:
            if self.filename:
                return self.save_file()
            return self.save_as()

        return True

    def exit_app(self):
        if self.confirm_save():
            self.root.destroy()

    def select_all(self):
        self.text_area.tag_add("sel", "1.0", "end-1c")
        self.text_area.mark_set("insert", "1.0")
        self.text_area.see("insert")
        return "break"

    def undo(self):
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        try:
            self.text_area.edit_redo()
        except tk.TclError:
            pass

    def show_about(self):
        messagebox.showinfo(
            "O programu",
            "Beležka\nNarejeno v Pythonu s Tkinterjem."
        )

    def odpri_datoteko_iz_argumenta(self, file_to_open):
        if not os.path.exists(file_to_open):
            messagebox.showerror("Napaka", "Podana datoteka ne obstaja.")
            return

        try:
            with open(file_to_open, "r", encoding="utf-8") as file:
                vsebina = file.read()
            self.kodiranje = "utf-8"
        except UnicodeDecodeError:
            try:
                with open(file_to_open, "r", encoding="cp1250") as file:
                    vsebina = file.read()
                self.kodiranje = "cp1250"
            except Exception as e:
                messagebox.showerror("Napaka", f"Pri odpiranju datoteke je prišlo do napake:\n{e}")
                return
        except Exception as e:
            messagebox.showerror("Napaka", f"Pri odpiranju datoteke je prišlo do napake:\n{e}")
            return

        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", vsebina)
        self.filename = file_to_open
        self.text_area.edit_modified(False)
        self.posodobi_naslov()
        self.posodobi_status()
        self.posodobi_stevilke_vrstic()


if __name__ == "__main__":
    root = tk.Tk()
    app = Beleznica(root)

    if len(sys.argv) > 1:
        app.odpri_datoteko_iz_argumenta(sys.argv[1])

    root.mainloop()
