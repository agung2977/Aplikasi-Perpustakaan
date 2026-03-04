import os
import sqlite3
import platform
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

DB_FILE = 'library.db'

class LibraryDB:
    def __init__(self, db_file=DB_FILE):
        self.conn = sqlite3.connect(db_file)
        self._create_table()

    def _create_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            year INTEGER,
            isbn TEXT,
            cover_path TEXT,
            video_path TEXT
        )
        '''
        self.conn.execute(sql)
        self.conn.commit()

    def add_book(self, title, author, year, isbn, cover_path, video_path):
        sql = 'INSERT INTO books (title,author,year,isbn,cover_path,video_path) VALUES (?,?,?,?,?,?)'
        cur = self.conn.execute(sql, (title, author, year, isbn, cover_path, video_path))
        self.conn.commit()
        return cur.lastrowid

    def update_book(self, book_id, title, author, year, isbn, cover_path, video_path):
        sql = 'UPDATE books SET title=?,author=?,year=?,isbn=?,cover_path=?,video_path=? WHERE id=?'
        self.conn.execute(sql, (title, author, year, isbn, cover_path, video_path, book_id))
        self.conn.commit()

    def delete_book(self, book_id):
        sql = 'DELETE FROM books WHERE id=?'
        self.conn.execute(sql, (book_id,))
        self.conn.commit()

    def search(self, title='', author='', year='', isbn=''):
        sql = 'SELECT * FROM books WHERE title LIKE ? AND author LIKE ? AND (year LIKE ? OR ?="") AND isbn LIKE ?'
        params = (f'%{title}%', f'%{author}%', f'%{year}%', year, f'%{isbn}%')
        cur = self.conn.execute(sql, params)
        return cur.fetchall()

    def list_all(self):
        cur = self.conn.execute('SELECT * FROM books ORDER BY id DESC')
        return cur.fetchall()

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Aplikasi Perpustakaan - Demo')
        self.db = LibraryDB()
        self.selected_book_id = None
        self.cover_image = None
        self._build_ui()
        self._populate_list()

    def _build_ui(self):
        frm = tk.Frame(self.root)
        frm.pack(padx=10, pady=10, fill='both', expand=True)

        # Left: form
        left = tk.Frame(frm)
        left.grid(row=0, column=0, sticky='nw')

        tk.Label(left, text='Judul').grid(row=0, column=0, sticky='w')
        self.e_title = tk.Entry(left, width=40)
        self.e_title.grid(row=0, column=1, pady=2)

        tk.Label(left, text='Pengarang').grid(row=1, column=0, sticky='w')
        self.e_author = tk.Entry(left, width=40)
        self.e_author.grid(row=1, column=1, pady=2)

        tk.Label(left, text='Tahun').grid(row=2, column=0, sticky='w')
        self.e_year = tk.Entry(left, width=15)
        self.e_year.grid(row=2, column=1, sticky='w', pady=2)

        tk.Label(left, text='ISBN').grid(row=3, column=0, sticky='w')
        self.e_isbn = tk.Entry(left, width=25)
        self.e_isbn.grid(row=3, column=1, sticky='w', pady=2)

        # cover & video path
        tk.Label(left, text='Cover (gambar)').grid(row=4, column=0, sticky='w')
        self.e_cover = tk.Entry(left, width=35)
        self.e_cover.grid(row=4, column=1, sticky='w')
        tk.Button(left, text='Pilih...', command=self._pick_cover).grid(row=4, column=2, padx=4)

        tk.Label(left, text='Video (opsional)').grid(row=5, column=0, sticky='w')
        self.e_video = tk.Entry(left, width=35)
        self.e_video.grid(row=5, column=1, sticky='w')
        tk.Button(left, text='Pilih...', command=self._pick_video).grid(row=5, column=2, padx=4)

        # action buttons
        btn_frame = tk.Frame(left)
        btn_frame.grid(row=6, column=0, columnspan=3, pady=8)
        tk.Button(btn_frame, text='Tambah', width=10, command=self._add_book).grid(row=0, column=0, padx=4)
        tk.Button(btn_frame, text='Update', width=10, command=self._update_book).grid(row=0, column=1, padx=4)
        tk.Button(btn_frame, text='Hapus', width=10, command=self._delete_book).grid(row=0, column=2, padx=4)
        tk.Button(btn_frame, text='Clear', width=8, command=self._clear_form).grid(row=0, column=3, padx=4)

        # Middle: list
        mid = tk.Frame(frm)
        mid.grid(row=0, column=1, padx=12, sticky='n')
        tk.Label(mid, text='Daftar Buku').pack(anchor='w')
        self.lb_books = tk.Listbox(mid, width=60, height=16)
        self.lb_books.pack()
        self.lb_books.bind('<<ListboxSelect>>', self._on_list_select)

        # search
        searchfrm = tk.Frame(mid)
        searchfrm.pack(pady=6, anchor='w')
        tk.Label(searchfrm, text='Cari Judul').grid(row=0, column=0)
        self.e_search = tk.Entry(searchfrm, width=25)
        self.e_search.grid(row=0, column=1, padx=6)
        tk.Button(searchfrm, text='Cari', command=self._search).grid(row=0, column=2)
        tk.Button(searchfrm, text='Tampilkan Semua', command=self._populate_list).grid(row=0, column=3, padx=6)

        # Right: preview
        right = tk.Frame(frm)
        right.grid(row=0, column=2, sticky='n')
        tk.Label(right, text='Preview Cover').pack()
        self.lbl_cover = tk.Label(right, text='(tidak ada gambar)', width=25, height=12, relief='groove')
        self.lbl_cover.pack(pady=6)
        tk.Button(right, text='Buka Cover', command=self._open_cover).pack(fill='x')
        tk.Button(right, text='Play Video', command=self._play_video).pack(fill='x', pady=4)

    def _pick_cover(self):
        path = filedialog.askopenfilename(title='Pilih gambar cover', filetypes=[('Image files','*.png;*.jpg;*.jpeg;*.gif;*.bmp'), ('All files','*.*')])
        if path:
            self.e_cover.delete(0, tk.END)
            self.e_cover.insert(0, path)
            self._show_cover(path)

    def _pick_video(self):
        path = filedialog.askopenfilename(title='Pilih file video', filetypes=[('Video files','*.mp4;*.mkv;*.avi;*.mov;*.wmv'), ('All files','*.*')])
        if path:
            self.e_video.delete(0, tk.END)
            self.e_video.insert(0, path)

    def _add_book(self):
        title = self.e_title.get().strip()
        if not title:
            messagebox.showwarning('Peringatan', 'Judul wajib diisi')
            return
        author = self.e_author.get().strip()
        year = self.e_year.get().strip()
        isbn = self.e_isbn.get().strip()
        cover = self.e_cover.get().strip()
        video = self.e_video.get().strip()
        self.db.add_book(title, author, year if year else None, isbn, cover, video)
        messagebox.showinfo('Sukses', 'Buku ditambahkan')
        self._populate_list()
        self._clear_form()

    def _update_book(self):
        if not self.selected_book_id:
            messagebox.showwarning('Peringatan', 'Pilih buku terlebih dahulu')
            return
        title = self.e_title.get().strip()
        if not title:
            messagebox.showwarning('Peringatan', 'Judul wajib diisi')
            return
        author = self.e_author.get().strip()
        year = self.e_year.get().strip()
        isbn = self.e_isbn.get().strip()
        cover = self.e_cover.get().strip()
        video = self.e_video.get().strip()
        self.db.update_book(self.selected_book_id, title, author, year if year else None, isbn, cover, video)
        messagebox.showinfo('Sukses', 'Data buku diperbarui')
        self._populate_list()

    def _delete_book(self):
        if not self.selected_book_id:
            messagebox.showwarning('Peringatan', 'Pilih buku terlebih dahulu')
            return
        if messagebox.askyesno('Konfirmasi', 'Hapus buku ini?'):
            self.db.delete_book(self.selected_book_id)
            messagebox.showinfo('Sukses', 'Buku dihapus')
            self._populate_list()
            self._clear_form()

    def _clear_form(self):
        self.selected_book_id = None
        self.e_title.delete(0, tk.END)
        self.e_author.delete(0, tk.END)
        self.e_year.delete(0, tk.END)
        self.e_isbn.delete(0, tk.END)
        self.e_cover.delete(0, tk.END)
        self.e_video.delete(0, tk.END)
        self.lbl_cover.config(image='', text='(tidak ada gambar)')
        self.cover_image = None

    def _populate_list(self):
        self.lb_books.delete(0, tk.END)
        for row in self.db.list_all():
            row_text = f"{row[0]} | {row[1]} — {row[2]} ({row[3]})"
            self.lb_books.insert(tk.END, row_text)

    def _on_list_select(self, event):
        sel = event.widget.curselection()
        if not sel:
            return
        idx = sel[0]
        text = self.lb_books.get(idx)
        # parse id from start
        book_id = int(text.split('|')[0].strip())
        # fetch full record
        cur = self.db.conn.execute('SELECT * FROM books WHERE id=?', (book_id,))
        row = cur.fetchone()
        if row:
            self.selected_book_id = row[0]
            self.e_title.delete(0, tk.END); self.e_title.insert(0, row[1])
            self.e_author.delete(0, tk.END); self.e_author.insert(0, row[2] or '')
            self.e_year.delete(0, tk.END); self.e_year.insert(0, row[3] or '')
            self.e_isbn.delete(0, tk.END); self.e_isbn.insert(0, row[4] or '')
            self.e_cover.delete(0, tk.END); self.e_cover.insert(0, row[5] or '')
            self.e_video.delete(0, tk.END); self.e_video.insert(0, row[6] or '')
            if row[5]:
                self._show_cover(row[5])
            else:
                self.lbl_cover.config(image='', text='(tidak ada gambar)')

    def _search(self):
        q = self.e_search.get().strip()
        results = self.db.search(title=q)
        self.lb_books.delete(0, tk.END)
        for row in results:
            row_text = f"{row[0]} | {row[1]} — {row[2]} ({row[3]})"
            self.lb_books.insert(tk.END, row_text)

    def _show_cover(self, path):
        if not os.path.exists(path):
            self.lbl_cover.config(image='', text='(file tidak ditemukan)')
            return
        if not PIL_AVAILABLE:
            self.lbl_cover.config(text='(Pillow tidak terpasang)')
            return
        try:
            img = Image.open(path)
            img.thumbnail((200, 280))
            self.cover_image = ImageTk.PhotoImage(img)
            self.lbl_cover.config(image=self.cover_image, text='')
        except Exception as e:
            print('Error show cover:', e)
            self.lbl_cover.config(image='', text='(gagal menampilkan)')

    def _open_cover(self):
        path = self.e_cover.get().strip()
        if not path:
            messagebox.showwarning('Peringatan', 'Tidak ada path cover')
            return
        if not os.path.exists(path):
            messagebox.showerror('Error', 'File cover tidak ditemukan')
            return
        self._open_file_with_os(path)

    def _play_video(self):
        path = self.e_video.get().strip()
        if not path:
            messagebox.showwarning('Peringatan', 'Tidak ada file video')
            return
        if not os.path.exists(path):
            messagebox.showerror('Error', 'File video tidak ditemukan')
            return
        self._open_file_with_os(path)

    def _open_file_with_os(self, path):
        try:
            if platform.system() == 'Windows':
                os.startfile(path)
            elif platform.system() == 'Darwin':
                subprocess.call(['open', path])
            else:
                subprocess.call(['xdg-open', path])
        except Exception as e:
            messagebox.showerror('Error', f'Gagal membuka file: {e}')

if __name__ == '__main__':
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()
