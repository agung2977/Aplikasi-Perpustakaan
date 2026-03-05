# Aplikasi-Perpustakaan

Program di atas adalah aplikasi manajemen perpustakaan sederhana berbasis GUI menggunakan Python dengan bantuan modul tkinter untuk tampilan, sqlite3 untuk database, serta Pillow (PIL) untuk menampilkan gambar cover buku.

Secara umum, aplikasi ini menyimpan data buku ke dalam database SQLite bernama library.db. Di dalamnya terdapat tabel books yang memiliki kolom: id, title, author, year, isbn, cover_path, dan video_path. Class LibraryDB bertugas mengelola database, seperti membuat tabel otomatis jika belum ada, menambahkan buku (add_book), memperbarui data (update_book), menghapus buku (delete_book), mencari buku (search), dan menampilkan semua data (list_all).

Class LibraryApp bertugas mengelola tampilan dan interaksi pengguna. Aplikasi dibagi menjadi tiga bagian utama:

- Form Input (kiri)
Pengguna dapat mengisi Judul, Pengarang, Tahun, ISBN, memilih gambar cover, dan memilih file video. Tersedia tombol Tambah, Update, Hapus, dan Clear untuk mengelola data.

- Daftar Buku (tengah)
Menampilkan semua buku dalam bentuk Listbox. Saat salah satu data diklik, detail buku otomatis muncul kembali di form untuk diedit atau dihapus. Tersedia fitur pencarian berdasarkan judul.

- Preview Cover (kanan)
Jika buku memiliki gambar cover dan modul Pillow terpasang, gambar akan ditampilkan dalam ukuran yang sudah diperkecil. Tersedia tombol untuk membuka file cover atau memutar video menggunakan aplikasi bawaan sistem operasi (Windows, macOS, atau Linux).

Alur kerja aplikasi:
- Saat tombol Tambah ditekan, data dari form disimpan ke database.
- Saat memilih buku di daftar, data akan ditampilkan kembali di form.
- Tombol Update memperbarui data buku yang dipilih.
- Tombol Hapus menghapus buku dari database setelah konfirmasi.
- Tombol Cari menampilkan hasil pencarian sesuai judul yang dimasukkan.
- Tombol Buka Cover dan Play Video membuka file menggunakan program default sistem operasi.

Secara konsep, aplikasi ini sudah menerapkan:
- CRUD (Create, Read, Update, Delete)
- Database lokal menggunakan SQLite
- GUI interaktif
- Integrasi file multimedia (gambar dan video)
- Cross-platform file opening

Jika digunakan sebagai bahan presentasi atau proyek pembelajaran, aplikasi ini sudah termasuk kategori Project Integrasi Python + Database + GUI + Multimedia, sangat cocok untuk praktik siswa bidang Informatika atau pengembangan aplikasi desktop sederhana.
