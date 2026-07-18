// script.js - interaktivitas ringan untuk CFG Pantun Validator

document.addEventListener("DOMContentLoaded", function () {
  // Set tahun berjalan di footer
  var yearEl = document.getElementById("thisYear");
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  // Tombol "Gunakan Contoh Pantun" pada halaman validasi
  var btnContoh = document.getElementById("btnContoh");
  var textarea = document.getElementById("pantun_text");
  if (btnContoh && textarea) {
    btnContoh.addEventListener("click", function () {
      textarea.value = btnContoh.dataset.contoh;
      textarea.focus();
    });
  }

  // Tombol Reset
  var btnReset = document.getElementById("btnReset");
  if (btnReset && textarea) {
    btnReset.addEventListener("click", function () {
      textarea.value = "";
      textarea.focus();
    });
  }

  // Hitung otomatis jumlah baris & kata secara live (bantuan visual saja,
  // validasi sesungguhnya tetap dilakukan oleh parser di server / backend)
  var liveInfo = document.getElementById("liveInfo");
  if (textarea && liveInfo) {
    var updateLiveInfo = function () {
      var lines = textarea.value.split("\n").filter(function (l) {
        return l.trim() !== "";
      });
      var totalBaris = lines.length;
      var infoWords = lines
        .map(function (l, idx) {
          var jumlah = l.trim().split(/\s+/).filter(Boolean).length;
          return "Baris " + (idx + 1) + ": " + jumlah + " kata";
        })
        .join(" &middot; ");
      liveInfo.innerHTML =
        "<strong>" + totalBaris + "</strong> baris terdeteksi. " + infoWords;
    };
    textarea.addEventListener("input", updateLiveInfo);
    updateLiveInfo();
  }

  // Konfirmasi sebelum menghapus riwayat
  var formHapus = document.getElementById("formHapusRiwayat");
  if (formHapus) {
    formHapus.addEventListener("submit", function (e) {
      if (!confirm("Yakin ingin menghapus seluruh riwayat validasi?")) {
        e.preventDefault();
      }
    });
  }
});
