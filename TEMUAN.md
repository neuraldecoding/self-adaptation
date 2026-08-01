# TEMUAN — Audit Komodo Mlipir Algorithm (KMA) v1.0.0

Dokumen ini mencatat hasil pemeriksaan kesesuaian antara:

- **Manuskrip**: `manuscript/komodomelipiralgorithm.pdf` — S. Suyanto, A.A. Ariyanto,
  A.F. Ariyanto, *Komodo Mlipir Algorithm*, Applied Soft Computing 114 (2022) 108043.
- **Kode**: `kma/` — KMA v1.0.0, MATLAB R2017a, rilis 23 November 2021.

Keduanya memang berpasangan (kode ini adalah kode pendamping resmi paper tersebut),
tetapi **tidak sepenuhnya sesuai**. Ditemukan 4 cacat perangkat lunak (A1–A4),
12 penyimpangan kode terhadap deskripsi/rumus di manuskrip (B1–B12), 7 kesalahan
di dalam manuskrip sendiri (C1–C7), dan beberapa masalah minor (D1–D4).

## Cara verifikasi

Tiga lapis, saling menguatkan:

1. **Pembacaan kode** untuk temuan statis: label `case`, indeks array, presedensi
   operator, dan perbandingan baris-per-baris terhadap rumus di manuskrip.
2. **Eksekusi langsung sumber MATLAB** di GNU Octave 10.3.0. Berkas `.m` di `kma/`
   dan `kma-fixed/` dijalankan **tanpa modifikasi apa pun**; lihat §E.0 dan
   `experiments/octave/`.
3. **Port Python yang setia** di `experiments/kma_py/` untuk memisahkan kontribusi
   tiap cacat. Port ini mempertahankan seluruh detail implementasi MATLAB dan
   hanya membuat A1–A4 bisa di-toggle, sehingga 4.830 run bisa dijalankan dengan
   tujuh konfigurasi — sesuatu yang tidak praktis dilakukan di Octave. Lihat
   `experiments/README.md`.

Perbaikan minimal untuk A1–A4 ada di `kma-fixed/` (kode asli di `kma/` sengaja
dibiarkan utuh sebagai baseline).

---

## A. Cacat perangkat lunak

### A1 — `Evaluation.m`: `case 14` hilang, `case 16` dobel

**Lokasi**: `kma/Evaluation.m:101` (dan `:120`)

Blok Foxholes diberi label `case 16`, padahal Foxholes adalah **F14** —
`kma/GetFunction.m:80` menetapkan `Nvar=2, Ra=65, Rb=-65, MV=0.998` untuk
`FunctionID == 14`, yang persis spesifikasi Foxholes pada Tabel 6 manuskrip.
Six Hump Camel di `:120` juga berlabel `case 16`.

MATLAB mengeksekusi *case* pertama yang cocok, sehingga:

- **F14** tidak cocok dengan case mana pun → `fx` tidak pernah di-assign → error
  runtime. F14 tidak dapat dijalankan sama sekali.
- **F16** menjalankan Foxholes, bukan Six Hump Camel. Ambang `-1.0316` tak akan
  pernah tercapai, sehingga run berjalan penuh sampai anggaran habis dan
  mengembalikan nilai positif.

**Bukti empiris**: pada port, konfigurasi `published` menghasilkan error untuk F14
di seluruh 30 run, dan untuk F16 solusi yang dikembalikan bernilai ≈ `5.5e-05`
pada fungsi Six Hump Camel yang sebenarnya — bukan `-1.032`. Lihat §E.4.

**Dampak**: hasil F14 (`9.980E-01`, Std `4.382E-16`) dan F16 (`-1.032E+00`) pada
Tabel 2 manuskrip **tidak dapat direproduksi** dengan kode yang dipublikasikan.
Kode yang dipakai untuk eksperimen jelas berbeda dari kode rilis ini.

**Perbaikan**: `case 16` → `case 14` pada blok Foxholes.

### A2 — Indeks `AllHQ` salah pada tahap kedua

**Lokasi**: `kma/KMA2D.m:174-175`, `kma/KMA3D.m:222-223`

```matlab
AllHQ(ind:ind+NumBM-1,:) = BigMales;
AllHQFX(ind:ind+NumBM-1) = BigMalesFX;
```

`ind` melangkah sebesar `SwarmSize` (1, 6, 11, …, 196) karena dipakai untuk
mengindeks `Pop`. Namun `AllHQ` hanya menyimpan `NumBM` baris per micro-swarm,
jadi totalnya 40 × 2 = 80 baris. Indeks yang benar adalah
`((ind-1)/SwarmSize)*NumBM + 1`.

MATLAB menumbuhkan array secara otomatis dengan **nol**. Akibatnya `AllHQ`
membengkak menjadi 197 baris, dan puluhan di antaranya adalah vektor nol dengan
fitness 0. Baris-baris itu kemudian dipakai sebagai individu *high-quality* di
`MoveBigMalesFemaleSecondStage` dan `MoveSmallMalesSecondStage`.

**Bukti empiris** (generasi pertama tahap dua, F5 50-D):

```
AllHQ rows expected=80  actual=197 | all-zero rows=69
AllHQFX==0 entries=69   | min AllHQFX=0  vs  min real FX=48.9995
```

**Dampak**: untuk F1–F4, F6, F7, F9–F11 yang optimum globalnya persis di titik
origin dengan f = 0, ini menyuntikkan **solusi optimal palsu langsung ke kumpulan
attractor**. Baris yang ditimpa pada rentang 1–80 juga menimpa big male dari
micro-swarm yang salah. Cacat ini berada tepat di dalam mekanisme
self-adaptation tahap dua — bagian yang menjadi fokus repositori ini.

**Perbaikan**: hitung indeks baris `AllHQ` secara terpisah dari indeks `Pop`.

### A3 — Presedensi operator pada rumus mlipir

**Lokasi**: `kma/KMA2D.m:484` dan `:534`, `kma/KMA3D.m:538` dan `:588`

```matlab
VMlipir = VMlipir + rand(1,Nvar) .* (HQ(ind,:).*B)-(SmallMales(ww,:).*B);
```

MATLAB membaca ini sebagai `rand.*(HQ.*B) − (SM.*B)`, bukan `rand.*((HQ−SM).*B)`
seperti Eq. (8) manuskrip. Pada dimensi yang di-*mlipir*, hasilnya adalah
`x_baru = r · x_HQ` — bukan langkah menuju big male, melainkan **kontraksi menuju
titik nol koordinat**.

**Bukti empiris** (Sphere 50-D, 3 seed):

| | kode apa adanya | Eq. (8) sesuai paper |
|---|---|---|
| Sphere, optimum di **0** | **0** dalam ~430 generasi, 3/3 seed | macet di ~6–7 × 10⁴ |
| Sphere digeser, optimum di **x = 20** | 1.9 / 2.8 / 10.6 | 1.2 / 0.25 / 1.1 |

Fungsinya identik bentuknya; hanya optimumnya digeser dari origin. Keunggulan
menghilang begitu optimum tidak lagi di origin.

**Konfirmasi tambahan pada F5.** Rosenbrock adalah satu-satunya fungsi F1–F13
yang bukan-origin *dan* bukan-flat, dan nilai fungsinya di titik origin adalah
tepat `Dim − 1`:

| Dim | f_Rosenbrock(0) | KMA Avg (Tabel 2–5) |
|---|---|---|
| 50 | 49 | 48.31 |
| 100 | 99 | 95.30 |
| 500 | 499 | 471.5 |
| 1000 | 999 | 961.7 |

Hasil F5 yang dilaporkan manuskrip melacak nilai fungsi **di titik origin** pada
semua dimensi (96–99%). Ini konsisten dengan penjelasan bahwa yang diukur adalah
kontraksi menuju origin, bukan pencarian menuju optimum di `(1,1,…)`.

**Dampak**: klaim andalan paper — "global optimum dengan Std = 0 dan MFE sangat
kecil" untuk F1–F4, F6, F9, F11 — berasal dari artefak implementasi yang bias ke
origin, bukan dari rumus mlipir yang dideskripsikan.

**Perbaikan**: `rand(1,Nvar) .* ((HQ(ind,:) - SmallMales(ww,:)) .* B)`.

> **Catatan penting**: A2 dan A3 adalah **dua jalur terpisah menuju bias yang
> sama**. Memperbaiki salah satu saja tidak menghilangkan bias origin, karena
> jalur yang lain masih terbuka. Lihat kolom `fix_A2`, `fix_A3`, dan `fix_A2+A3`
> pada tabel hasil.

### A4 — `NumEva` menghitung kurang dari evaluasi sebenarnya

**Lokasi**: `kma/KMA2D.m:70`, `:181`, dan populasi awal `:36-38`, `:136-138`

Per generasi tahap satu kode menambah `NumEva` sebesar `PopSize` (5), padahal
evaluasi riil adalah 2 big male + 2 offspring (atau 1 mutasi) + 2 small male =
**5–6**. Pola yang sama terjadi di tahap dua (`NumEva += SwarmSize`). Selain itu
**tidak terhitung sama sekali**: 5 evaluasi populasi awal, dan **195 evaluasi**
`ConsPop` pada awal tahap dua.

**Bukti empiris** (Rosenbrock 50-D): `counted NumEva = 25000` sementara
`real evals = 29598` → **+18,4%**.

**Dampak**: seluruh kompetitor pada Tabel 2–5 dibatasi tepat 25.000 evaluasi,
sedangkan KMA sebenarnya memakai ~29.000–30.000. Perbandingannya tidak setara.
Kolom MFE juga tidak mencerminkan biaya sebenarnya.

**Perbaikan**: hitung di dalam `Evaluation` — satu panggilan = satu evaluasi.

---

## B. Kode menyimpang dari manuskrip

Bukan bug, tetapi kode tidak melakukan apa yang ditulis paper.

| # | Manuskrip | Kode |
|---|---|---|
| B1 | "n Komodo are created randomly" (Algoritma 1) | `PopConsInitialization` menempatkan seluruh individu di **4 sudut** ruang pencarian (±1%). 200 individu → hanya 4 posisi berbeda. Skema ini **tidak disebut sama sekali** di paper. |
| B2 | Tahap 2 = satu populasi 20–200 dibagi 3 grup | Kode membelahnya menjadi **40 micro-swarm @5** plus mekanisme `AllHQ` lintas-swarm. Arsitektur ini **tidak ada di paper**. |
| B3 | §2.8: radius partenogenesis `α = 0.1` | `MutRadius = 0.5` (`KMA2D.m:51`). §4 paper sendiri menulis "mutation radius of 0.5" — manuskrip kontradiksi dengan dirinya sendiri; kode mengikuti §4. |
| B4 | Eq. (7) memutasi semua dimensi | Kode menambahkan `MutRate = 0.5` per dimensi (`KMA2D.m:575`); parameter ini tidak ada di paper. |
| B5 | §2.10: "two successive improvements/stagnations" | `GenImprove > MaxGenImprove` dengan `MaxGenImprove = 2` → butuh **3** generasi berturut-turut (`KMA2D.m:219`, `:232`). |
| B6 | §2.8: female kawin/partenogenesis dengan **peluang tetap 0.5** | `if WinnerFX < FemaleFX \|\| rand < 0.5` (`KMA2D.m:348`). Karena winner adalah individu terbaik dari populasi yang sudah terurut, kondisi pertama hampir selalu benar → peluang kawin ≈ 1, bukan 0.5. |
| B7 | Eq. (4) dan (9): jumlahkan atas **semua q** big male | `MaxFolHQ = randi(2)` (big male tahap 1), `1` (small male tahap 1), `randi(3)` (tahap 2). §4 menyebut "one to three", yang hanya cocok untuk tahap 2. |
| B8 | — | `FolHQ = FolHQ + 1` diletakkan **di luar** `if ind ~= ss` (`KMA2D.m:331`, `:410`), jadi iterasi yang dilewati tetap dihitung sebagai pengikut → jumlah pengikut efektif lebih sedikit dari yang dimaksud. |
| B9 | Eq. (8): tiap dimensi dipilih dengan `r2 < d` | Kode memilih tepat `D = round(d·m)` dimensi lewat `randperm` — jumlahnya deterministik, bukan stokastik. |
| B10 | §2.7: q = 2 untuk unimodal, **q = 3** lebih baik untuk multimodal | `NumBM = floor(PopSize/2) = 2` selalu, di kedua tahap. Hipotesis q = 3 tidak pernah diimplementasikan. |
| B11 | — | `Reposition` (`KMA2D.m:602`) memakai `MutRadius` **dua kali** (`MutRadius*MaxStep`, padahal `MaxStep` sudah mengandung `MutRadius`) → radius 0.25 range, tidak konsisten dengan `Mutation`. |
| B12 | §2.10: individu baru "moved randomly" | Kode memakai **Lévy flight** `0.05*levy(1,Nvar,1.5)` (`KMA2D.m:587`); tidak disebut di paper. |

Yang **sudah sesuai**: mekanisme deteksi kompleksitas (100 generasi,
`ImproveRate < 0.5`, maksimum 1000 generasi) cocok dengan §4 — meski absen dari
pseudocode Algoritma 1. Parameter `n1=5, n2=200, n2,min=20, n2,max=200,
d1=(m−1)/m, d2=0.5` juga cocok dengan Tabel 1. Seluruh 23 fungsi benchmark di
`Evaluation.m` (selain A1) sudah diverifikasi cocok dengan optimum pada Tabel 6.

---

## C. Kesalahan di dalam manuskrip

- **C1 — Eq. (1)**: `q = ⌊(p−1)n⌋`. Dengan p = 0.5 dan n = 5 hasilnya **−3**.
  Seharusnya `q = ⌊p·n⌋`.
- **C2 — Eq. (2)**: `s = n − q` lupa mengurangi satu female. Seharusnya
  `s = n − q − 1` (kode: 5 = 2 + 1 + 2).
- **C3 — Distribusi acak**: §2.3, §2.7, §2.8, dan §2.9 berulang kali menulis
  "random numbers in the interval [0,1] in the normal distribution" — kontradiktif.
  Kode memakai `rand`, yaitu **uniform**.
- **C4 — Tabel 6, F2 (Schwefel 2.22)**: range ditulis `[−100, 100]`; seharusnya
  `[−10, 10]`, sesuai `GetFunction.m:33-34` dan literatur standar.
- **C5 — §2.8 vs §4**: `α = 0.1` versus "mutation radius of 0.5" (lihat B3).
- **C6 — Eq. (5)**: teks menyebut "the *k*th dimension" dan `rk`, padahal
  indeksnya `l`. Salah ketik notasi.
- **C7 — Komentar `GetFunction.m`**: `:68` untuk F11 (Griewank) menulis
  "Minimum = −418.9829 × 10^30" (salin-tempel dari F8); `:56` untuk F8 juga
  menulis `10^30` padahal maksudnya `× Dim`. Nilai `MV` itu sendiri sudah benar.

---

## D. Masalah minor

- **D1** — `Evaluation.m:114` (Kowalik, cabang `Dim == 2`) kehilangan `.^2`
  dibanding cabang normal di `:116`. Hanya memengaruhi permukaan 3D F15 pada
  `KMA3D`.
- **D2** — `KMA2D.m:47` menimpa `MaxAdaPopSize` yang sudah diset di
  `Main2D.m:39`, sehingga mengubah parameter di Main tidak berefek.
- **D3** — `EvoPopSize` pada tahap dua di-*append* setelah kemungkinan `break`
  (`KMA2D.m:262`), sehingga panjangnya bisa berbeda dari `fopt`/`fmean`.
- **D4** — `Main3D.m:35` menyebut dimensi "can be scaled up to millions",
  `Main2D.m:35` menyebut "thousands"; paper hanya menguji sampai 1000.

---

## E. Hasil eksperimen

Tabel lengkap ada di `experiments/results/summary.md`, data mentah per-run di
`experiments/results/raw.csv`. Setup: 23 fungsi benchmark, dimensi 50 untuk
F1–F13, anggaran 25.000 evaluasi, **30 run independen** per sel (4.830 run total),
tujuh konfigurasi.

### E.0 Verifikasi langsung dengan GNU Octave 10.3

Bagian ini **tidak** memakai port Python. Berkas `.m` di `kma/` dan `kma-fixed/`
dijalankan apa adanya di GNU Octave 10.3.0 lewat `experiments/octave/run_one.m`
(dimensi 50 untuk F1–F11, seed 1–3). Hasil mentah: `experiments/results/octave_verification.txt`.

**Semantik bahasa yang menjadi dasar A1 dan A2, dibuktikan langsung:**

```
id=16 -> FOXHOLES        % case duplikat: yang cocok PERTAMA yang dieksekusi
id=14 -> <error>         % tidak ada case yang cocok, nilai tak terdefinisi
A(7:8,:) = ...           % array 4 baris tumbuh jadi 8, 2 baris terisi NOL
```

Replay indeks `AllHQ` dengan ukuran sebenarnya (`experiments/octave/allhq_index_demo.m`):

```
built    : rows= 80  all-zero rows= 0
published: rows=197  all-zero rows=69   <- individu hantu di titik origin
fixed    : rows= 80  all-zero rows= 0
```

Angka 197 baris dan 69 baris nol **persis sama** dengan yang diprediksi port Python.

**Hasil menjalankan algoritmanya (`opt`, 3 seed):**

| Func | `kma/` (baseline terbit) | `kma-fixed/` (A1–A4 diperbaiki) |
|---|---|---|
| F1 Sphere | **0 · 0 · 0** | 57,2 · 113,9 · 22,1 |
| F5 Rosenbrock | 46,8 · 46,8 · 47,2 | 1,09e4 · 1,35e4 · 1,79e5 |
| F6 Step | **0 · 0 · 0** | 49 · 92 · 47 |
| F9 Rastrigin | **0 · 0 · 0** | 107,6 · 52,7 · 33,4 |
| F10 Ackley | 4,44e-16 ×3 | 1,35 · 2,58 · 2,13 |
| F11 Griewank | **0 · 0 · 0** | 1,51 · 1,82 · 1,19 |
| F14 Foxholes | **error ×3** | 0,998004 ×3 |
| F16 Six Hump Camel | 12,6705 ×3 | −1,03160 ×3 |

**Baseline mereproduksi angka manuskrip, termasuk MFE-nya:**

| | Octave, `kma/`, dim 50 | Manuskrip |
|---|---|---|
| F9 mean function evaluations | 140–145 | 145,33 (§3.3) |
| F6 mean function evaluations | 45–60 | 55,83 (Tabel 3, dim 100) |
| F11 mean function evaluations | 160–180 | 169,83 (Tabel 3, dim 100) |
| F5 nilai optimum | 46,8–47,2 | 48,31 (Tabel 2) |
| F16 | 12,6705 | −1,032 → **tidak cocok** (lihat A1) |

Kecocokan MFE sampai ke angka satuan menunjukkan bahwa yang dijalankan di sini
memang kode yang sama dengan yang menghasilkan Tabel 2–5 — kecuali untuk F14 dan
F16, yang tidak mungkin menghasilkan angka di Tabel 2 dengan kode ini.

`kma-fixed/` memperbaiki A2, A3, dan A4 sekaligus, jadi tabel di atas tidak
memisahkan kontribusi masing-masing. Pemisahan itu ada di §E.2 (port Python),
yang menunjukkan bahwa A4 sendirian tidak mengubah guaranty sama sekali dan yang
menentukan adalah A2+A3.

### E.1 Port ini memang mereproduksi perilaku kode terbit

Sebelum menafsirkan selisih apa pun, port perlu dibuktikan setia. Tiga tanda
independen:

- **Guaranty F1–F13**: konfigurasi `published` mencapai ambang optimum global di
  seluruh 30 run untuk **7 dari 13** fungsi = **53,85%** — persis angka yang
  diklaim §3.4 dan Tabel 3–5 manuskrip.
- **F7**: `published` menghasilkan `1,969e-04` versus `1,715e-04` di Tabel 2.
- **F5, F8, F10, F12, F13**: berada pada orde yang sama dengan Tabel 2
  (44,05 vs 48,31; −1,665e4 vs −1,701e4; 4,44e-16 vs 8,88e-16; 6,6e-03 vs
  2,8e-03; 6,7e-02 vs 5,3e-02).

### E.2 A2 dan A3 adalah dua jalur menuju bias yang sama

Nilai rata-rata (30 run) pada fungsi yang optimumnya di titik origin:

| Func | paper | published | fix_A2 saja | fix_A3 saja | **fix_A2+A3** |
|---|---|---|---|---|---|
| F1 Sphere | 0 | 0 | 0 | 2,1e-34 | **4,20e+01** |
| F2 Schwefel 2.22 | 0 | 0 | 0 | 4,1e-18 | **2,66e+00** |
| F3 Schwefel 1.2 | 0 | 0 | 0 | 3,1e-29 | **5,09e+02** |
| F4 Schwefel 2.21 | 0 | 0 | 0 | 2,2e-17 | **1,87e+00** |
| F6 Step | 0 | 0 | 0 | 0 | **6,10e+01** |
| F9 Rastrigin | 0 | 0 | 0 | 0 | **3,85e+01** |
| F10 Ackley | 8,9e-16 | 4,4e-16 | 4,4e-16 | 4,4e-16 | **1,94e+00** |
| F11 Griewank | 0 | 0 | 0 | 0 | **1,42e+00** |

Memperbaiki **salah satu** cacat saja tidak mengubah apa pun: jalur bias yang
lain masih terbuka. Menutup **keduanya** membuat hasil "0 dengan Std = 0" hilang
sepenuhnya.

Dampaknya pada metrik utama manuskrip:

| Konfigurasi | Guaranty F1–F13 |
|---|---|
| `published` (= klaim manuskrip) | **7/13 = 53,85%** |
| `fix_A1` / `fix_A2` / `fix_A4` (perbaikan tunggal) | 7/13 = 53,85% |
| `fix_A3` saja | 3/13 = 23,08% |
| **`fix_A2+A3`** | **0/13 = 0%** |
| `all_fixed` | 0/13 = 0% |

Angka 53,85% yang dipakai manuskrip untuk mengklaim skalabilitas di atas SMA
(23,08%), MPA (15,38%), dan EO (15,38%) menjadi **0%** begitu kedua jalur bias
origin ditutup.

### E.3 F5 bukan "terjebak di area datar", melainkan berhenti di origin

| Dim | f_Rosenbrock(0) | KMA Avg (Tabel 2–5) | rasio |
|---|---|---|---|
| 50 | 49 | 48,31 | 0,986 |
| 100 | 99 | 95,30 | 0,963 |
| 500 | 499 | 471,5 | 0,945 |
| 1000 | 999 | 961,7 | 0,963 |

Pada port, `published` memberi 44,05 (dekat f(0) = 49), sedangkan `fix_A2+A3`
memberi 3,3e+04 — yaitu hasil sebenarnya dari pencarian tanpa bias origin.
Penjelasan §4 manuskrip ("KMA terjebak stagnasi karena area datar F5") tidak
didukung: yang terjadi adalah solusi tertarik ke titik nol, dan Rosenbrock
kebetulan bernilai `Dim − 1` di sana.

### E.4 A1: F14 gagal jalan, F16 mengoptimalkan fungsi yang salah

| Func | published | fix_A1 | paper |
|---|---|---|---|
| F14 Foxholes | **error di 30/30 run** | 9,980e-01 (Std 0) | 9,980e-01 |
| F16 Six Hump Camel | 5,5e-05 (Guaranty 0%) | −1,032 (Guaranty 100%) | −1,032 |

Nilai `5,5e-05` untuk F16 adalah nilai fungsi Six Hump Camel yang sebenarnya pada
solusi yang dikembalikan kode — kode terbit mengoptimalkan Foxholes, sehingga
solusinya tidak ada hubungannya dengan optimum F16 di `(0,0898; −0,7126)`.

### E.5 A4: anggaran evaluasi terlampaui 13–29%

| Func | `NumEva` versi terbit | evaluasi sebenarnya | rasio |
|---|---|---|---|
| F1 | 2.194 | 2.637 | 1,202 |
| F5 | 25.040 | 29.696 | 1,186 |
| F8 | 25.064 | 29.880 | 1,192 |
| F12 | 25.044 | 29.819 | 1,191 |
| F15 | 25.098 | 30.115 | 1,200 |
| F19 | 1.809 | 2.314 | 1,280 |

Rata-rata rasio ≈ 1,20 di seluruh 23 fungsi (rentang 1,13–1,29). Seluruh
kompetitor pada Tabel 2–5 dibatasi tepat 25.000 evaluasi, sedangkan KMA memakai
sekitar 29.000–30.000. MFE yang dilaporkan juga lebih rendah ~20% dari biaya
sebenarnya.

### E.6 Individu hantu akibat A2, terukur

Jumlah maksimum baris `AllHQ` yang seluruhnya nol dalam satu generasi tahap dua,
untuk fungsi yang benar-benar masuk ke tahap dua:

| Func | published | fix_A2 |
|---|---|---|
| F5, F7, F8, F9, F10, F12, F13, F17, F20 | 69 | 0 |
| F19 | 70 | 0 |
| F15 | 71 | 0 |
| F18 | 73 | 0 |
| F16 | 81 | 0 |

Dari 80 baris `AllHQ` yang sah, versi terbit menghasilkan array 197 baris dengan
~70 di antaranya berupa vektor nol berfitness 0.

### E.7 Yang TIDAK terpengaruh

F17 (Branin), F18 (Goldstein–Price), F19 (Hartman 3), dan F23 (Shekel 10)
memberi Guaranty 100% pada **semua** konfigurasi, dan F20–F22 hanya bergeser
dalam batas noise. Hasil KMA untuk fungsi fixed-dimension multimodal ini **tidak**
bergantung pada cacat mana pun — bagian Tabel 2 itu sah. Optimum fungsi-fungsi
tersebut memang jauh dari titik origin dan ruang pencarian mereka kecil, sehingga
bias origin tidak membantu maupun merugikan.

### E.8 Peringatan penafsiran

- Kolom `all_fixed` **bukan** "algoritma paper yang dikerjakan dengan benar".
  Seluruh penyimpangan B1–B12 masih ada di dalamnya — terutama B1 (inisialisasi
  di keempat sudut), yang membuat populasi awal hampir tanpa keragaman. Sebagian
  dari selisih yang terlihat berasal dari sana, bukan dari A1–A4.
- Untuk **F7** gunakan `reported_best`, bukan `true_best`. F7 mengandung suku
  `+ rand`, sehingga mengevaluasi ulang solusi terbaik menambahkan noise baru
  (rata-rata 0,5) dan membuat `true_best` tidak sebanding dengan Tabel 2.
- Selisih antar konfigurasi valid karena semuanya berbagi port dan seed yang
  sama; nilai absolutnya tidak akan identik dengan MATLAB karena aliran bilangan
  acaknya berbeda.


---

## F. Reproduksi

```bash
# eksperimen (butuh numpy)
cd experiments
python3 run_experiments.py --seeds 30 --dim 50 --jobs 11
# -> results/raw.csv, results/summary.md

# kode MATLAB
cd kma        # baseline asli
cd kma-fixed  # dengan perbaikan A1-A4
# lalu jalankan Main2D atau Main3D
```

Hanya satu dari `kma/` dan `kma-fixed/` yang boleh ada di MATLAB path pada satu
waktu, karena nama fungsinya sama.

## G. Batasan audit ini

- `kma/` dan `kma-fixed/` sudah dieksekusi di **GNU Octave 10.3.0**, bukan di
  MATLAB R2017a. Octave menjalankan kedua versi tanpa modifikasi dan mereproduksi
  angka manuskrip pada baseline (§E.0), tetapi tetap bukan MATLAB. Satu
  ketergantungan diganti untuk verifikasi: `levy.m` memanggil
  `random('Normal',…)` dari Statistics Toolbox, yang di Octave disediakan lewat
  shim `experiments/octave/random.m` (`mu + sigma.*randn`, ekuivalen persis).
  Shim itu tidak boleh diletakkan di path MATLAB. Jalankan sekali di MATLAB
  sebelum dipakai untuk publikasi.
- Angka pada §E.1–§E.8 berasal dari port Python, bukan dari MATLAB atau Octave.
  Aliran bilangan acaknya berbeda, jadi nilai per-run tidak akan identik; yang
  dibandingkan adalah perilaku agregat antar konfigurasi yang berbagi port yang
  sama. §E.0 memakai sumber MATLAB asli dan berfungsi sebagai pemeriksaan silang.
- Sweep Octave di §E.0 hanya 3 seed per sel (bukan 30) karena satu run 50-dimensi
  memakan ~16 detik. Cukup untuk memastikan arah dan besaran efeknya, tidak cukup
  untuk statistik seperti Tabel 2.
- Eksperimen dijalankan pada dimensi 50 saja (F1–F13). Analisis skalabilitas
  Tabel 3–5 (100/500/1000 dimensi) tidak direplikasi, kecuali perbandingan
  `f_Rosenbrock(0)` pada A3 yang dihitung analitik.
- Konfigurasi `all_fixed` **bukan** "algoritma paper yang dikerjakan dengan
  benar". Itu adalah kode terbit dengan empat cacat dihapus; seluruh penyimpangan
  B1–B12 masih ada di dalamnya, dan sebagian dari selisih yang terlihat berasal
  dari sana (terutama B1, inisialisasi di sudut).
