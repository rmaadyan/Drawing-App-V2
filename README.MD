Fitur Aplikasi:
Mode Menggambar:

Titik: Klik untuk membuat titik
Garis: Klik dan drag untuk membuat garis
Persegi: Klik dan drag untuk membuat persegi
Lingkaran: Klik dan drag untuk membuat lingkaran
Titik Sambung: Klik beberapa kali, tekan Enter untuk menyimpan
Ellipse: Klik dan drag untuk membuat ellipse
Pemilihan Warna:

7 pilihan warna: Hitam, Merah, Hijau, Biru, Kuning, Ungu, Cyan
Tombol Clear:

Menghapus semua gambar
Cara Penggunaan:
Pilih mode menggambar dengan mengklik tombol mode
Pilih warna dengan mengklik kotak warna
Gambar di area putih dengan mouse
Untuk titik sambung, klik beberapa titik lalu tekan Enter
Klik "Clear" untuk menghapus semua gambar
Aplikasi ini sudah siap untuk diupload ke itch.io dan dapat langsung dimainkan di browser!

Cara Menjalankan di itch.io:

Install Pygbag:
pip install pygbag

Buat struktur folder:
scss
my-drawing-app/
├── main.py (kode di atas)
└── index.html (opsional)

Build untuk web:
cd my-drawing-app
python -m pygbag main.py

Upload ke itch.io:
Pygbag akan membuat folder build/web
Zip semua file dalam folder web
Upload zip file ke itch.io sebagai HTML5 game

Fitur-Fitur Baru:
1. Menggambar Objek
✅ Titik (Point)
✅ Garis (Line)
✅ Persegi (Rectangle)
✅ Lingkaran (Circle)
✅ Ellipse

2. Pemilihan Warna
10 pilihan warna dengan tampilan yang lebih menarik
Tombol warna dengan efek shadow dan highlight saat dipilih

3. Pengaturan Ketebalan
Slider interaktif untuk mengatur ketebalan garis (1-10 px)
Preview ketebalan yang real-time
Nilai ketebalan ditampilkan di samping slider

4. Transformasi Objek
Select: Pilih objek dengan klik mouse
Move (Translasi): Geser objek yang dipilih
Rotate (Rotasi): Putar objek berdasarkan gerakan mouse horizontal
Scale (Scaling): Perbesar/perkecil objek

5. Koordinat Mouse
Input koordinat menggunakan mouse (click and drag)
Tampilan koordinat X,Y real-time di pojok kanan bawah panel

Perbaikan Tampilan GUI:

1. Layout yang Lebih Terorganisir
Panel atas dengan background yang lebih soft
Pembagian section yang jelas (Drawing Tools, Transform Tools, Colors, Thickness)
Rounded corners pada tombol dan panel

2. Visual Feedback
Efek hover pada tombol
Highlight untuk tombol aktif
Shadow effect pada tombol warna
Grid background pada canvas untuk membantu penggambaran

3. Fitur Tambahan UI
Tombol "Undo" untuk membatalkan gambar terakhir
Tombol "Clear All" untuk menghapus semua gambar
Tooltip saat hover di tombol transformasi
Indikator visual saat objek dipilih (bounding box biru)

4. Ikon Visual
Ikon sederhana untuk setiap tool menggambar
Tampilan yang lebih intuitif

Cara Penggunaan:
Menggambar: Pilih tool gambar, pilih warna dan ketebalan, lalu klik dan drag di canvas
Memilih Objek: Klik tombol "Select" lalu klik pada objek yang ingin dipilih
Transformasi:
Pilih objek terlebih dahulu
Pilih jenis transformasi (Move/Rotate/Scale)
Klik dan drag untuk melakukan transformasi
Mengubah Warna/Ketebalan: Pilih sebelum menggambar objek baru
Aplikasi ini sekarang memiliki tampilan yang lebih professional dan user-friendly dengan fitur-fitur yang lengkap untuk aplikasi menggambar 2D sederhana.