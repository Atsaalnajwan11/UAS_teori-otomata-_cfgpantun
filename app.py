# app.py
# ============================================================
# Aplikasi Flask: Implementasi Context-Free Grammar (CFG)
# untuk Validasi Struktur Pantun Berbasis Web
#
# UAS Teori Bahasa dan Otomata
# ============================================================

import os
import sqlite3
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from grammar import PRODUKSI_CFG, ATURAN_SEMANTIK, get_grammar_text
from cfg_parser import validasi_pantun

# ------------------------------------------------------------
# Konfigurasi Aplikasi
# ------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cfg-pantun-secret-key-uas-tbo")

CONTOH_PANTUN = """Jalan-jalan ke kota Blitar
Jangan lupa membeli sukun
Rajin-rajinlah kamu semua belajar
Supaya jadi anak yang santun"""


# ------------------------------------------------------------
# Database helper (SQLite murni, tanpa ORM agar ringan & jelas)
# ------------------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Membuat tabel riwayat_validasi jika belum ada."""
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS riwayat_validasi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isi_pantun TEXT NOT NULL,
            status TEXT NOT NULL,
            jumlah_baris INTEGER,
            alasan TEXT,
            tanggal_validasi TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def simpan_riwayat(isi_pantun, status, jumlah_baris, alasan):
    conn = get_db_connection()
    conn.execute(
        """INSERT INTO riwayat_validasi
           (isi_pantun, status, jumlah_baris, alasan, tanggal_validasi)
           VALUES (?, ?, ?, ?, ?)""",
        (
            isi_pantun,
            status,
            jumlah_baris,
            alasan,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    conn.close()


def ambil_riwayat(limit=100):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM riwayat_validasi ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return rows


def hapus_riwayat():
    conn = get_db_connection()
    conn.execute("DELETE FROM riwayat_validasi")
    conn.commit()
    conn.close()


# ------------------------------------------------------------
# Routes
# ------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", active_page="home")


@app.route("/validate", methods=["GET", "POST"])
def validate():
    hasil = None
    teks_input = ""

    if request.method == "POST":
        teks_input = request.form.get("pantun_text", "")

        if teks_input.strip() == "":
            flash("Teks pantun tidak boleh kosong.", "warning")
            return render_template(
                "validate.html",
                active_page="validate",
                contoh=CONTOH_PANTUN,
                hasil=None,
                teks_input=teks_input,
            )

        # Panggil Recursive Descent Parser (implementasi CFG)
        hasil = validasi_pantun(teks_input)

        status_text = "Valid" if hasil["valid"] else "Invalid"
        alasan_text = (
            "Pantun memenuhi seluruh aturan CFG."
            if hasil["valid"]
            else " | ".join(hasil["errors"])
        )

        # Simpan ke database riwayat
        simpan_riwayat(
            isi_pantun=teks_input,
            status=status_text,
            jumlah_baris=hasil["jumlah_baris"],
            alasan=alasan_text,
        )

    return render_template(
        "validate.html",
        active_page="validate",
        contoh=CONTOH_PANTUN,
        hasil=hasil,
        teks_input=teks_input,
    )


@app.route("/api/validate", methods=["POST"])
def api_validate():
    """Endpoint JSON opsional (mis. untuk keperluan AJAX / integrasi)."""
    data = request.get_json(silent=True) or {}
    teks = data.get("pantun_text", "")
    if teks.strip() == "":
        return jsonify({"error": "Teks pantun kosong."}), 400
    hasil = validasi_pantun(teks)
    return jsonify(hasil)


@app.route("/grammar")
def grammar_page():
    return render_template(
        "grammar.html",
        active_page="grammar",
        produksi=PRODUKSI_CFG,
        aturan_semantik=ATURAN_SEMANTIK,
        grammar_text=get_grammar_text(),
    )


@app.route("/history")
def history():
    rows = ambil_riwayat()
    return render_template("history.html", active_page="history", riwayat=rows)


@app.route("/history/clear", methods=["POST"])
def history_clear():
    hapus_riwayat()
    flash("Riwayat validasi berhasil dihapus.", "success")
    return redirect(url_for("history"))


@app.route("/about")
def about():
    return render_template("about.html", active_page="about")


# ------------------------------------------------------------
# Inisialisasi database saat modul di-load (aman untuk Gunicorn)
# ------------------------------------------------------------
init_db()


if __name__ == "__main__":
    # Mode pengembangan lokal
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
