# cfg_parser.py
# ============================================================
# Recursive Descent Parser (Top-Down Parser)
# ------------------------------------------------------------
# Catatan penamaan: file ini SENGAJA tidak diberi nama "parser.py"
# karena Python memiliki modul internal bawaan bernama "parser"
# (stdlib, deprecated) yang dapat menimbulkan konflik import pada
# beberapa versi Python (mis. Python 3.9). Nama "cfg_parser.py"
# dipakai untuk menghindari bentrok tersebut.
#
# Mengimplementasikan CFG yang didefinisikan pada grammar.py
# TANPA menggunakan regex sebagai metode utama validasi.
# Regex (jika ada) hanya dipakai untuk tokenisasi ringan, bukan
# untuk menentukan valid/tidaknya struktur pantun.
#
# Struktur parser mengikuti pola turunan langsung dari grammar:
#
#   parse_pantun()    -> Pantun    -> Sampiran Isi
#   parse_sampiran()  -> Sampiran  -> Baris Baris
#   parse_isi()       -> Isi       -> Baris Baris
#   parse_baris()     -> Baris     -> Kalimat
#   parse_kalimat()   -> Kalimat   -> Kata Kalimat | Kata
#
# Setiap fungsi mengembalikan sebuah "node" hasil parsing beserta
# jejak (trace) aturan produksi yang digunakan, sehingga proses
# parsing dapat ditampilkan secara transparan ke pengguna.
# ============================================================

from grammar import (
    JUMLAH_BARIS_PANTUN,
    MIN_KATA_PER_BARIS,
    MAX_KATA_PER_BARIS,
)


class ParseError(Exception):
    """Exception khusus untuk kegagalan parsing pada suatu tahap CFG."""

    def __init__(self, message, baris_ke=None):
        self.message = message
        self.baris_ke = baris_ke
        super().__init__(message)


class PantunParser:
    """
    Recursive Descent Parser untuk struktur Pantun.

    Cara pakai:
        parser = PantunParser(teks_pantun)
        hasil = parser.parse()
        # hasil adalah dict berisi status, trace, detail baris, dsb.
    """

    def __init__(self, teks_pantun: str):
        self.teks_asli = teks_pantun
        # Tokenisasi baris: split berdasarkan newline, buang baris kosong
        # di ujung tapi pertahankan baris kosong di tengah agar terdeteksi
        # sebagai error struktural.
        baris_mentah = teks_pantun.strip("\n").split("\n")
        self.baris_list = [b.strip() for b in baris_mentah]
        self.trace = []          # jejak aturan produksi yang dipakai
        self.detail_baris = []   # detail tiap baris (jumlah kata, dll)
        self.errors = []         # daftar alasan penolakan (bisa lebih dari 1)

    # ------------------------------------------------------------
    # Utilitas kecil untuk mencatat langkah parsing (derivation step)
    # ------------------------------------------------------------
    def _log(self, rule_id, rule_text, keterangan):
        self.trace.append({
            "id": rule_id,
            "rule": rule_text,
            "keterangan": keterangan,
        })

    # ------------------------------------------------------------
    # Kata -> [token]
    # ------------------------------------------------------------
    def _tokenize_kata(self, baris: str):
        """Memecah satu baris menjadi daftar token Kata (berbasis spasi)."""
        if baris is None:
            return []
        tokens = [t for t in baris.strip().split(" ") if t != ""]
        return tokens

    # ------------------------------------------------------------
    # Kalimat -> Kata Kalimat | Kata   (basis rekursi eksplisit)
    # ------------------------------------------------------------
    def parse_kalimat(self, tokens, posisi_baris):
        """
        Menurunkan Kalimat secara rekursif: Kata diikuti Kalimat, atau
        berhenti pada satu Kata. Fungsi ini secara eksplisit meniru
        rekursi pada grammar (bukan sekadar len(tokens)).
        """
        if len(tokens) == 0:
            raise ParseError(
                f"Baris {posisi_baris} kosong: Kalimat harus memuat "
                f"minimal satu Kata.",
                baris_ke=posisi_baris,
            )

        if len(tokens) == 1:
            # Basis rekursi: Kalimat -> Kata
            return {"kata": tokens[0], "sisa": None}

        # Kalimat -> Kata Kalimat (rekursif turun ke sisa token)
        kata_pertama = tokens[0]
        sisa_kalimat = self.parse_kalimat(tokens[1:], posisi_baris)
        return {"kata": kata_pertama, "sisa": sisa_kalimat}

    # ------------------------------------------------------------
    # Baris -> Kalimat
    # ------------------------------------------------------------
    def parse_baris(self, teks_baris, posisi_baris, peran):
        """
        Menurunkan satu Baris -> Kalimat, sekaligus memeriksa
        batasan semantik jumlah kata (4-12).
        peran: "Sampiran" atau "Isi", hanya untuk keperluan pelaporan.
        """
        tokens = self._tokenize_kata(teks_baris)
        jumlah_kata = len(tokens)

        detail = {
            "baris_ke": posisi_baris,
            "peran": peran,
            "teks": teks_baris,
            "jumlah_kata": jumlah_kata,
            "tokens": tokens,
            "valid_jumlah_kata": MIN_KATA_PER_BARIS <= jumlah_kata <= MAX_KATA_PER_BARIS,
        }

        # Turunkan Kalimat (akan melempar ParseError jika token kosong)
        try:
            pohon_kalimat = self.parse_kalimat(tokens, posisi_baris)
            detail["berhasil_diturunkan"] = True
        except ParseError as e:
            detail["berhasil_diturunkan"] = False
            self.detail_baris.append(detail)
            self.errors.append(str(e))
            return detail

        if not detail["valid_jumlah_kata"]:
            alasan = (
                f"Baris {posisi_baris} ({peran}) memiliki {jumlah_kata} kata, "
                f"tidak memenuhi aturan {MIN_KATA_PER_BARIS}-{MAX_KATA_PER_BARIS} "
                f"kata per baris."
            )
            self.errors.append(alasan)

        self.detail_baris.append(detail)
        return detail

    # ------------------------------------------------------------
    # Sampiran -> Baris Baris
    # ------------------------------------------------------------
    def parse_sampiran(self, baris1, baris2):
        self._log("R2", "Sampiran -> Baris Baris",
                   "Menurunkan Sampiran menjadi baris ke-1 dan ke-2.")
        b1 = self.parse_baris(baris1, 1, "Sampiran")
        self._log("R4/R5", "Baris -> Kalimat -> Kata Kalimat | Kata",
                   f"Baris 1 diturunkan menjadi {b1['jumlah_kata']} token Kata.")
        b2 = self.parse_baris(baris2, 2, "Sampiran")
        self._log("R4/R5", "Baris -> Kalimat -> Kata Kalimat | Kata",
                   f"Baris 2 diturunkan menjadi {b2['jumlah_kata']} token Kata.")
        return [b1, b2]

    # ------------------------------------------------------------
    # Isi -> Baris Baris
    # ------------------------------------------------------------
    def parse_isi(self, baris3, baris4):
        self._log("R3", "Isi -> Baris Baris",
                   "Menurunkan Isi menjadi baris ke-3 dan ke-4.")
        b3 = self.parse_baris(baris3, 3, "Isi")
        self._log("R4/R5", "Baris -> Kalimat -> Kata Kalimat | Kata",
                   f"Baris 3 diturunkan menjadi {b3['jumlah_kata']} token Kata.")
        b4 = self.parse_baris(baris4, 4, "Isi")
        self._log("R4/R5", "Baris -> Kalimat -> Kata Kalimat | Kata",
                   f"Baris 4 diturunkan menjadi {b4['jumlah_kata']} token Kata.")
        return [b3, b4]

    # ------------------------------------------------------------
    # Pantun -> Sampiran Isi   (simbol awal / start symbol)
    # ------------------------------------------------------------
    def parse(self):
        """
        Titik masuk utama parser. Mengembalikan dict hasil validasi
        yang siap ditampilkan / disimpan ke database.
        """
        self._log("R1", "Pantun -> Sampiran Isi",
                   "Mulai penurunan dari simbol awal (start symbol) Pantun.")

        jumlah_baris = len(self.baris_list)
        if jumlah_baris != JUMLAH_BARIS_PANTUN:
            self.errors.append(
                f"Jumlah baris pantun adalah {jumlah_baris}, "
                f"tetapi aturan CFG mensyaratkan tepat "
                f"{JUMLAH_BARIS_PANTUN} baris (Pantun -> Sampiran Isi, "
                f"masing-masing 2 baris)."
            )
            # Tetap coba proses baris yang tersedia agar detail tetap informatif,
            # tapi batasi agar index tidak error.
            baris_pad = (self.baris_list + [""] * JUMLAH_BARIS_PANTUN)[:JUMLAH_BARIS_PANTUN]
        else:
            baris_pad = self.baris_list

        sampiran = self.parse_sampiran(baris_pad[0], baris_pad[1])
        isi = self.parse_isi(baris_pad[2], baris_pad[3])

        valid = len(self.errors) == 0

        return {
            "valid": valid,
            "jumlah_baris": jumlah_baris,
            "detail_baris": self.detail_baris,
            "trace": self.trace,
            "errors": self.errors,
            "sampiran": sampiran,
            "isi": isi,
        }


def validasi_pantun(teks_pantun: str) -> dict:
    """Fungsi pembungkus (wrapper) sederhana untuk dipanggil dari app.py."""
    parser = PantunParser(teks_pantun)
    return parser.parse()