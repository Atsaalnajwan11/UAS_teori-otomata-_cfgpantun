# grammar.py
# ============================================================
# Definisi Context-Free Grammar (CFG) untuk Validasi Pantun
# ------------------------------------------------------------
# File ini HANYA berisi definisi grammar (aturan produksi),
# dipisahkan dari parser.py agar mudah dikembangkan / diubah
# tanpa menyentuh logika parsing.
#
# Grammar formal (BNF-like):
#
#   Pantun    -> Sampiran Isi
#   Sampiran  -> Baris Baris
#   Isi       -> Baris Baris
#   Baris     -> Kalimat
#   Kalimat   -> Kata Kalimat | Kata
#   Kata      -> <token alfanumerik apa pun, minimal 1 karakter>
#
# Batasan semantik tambahan (constraint, bukan bagian produksi
# bebas konteks murni, tetapi diperiksa oleh parser sebagai
# "attribute grammar" / semantic action):
#
#   4 <= jumlah_kata(Baris) <= 12
#   jumlah_baris(Pantun) == 4
#
# ============================================================

# Jumlah baris yang wajib ada dalam satu pantun
JUMLAH_BARIS_PANTUN = 4

# Batas jumlah kata per baris (Kalimat)
MIN_KATA_PER_BARIS = 4
MAX_KATA_PER_BARIS = 12

# Representasi aturan produksi CFG (untuk ditampilkan ke pengguna
# di halaman "Grammar CFG" dan dipakai sebagai referensi oleh parser)
PRODUKSI_CFG = [
    {
        "id": "R1",
        "rule": "Pantun -> Sampiran Isi",
        "keterangan": "Sebuah pantun tersusun atas Sampiran diikuti Isi."
    },
    {
        "id": "R2",
        "rule": "Sampiran -> Baris Baris",
        "keterangan": "Sampiran terdiri dari baris ke-1 dan baris ke-2."
    },
    {
        "id": "R3",
        "rule": "Isi -> Baris Baris",
        "keterangan": "Isi terdiri dari baris ke-3 dan baris ke-4."
    },
    {
        "id": "R4",
        "rule": "Baris -> Kalimat",
        "keterangan": "Setiap baris adalah satu Kalimat (rangkaian kata)."
    },
    {
        "id": "R5",
        "rule": "Kalimat -> Kata Kalimat | Kata",
        "keterangan": "Kalimat didefinisikan secara rekursif: satu Kata "
                       "diikuti Kalimat lain, atau berhenti pada satu Kata "
                       "(basis rekursi)."
    },
    {
        "id": "R6",
        "rule": "Kata -> [a-zA-Z0-9'\\-]+",
        "keterangan": "Kata adalah token dasar (terminal) hasil tokenisasi "
                       "baris berdasarkan spasi."
    },
]

# Aturan semantik tambahan (ditampilkan sebagai bagian dari halaman grammar)
ATURAN_SEMANTIK = [
    f"Jumlah baris pada satu Pantun harus tepat {JUMLAH_BARIS_PANTUN} baris.",
    f"Jumlah kata pada setiap Baris harus berada pada rentang "
    f"{MIN_KATA_PER_BARIS} - {MAX_KATA_PER_BARIS} kata.",
    "Baris ke-1 dan ke-2 berperan sebagai Sampiran.",
    "Baris ke-3 dan ke-4 berperan sebagai Isi.",
    "Baris tidak boleh kosong (whitespace saja dianggap tidak valid).",
]


def get_grammar_text():
    """Mengembalikan representasi grammar dalam bentuk teks BNF sederhana."""
    return "\n".join(item["rule"] for item in PRODUKSI_CFG)
