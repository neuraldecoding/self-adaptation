# self-adaptation

Mekanisme self-adaptation asli pada **Komodo Mlipir Algorithm (KMA)** — beserta
audit kesesuaian antara manuskrip yang diterbitkan dan kode pendampingnya.

Repositori ini memuat dua hal yang saling terkait:

- **Objek studi**: KMA v1.0.0 (MATLAB), khususnya self-adaptation ukuran populasi
  pada tahap kedua evolusi.
- **Hasil audit**: pemeriksaan apakah kode di `kma/` benar-benar melakukan apa
  yang ditulis di manuskrip. Jawabannya: **tidak sepenuhnya**. Ditemukan 4 cacat
  perangkat lunak, 12 penyimpangan kode terhadap manuskrip, 7 kesalahan di dalam
  manuskrip sendiri, dan beberapa masalah minor.

Laporan lengkap: **[TEMUAN.md](TEMUAN.md)**.

## Sumber

| | |
|---|---|
| Manuskrip | S. Suyanto, A.A. Ariyanto, A.F. Ariyanto, *Komodo Mlipir Algorithm*, **Applied Soft Computing 114 (2022) 108043**. [doi:10.1016/j.asoc.2021.108043](https://doi.org/10.1016/j.asoc.2021.108043) — salinan di `manuscript/` |
| Kode | KMA v1.0.0, MATLAB R2017a, rilis 23 November 2021 — salinan **tanpa modifikasi** di `kma/` |

---

## Ringkasan temuan

### Cacat perangkat lunak

| Kode | Lokasi | Inti masalah |
|---|---|---|
| **A1** | `kma/Evaluation.m:101` | Blok Foxholes diberi label `case 16`, padahal Foxholes adalah **F14**. Karena MATLAB mengeksekusi *case* pertama yang cocok, **F14 error** (`fx` tak pernah di-assign) dan **F16 diam-diam mengoptimalkan Foxholes**, bukan Six Hump Camel. |
| **A2** | `kma/KMA2D.m:174-175`<br>`kma/KMA3D.m:222-223` | Indeks baris `AllHQ` memakai indeks `Pop`. Array tumbuh dari 80 menjadi 197 baris, ~70 di antaranya **vektor nol berfitness 0** yang kemudian dipakai sebagai individu *high-quality*. Cacat ini berada tepat di dalam mekanisme self-adaptation tahap dua. |
| **A3** | `kma/KMA2D.m:484`, `:534`<br>`kma/KMA3D.m:538`, `:588` | Presedensi operator: baris itu dievaluasi sebagai `rand.*(HQ.*B) − (SM.*B)`, bukan `rand.*((HQ−SM).*B)` seperti Eq. (8). Efeknya **kontraksi menuju titik nol koordinat**, bukan langkah menuju big male. |
| **A4** | `kma/KMA2D.m:70`, `:181` | `NumEva` dinaikkan per generasi, bukan per evaluasi. Anggaran 25.000 terlampaui **13–29%**, dan 200 evaluasi (populasi awal + `ConsPop`) tidak terhitung sama sekali. |

**A2 dan A3 adalah dua jalur terpisah menuju bias yang sama.** Memperbaiki salah
satu saja tidak menghilangkan bias origin — jalur yang lain masih terbuka.

### Penyimpangan dan kesalahan lain

- **B1–B12** — kode tidak melakukan apa yang ditulis paper. Terbesar: inisialisasi
  populasi di **4 sudut** ruang pencarian (paper menulis "created randomly"), dan
  struktur **40 micro-swarm** pada tahap dua yang sama sekali tidak dideskripsikan.
- **C1–C7** — kesalahan di dalam manuskrip. Termasuk Eq. (1) `q = ⌊(p−1)n⌋` yang
  bernilai negatif, Eq. (2) yang lupa mengurangi satu female, dan §2.8 (`α = 0.1`)
  yang bertentangan dengan §4 ("mutation radius of 0.5").
- **D1–D4** — masalah minor.

---

## Hasil utama

### Angka andalan manuskrip bergantung pada bias origin

Guaranty diukur langsung di Octave dengan sumber MATLAB asli, 30 run per sel:

| | `kma/` (versi terbit) | `kma-fixed/` (A1–A4 diperbaiki) |
|---|---|---|
| Guaranty F1–F13 | **7/13 = 53,85%** | **0/13 = 0%** |

Angka 53,85% itu persis yang diklaim §3.4 manuskrip untuk mengunggulkan KMA di
atas SMA (23,08%), MPA dan EO (15,38%). Angka itu menjadi **0%** begitu kedua
jalur bias origin ditutup.

### Baseline mereproduksi Tabel 2 — kecuali F14 dan F16

30 run per sel, dimensi 50, GNU Octave 10.3:

| Func | `kma/` Avg (Std) | Tabel 2 | `kma-fixed/` Avg (Std) |
|---|---|---|---|
| F1–F4, F6, F9, F11 | **0 (0)** | 0 (0) | 1,5–681 (gagal total) |
| F7 Quartic | 2,212e-04 (1,49e-04) | 1,715e-04 (1,19e-04) | 7,239e-03 (7,67e-03) |
| F8 Schwefel | −1,641e+04 (2,16e+03) | −1,701e+04 (2,45e+03) | −1,491e+04 (1,34e+03) |
| F12 Penalized | 2,105e-03 (2,80e-03) | 2,799e-03 (1,82e-03) | 1,091e-01 (2,30e-01) |
| F17 Branin | 3,9794e-01 (3,64e-05) | 3,979e-01 (3,51e-05) | 3,9795e-01 (2,81e-05) |
| F22 Shekel 7 | −10,4029 (1,18e-05) | −10,4029 (1,01e-05) | −10,4029 (1,02e-05) |
| **F14 Foxholes** | **error di 30/30 run** | 9,980e-01 (4,38e-16) | 9,980e-01 (0) |
| **F16 Six Hump Camel** | **12,671 (0)** | −1,032 (9,78e-06) | −1,0316 (8,68e-06) |

Cocok pada **21 dari 23 fungsi**, Avg maupun Std — F17, F22, dan F23 bahkan cocok
pada Std-nya. MFE juga cocok sampai orde satuan: F6 median **55,0** vs 55,83; F9
median **150,0** vs 150,5; F11 median **175,0** vs 169,83. Kecocokan sedetail itu
praktis menutup kemungkinan kebetulan — kode di `kma/` memang kode yang
menghasilkan Tabel 2–5, yang membuat pengecualian F14 dan F16 semakin tegas.

### F5 melacak nilai fungsi di titik origin

Rosenbrock bernilai tepat `Dim − 1` di titik nol:

| Dim | f_Rosenbrock(0) | KMA Avg (Tabel 2–5) | rasio |
|---|---|---|---|
| 50 | 49 | 48,31 | 0,986 |
| 100 | 99 | 95,30 | 0,963 |
| 500 | 499 | 471,5 | 0,945 |
| 1000 | 999 | 961,7 | 0,963 |

Penjelasan §4 manuskrip ("KMA terjebak stagnasi karena area datar F5") tidak
didukung: solusinya tertarik ke titik nol, dan Rosenbrock kebetulan bernilai
`Dim − 1` di sana.

### Yang tetap sah

**F15 dan F17–F23 tidak terpengaruh cacat mana pun.** `kma/` dan `kma-fixed/`
memberi hasil praktis identik — F18 dan F21 sama-sama eksak, F22 dan F23 sama
sampai enam angka penting. Optimum fungsi-fungsi itu jauh dari origin dan ruang
pencariannya kecil, sehingga bias origin tidak membantu maupun merugikan. Bagian
fixed-dimension multimodal pada Tabel 2 sah apa adanya.

Gambaran akhirnya terpisah rapi menjadi tiga kelompok:

- **F1–F13** — bergantung penuh pada bias origin (A2+A3).
- **F14, F16** — rusak karena A1; angka di Tabel 2 tidak dapat dihasilkan kode ini.
- **F15, F17–F23** — sah apa adanya.

---

## Isi repositori

```
manuscript/     komodomelipiralgorithm.pdf — paper Applied Soft Computing 114 (2022) 108043
kma/            KMA v1.0.0 asli, TIDAK DISENTUH. Baseline untuk semua perbandingan.
kma-fixed/      Salinan dengan perbaikan minimal A1-A4 saja. Tiap perubahan ditandai
                komentar "FIX Ax". Diff lengkap di A1-A4.patch. Penyimpangan B1-B12
                sengaja dibiarkan agar efek A1-A4 terisolasi.
experiments/
  octave/       Menjalankan sumber MATLAB apa adanya di GNU Octave.
                run_one.m           satu run headless
                sweep.sh            sweep kma/ vs kma-fixed/, paralel
                summarize.py        ringkasan bergaya Tabel 2
                allhq_index_demo.m  replay pengindeksan AllHQ (temuan A2)
                random.m            shim Octave untuk random('Normal',...)
  kma_py/       Port Python yang setia dari KMA2D.m dengan A1-A4 bisa di-toggle,
                plus 23 fungsi benchmark yang sudah diverifikasi terhadap Tabel 6.
  results/      octave_verification.txt  1.380 run Octave (23 fungsi x 30 seed x 2 versi)
                octave_summary.md        ringkasan Avg (Std), MFE, Guaranty
                raw.csv                  4.830 run Python (23 fungsi x 7 konfigurasi x 30 seed)
                summary.md               ringkasan per konfigurasi
TEMUAN.md       Laporan audit lengkap: A1-A4, B1-B12, C1-C7, D1-D4, hasil, batasan.
```

### Kenapa dua jalur eksperimen

| | Octave | Python |
|---|---|---|
| Yang dijalankan | sumber MATLAB **asli**, tanpa modifikasi | port yang setia, A1–A4 bisa di-toggle |
| Kekuatan | membuktikan perilaku kode yang sebenarnya | memisahkan kontribusi **tiap** cacat |
| Skala | 1.380 run (~35 menit) | 4.830 run, 7 konfigurasi |

Octave menjawab "apakah kode ini benar-benar berperilaku begitu"; Python menjawab
"cacat yang mana yang menyebabkannya". Keduanya saling memeriksa: prediksi port
Python tentang 197 baris `AllHQ` dengan 69 baris nol terkonfirmasi persis di
Octave, begitu pula Guaranty 53,85% → 0%.

---

## Reproduksi

### Menjalankan kode MATLAB

`Main2D.m`/`Main3D.m` memanggil `KMA2D`/`KMA3D` dengan nama yang sama di kedua
folder, jadi **hanya satu** yang boleh ada di path pada satu waktu:

```matlab
cd kma          % baseline asli
% atau: cd kma-fixed
Main2D
```

### Verifikasi dengan GNU Octave (tanpa root)

```bash
mkdir -p ~/.local/micromamba && cd ~/.local/micromamba
curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj bin/micromamba
export MAMBA_ROOT_PREFIX=~/.local/micromamba
./bin/micromamba create -y -n oct -c conda-forge octave
```

Jalankan selalu lewat `micromamba run` — tanpa itu `OCTAVE_HOME` tidak terpasang
dan Octave tidak menemukan pustaka m-file bawaannya.

```bash
cd experiments/octave
SEEDS=30 JOBS=10 ./sweep.sh > ../results/octave_verification.txt   # ~35 menit
python3 summarize.py ../results/octave_verification.txt > ../results/octave_summary.md
```

Menghapusnya cukup `rm -rf ~/.local/micromamba`. Detail: `experiments/octave/README.md`.

### Eksperimen Python

```bash
cd experiments
python3 run_experiments.py --seeds 30 --dim 50 --jobs 11    # butuh numpy
```

Detail: `experiments/README.md`.

---

## Status dan batasan verifikasi

- Temuan statis (label `case`, indeks array, presedensi operator, perbandingan
  rumus) diverifikasi lewat **pembacaan kode**.
- Perilaku diverifikasi lewat **eksekusi langsung di GNU Octave 10.3.0** —
  1.380 run, seluruh 23 fungsi, 30 seed.
- Kontribusi tiap cacat dipisahkan lewat **port Python** — 4.830 run, 7 konfigurasi.

Yang belum:

- **Belum dijalankan di MATLAB R2017a.** Satu ketergantungan diganti untuk
  verifikasi Octave: `levy.m` memanggil `random('Normal',…)` dari Statistics
  Toolbox, yang disediakan lewat shim `experiments/octave/random.m`
  (`mu + sigma.*randn`, ekuivalen persis). **Shim itu tidak boleh diletakkan di
  path MATLAB.** Jalankan sekali di MATLAB sebelum dipakai untuk publikasi.
- **Skalabilitas Tabel 3–5** (dimensi 100/500/1000) tidak direplikasi, kecuali
  perbandingan `f_Rosenbrock(0)` yang dihitung analitik.
- **F20 Hartman 6** adalah satu-satunya fungsi di luar F14/F16 yang tidak cocok:
  baseline memberi Std 2,93e-02 (28 dari 30 run mencapai optimum) sementara
  Tabel 2 melaporkan 3,17e-04.
- `kma-fixed/` **bukan** "algoritma paper yang dikerjakan dengan benar". Itu kode
  terbit dengan empat cacat dihapus; seluruh penyimpangan B1–B12 masih ada di
  dalamnya — terutama B1, inisialisasi di sudut — dan sebagian selisih yang
  terlihat berasal dari sana.

---

## Lisensi dan atribusi

- `kma/` dan `kma-fixed/` adalah karya **Suyanto Suyanto (Telkom University)**,
  dilisensikan **BSD 3-Clause** — lihat `kma/license.txt`. Lisensi itu tetap
  berlaku untuk kedua folder, termasuk salinan yang sudah dipatch.
- `manuscript/` adalah artikel akses terbuka Elsevier di bawah **CC BY-NC-ND 4.0**.
- Sisa repositori (audit, harness eksperimen, dokumentasi) di bawah **GPL-3.0**,
  lihat `LICENSE`.
