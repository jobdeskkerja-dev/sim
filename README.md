---
title: SIPRES - Dashboard Kehadiran Siswa
emoji: 📊
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
---

# SIPRES — Dashboard Kehadiran Siswa SMKN 4 OKU

Dashboard analitik kehadiran dan kedisiplinan siswa untuk Guru BK dan Wali Kelas.

## Fitur
- Import data absensi Excel (.xlsx)
- Ringkasan jumlah siswa, alpa, keterlambatan, dan sanksi
- Rekomendasi status Aman / SP 1 / SP 2
- Grafik distribusi status dan jenis pelanggaran
- Tabel peringatan dini dan detail siswa

## Format kolom Excel wajib
`NIS`, `Nama`, `Kelas`, `Alpa`, `Menit_Terlambat`, `Jumlah_Sanksi`

## Menambahkan logo
Unggah file logo (PNG/JPG) ke root Space dengan nama yang mengandung kata `logo`, misalnya `logo-smkn4oku.png`.
