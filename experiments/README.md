# experiments — mengukur kontribusi tiap temuan terhadap angka Tabel 2

Harness ini menjawab satu pertanyaan: **seberapa besar tiap cacat A1–A4 menyumbang
pada hasil yang dilaporkan di Tabel 2 manuskrip?**

MATLAB/Octave tidak tersedia di mesin tempat audit ini dikerjakan, jadi
`kma_py/kma.py` adalah **port Python yang setia** dari `kma/KMA2D.m`. Seluruh
pilihan struktural dipertahankan apa adanya — inisialisasi di sudut
(`PopConsInitialization`), 40 micro-swarm pada tahap dua, `MutRadius = 0.5`,
ambang improve/stagnasi `> 2`, `MutRadius` ganda di `Reposition`, penambahan
`FolHQ` di luar `if`, dan seterusnya. Hanya empat cacat berikut yang bisa
di-toggle, sehingga setiap selisih antar konfigurasi murni berasal dari cacat
yang di-toggle:

| Flag | Temuan |
|---|---|
| `fix_case14` | **A1** `case 16` → `case 14` untuk Foxholes |
| `fix_allhq` | **A2** indeks baris `AllHQ`/`AllHQFX` tahap dua |
| `fix_mlipir` | **A3** presedensi operator pada kecepatan mlipir, Eq. (8) |
| `fix_evalcount` | **A4** anggaran 25.000 dibebankan pada panggilan objektif nyata |

`kma_py/benchmarks.py` memuat 23 fungsi benchmark hasil terjemahan 1:1 dari
`Evaluation.m` + `GetFunction.m`, sudah diverifikasi terhadap optimum yang
tercantum di Tabel 6 manuskrip. Modul itu menyediakan dua dispatcher: yang benar,
dan yang mereproduksi `switch` versi terbit (F14 tanpa case, F16 menjalankan
Foxholes) untuk mengukur A1.

## Menjalankan

```bash
cd experiments
python3 run_experiments.py --seeds 30 --dim 50 --jobs 11
```

Butuh `numpy`. Hasil ditulis ke `results/raw.csv` (satu baris per run) dan
`results/summary.md` (tabel ringkas).

Tujuh konfigurasi dijalankan: `published` (semua cacat aktif), tiap perbaikan
tunggal (`fix_A1` … `fix_A4`), `fix_A2+A3` (kedua jalur bias origin ditutup
tetapi anggaran evaluasi dibiarkan seperti aslinya), dan `all_fixed`.

## Membaca hasilnya

Metrik utama adalah `true_best`: nilai **fungsi objektif yang benar** pada solusi
yang dikembalikan. Ini penting untuk F16 — pada konfigurasi `published` kode
sebenarnya mengoptimalkan Foxholes, sehingga `reported_best` tidak sebanding
dengan angka Tabel 2. Kolom `reported_best` tetap disimpan di `raw.csv`.

`counted_evals` adalah `NumEva` seperti dihitung kode terbit; `real_evals` adalah
jumlah panggilan fungsi objektif yang sebenarnya. Selisih keduanya adalah temuan
A4.

Analisis lengkap ada di `../TEMUAN.md`.
