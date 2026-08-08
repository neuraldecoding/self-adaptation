# self-adaptation

Mekanisme self-adaptation asli pada **Komodo Mlipir Algorithm (KMA)** — beserta
audit kesesuaian antara manuskrip yang diterbitkan dan kode pendampingnya.

Repositori ini memuat dua hal yang saling terkait:

- **Objek studi**: mekanisme self-adaptation ukuran populasi pada KMA v1.0.0
  (MATLAB) — konsep, implementasi, dan perilaku sebenarnya saat dijalankan.
- **Hasil audit**: pemeriksaan apakah kode di `kma/` benar-benar melakukan apa
  yang ditulis di manuskrip. Jawabannya **tidak sepenuhnya** — 4 cacat perangkat
  lunak, 14 penyimpangan kode terhadap manuskrip, 7 kesalahan di dalam manuskrip
  sendiri, dan beberapa masalah minor.

| Dokumen | Isi |
|---|---|
| **README.md** (berkas ini) | konsep self-adaptation, taksonomi, cara mengevaluasi, pelajaran yang bisa dipakai di kasus lain, ringkasan hasil |
| **[TEMUAN.md](TEMUAN.md)** | laporan audit lengkap: A1–A4, B1–B14, C1–C7, D1–D4, seluruh hasil eksperimen, batasan |
| **[ROADMAP.md](ROADMAP.md)** | peta jalan pengembangan dari *adaptive* ke *self-adaptive* |

## Sumber

| | |
|---|---|
| Manuskrip | S. Suyanto, A.A. Ariyanto, A.F. Ariyanto, *Komodo Mlipir Algorithm*, **Applied Soft Computing 114 (2022) 108043**. [doi:10.1016/j.asoc.2021.108043](https://doi.org/10.1016/j.asoc.2021.108043) — salinan di `manuscript/` |
| Kode | KMA v1.0.0, MATLAB R2017a, rilis 23 November 2021 — salinan **tanpa modifikasi** di `kma/` |

---

# Mekanisme self-adaptation

Bagian ini ditulis agar bisa dipakai di luar KMA. Konsep dan taksonominya berlaku
untuk metaheuristik mana pun; KMA dipakai sebagai studi kasus, termasuk
kesalahan-kesalahannya, yang justru sering lebih instruktif daripada contoh yang
mulus.

## 1. Masalah yang dipecahkan: parameter kendali

Setiap metaheuristik punya **parameter kendali** — ukuran populasi, laju mutasi,
laju crossover, ukuran langkah, tekanan seleksi. Nilainya biasanya dipatok
pengguna sebelum run. Ada dua masalah dengan cara itu:

1. **Nilai optimalnya bergantung pada masalah** yang sedang dipecahkan, padahal
   karakteristik masalah itu justru belum diketahui — kalau sudah diketahui,
   mungkin tidak perlu metaheuristik. Ini konsekuensi langsung teorema *No Free
   Lunch* (Wolpert & Macready, 1997): tidak ada satu setelan yang unggul untuk
   semua masalah.
2. **Nilai terbaiknya berubah selama run.** Di generasi awal populasi masih
   tersebar dan yang dibutuhkan adalah penjelajahan luas; di generasi akhir
   populasi sudah mengerucut dan yang dibutuhkan adalah pendalaman. Satu nilai
   tetap tidak mungkin optimal di kedua fase.

Parameter control adalah jawaban untuk keduanya: parameter diubah **selama** run,
bukan ditetapkan sebelum run.

## 2. Eksploitasi dan eksplorasi

Hampir semua parameter kendali pada akhirnya mengatur satu hal yang sama, jadi
konsep ini perlu jelas lebih dulu.

**Eksploitasi** (*intensification*) — memperdalam pencarian di sekitar solusi baik
yang sudah ditemukan. Konvergensi cepat, presisi tinggi, tetapi berisiko terkunci
di optimum lokal.

**Eksplorasi** (*diversification*) — menjelajah wilayah ruang pencarian yang belum
tersentuh. Menghindari optimum lokal, tetapi boros evaluasi dan lambat mengerucut.

Keduanya saling meniadakan dalam anggaran evaluasi yang terbatas: setiap evaluasi
yang dipakai menjelajah adalah evaluasi yang tidak dipakai mendalami.

| Terlalu eksploitatif | Terlalu eksploratif |
|---|---|
| konvergensi prematur | tidak pernah mengerucut |
| terjebak optimum lokal | praktis menjadi pencarian acak |
| keragaman populasi habis dini | anggaran evaluasi terbuang |

Yang mengendalikan keseimbangan ini biasanya: **ukuran populasi**, keragaman
populasi, ukuran langkah gerakan, dan tekanan seleksi.

Pada KMA, keseimbangan itu dirancang lewat tiga strategi gerakan yang berjalan
bersamaan — istilah dari manuskrip:

| Singkatan | Pelaku | Sifat |
|---|---|---|
| **HILE** *high-exploitation low-exploration* | big male | mendalami area sekitar solusi terbaik |
| **MIME** *medium-exploitation medium-exploration* | female | kawin (eksploitasi) atau partenogenesis (eksplorasi), peluang 0,5 |
| **LIHE** *low-exploitation high-exploration* | small male | gerakan *mlipir*, menjelajah sisi ruang pencarian |

Di atas ketiganya, **ukuran populasi `n`** bekerja sebagai pengatur global:
`n` besar berarti banyak kandidat tersebar sekaligus (eksplorasi naik, biaya per
generasi naik), `n` kecil berarti pencarian mengerucut cepat dan hemat evaluasi
(eksploitasi naik, risiko terjebak naik). Itulah yang diadaptasi KMA.

## 3. Taksonomi: tuning, deterministic, adaptive, self-adaptive

Ini rujukan baku dari Eiben, Hinterding & Michalewicz (1999). Membedakannya
penting karena **istilah "self-adaptive" sering dipakai longgar** di literatur
metaheuristik, termasuk oleh KMA.

Pembagian pertama:

- **Parameter tuning** — nilai dicari **sebelum** run (grid search, irace, dsb.),
  lalu dipatok. Bukan parameter control.
- **Parameter control** — nilai berubah **selama** run. Terbagi tiga:

| Tingkat | Apa yang menggerakkan | Umpan balik? | Diseleksi? | Contoh |
|---|---|---|---|---|
| **Deterministic** | jadwal tetap terhadap waktu/generasi | tidak | tidak | LSHADE: `n` turun linear terhadap jumlah evaluasi |
| **Adaptive** | umpan balik dari jalannya pencarian | **ya** | tidak | aturan 1/5 Rechenberg; **Eq. (10) KMA** |
| **Self-adaptive** | parameter dikodekan **di dalam individu**, ikut bervariasi dan **diseleksi** | tidak langsung | **ya** | σ pada Evolution Strategies; `F` dan `CR` pada jDE |

### Cara mengenali mana yang mana

Ajukan dua pertanyaan berurutan:

1. **Apakah perubahannya bergantung pada apa yang ditemukan pencarian?**
   Tidak → *deterministic*. Ya → lanjut.
2. **Apakah parameternya menempel pada individu dan ikut mati bersama individu
   yang kalah seleksi?**
   Tidak → *adaptive*. Ya → *self-adaptive*.

### Di mana KMA berada

KMA memakai sinyal membaik/stagnan untuk menggerakkan `n`, jadi lolos pertanyaan
pertama. Tetapi `n` tidak menempel pada individu mana pun dan tidak melewati
seleksi, jadi gagal di pertanyaan kedua.

> **Skema KMA tergolong *adaptive*, bukan *self-adaptive* dalam arti ketat.**
> Ini bukan cacat — skema adaptive sepenuhnya sah dan banyak dipakai — hanya
> penamaannya yang tidak sesuai taksonomi baku. Dokumen ini tetap memakai istilah
> manuskrip agar mudah dirujuk silang.

### Kenapa perbedaan ini penting secara praktis

Self-adaptive menuntut **lingkaran seleksi yang tertutup**: parameter memengaruhi
fitness individu pembawanya → individu itu diseleksi → parameter yang baik ikut
lolos. Kalau salah satu mata rantai putus, yang didapat hanya angka acak yang
menumpang di dalam genom, bukan self-adaptation. Konsekuensinya langsung ke
rancangan — lihat §8 dan [ROADMAP.md](ROADMAP.md).

## 4. Anatomi sebuah skema adaptif

Skema parameter control apa pun bisa dipecah menjadi empat komponen. Daftar ini
bisa langsung dipakai sebagai kerangka saat merancang skema sendiri.

| Komponen | Pertanyaan | Pada KMA |
|---|---|---|
| **Parameter** | apa yang diadaptasi, dan kenapa itu yang dipilih? | ukuran populasi `n` |
| **Sinyal umpan balik** | apa yang diamati untuk memutuskan? | perbaikan fitness terbaik-sejauh-ini |
| **Aturan keputusan** | bagaimana sinyal diterjemahkan jadi perubahan? | Eq. (10): membaik → `n − 5`, stagnan → `n + 5` |
| **Batas dan nilai awal** | rentang sahnya, dan mulai dari mana? | `n ∈ [20, 200]`, `n₀ = 200` |

Komponen keempat paling sering diremehkan, padahal justru di situ skema KMA
tersandung — lihat §7.

## 5. Implementasi pada KMA

### Parameter yang dipilih

KMA hanya mengadaptasi `n`. Alasannya di §2.10 manuskrip: `n` dianggap jauh lebih
sensitif daripada porsi big male `p` dan mlipir rate `d`, sehingga `p` dan `d`
dipatok 0,5.

> Perlu dicatat, manuskrip menyatakannya sebagai *"Hypothetically, n is more
> sensitive than p and d"* — **hipotesis yang tidak pernah diuji**. Tidak ada
> analisis sensitivitas di paper. Kalau merancang skema sendiri, ini langkah yang
> sebaiknya tidak dilewati.

### Aturan kendalinya

| Sinyal | Tafsiran | Tindakan | Maksud |
|---|---|---|---|
| dua generasi berturut **membaik** | pencarian sedang produktif | `n − 5` | perketat eksploitasi, hemat evaluasi |
| dua generasi berturut **stagnan** | terjebak lokal atau area datar | `n + 5`, individu baru dari big male terbaik yang digeser acak | suntikkan keragaman untuk kabur |

Persyaratan "dua generasi berturut" adalah **histeresis** — mencegah skema
bereaksi terhadap fluktuasi satu generasi. (Kode sebenarnya memakai `> 2`, jadi
tiga generasi; lihat B5 di TEMUAN.md.)

### Posisinya di kode: menyatu atau blok terpisah?

**Manuskrip bertentangan dengan dirinya sendiri.** Algoritma 1 — satu-satunya
spesifikasi formal — menempatkannya **menyatu** di dalam loop utama, dijalankan
tiap generasi, sejajar dengan ketiga gerakan. Sebaliknya §2.4 dan §3.1 menyatakan
fase 1 memakai populasi tetap 5 individu dan self-adaptation hanya ada di fase 2.
**Kode mengikuti §2.4/§3.1, bukan Algoritma 1.**

```
 68  while Gen < MaxGenExam2              TAHAP 1
 79    MoveBigMalesFemaleFirstStage
 80    MoveSmallMalesFirstStage
 93    EvoPopSize = [EvoPopSize PopSize]     n tetap 5, tidak ada adaptasi apa pun
112  end

145  while NumEva < MaxNumEva              TAHAP 2, loop luar
149    for ind=1:SwarmSize:AdaPopSize        loop dalam, 40 micro-swarm
171      MoveBigMalesFemaleSecondStage         ketiga gerakan ada DI SINI
172      MoveSmallMalesSecondStage
188    end
207    % Self-adaptation of population size   BLOK SELF-ADAPTATION (207-256)
209      counter improve / stagnan
219      cabang menyusut : sort lalu potong
232      cabang membesar : AddingPop / Reposition
262    EvoPopSize = [EvoPopSize AdaPopSize]
264  end
```

Jadi **blok terpisah**, dan terpisah dalam tiga hal sekaligus:

1. **Menurut tahap** — sama sekali tidak ada di tahap 1; 1.000 generasi berjalan
   pada `n = 5` tetap.
2. **Menurut level loop** — ketiga gerakan di loop dalam per micro-swarm
   (149–188), self-adaptation di loop luar (207–256). Beda tingkat nesting, dan
   tidak bisa dipetakan ke Algoritma 1 karena micro-swarm tidak ada di manuskrip.
3. **Menurut data** — blok itu hanya menyentuh `Pop`, `FX`, `OneElitFX`, dan
   counter-nya sendiri. Tidak menyentuh `BigMales`, `Female`, `SmallMales`,
   `AllHQ`, maupun `MlipirRate`. Bisa diangkat keluar utuh.

Ada ironi kecil: ketiga gerakan difaktorkan menjadi subfungsi bernama, sementara
self-adaptation — yang di manuskrip punya bagian sendiri sebagai kontribusi —
ditulis **inline tanpa nama**.

## 6. Cara mengevaluasi skema self-adaptation

Bagian ini yang paling mudah dilewatkan, dan paling sering membuat klaim tidak
bisa dipertahankan.

### Ablation adalah wajib

Skema adaptif harus dibandingkan dengan **parameter tetap yang disetel baik**.
Kalau `n` adaptif tidak mengalahkan `n` tetap terbaik dari `{20, 50, 100, 200}`,
skema adaptifnya tidak memberi nilai tambah — kerumitannya tidak terbayar.

> Paper KMA tidak melakukan ablation ini. Struktur §3 hanya berisi parameter
> settings, perbandingan dengan kompetitor, kurva konvergensi, dan skalabilitas.
> Tidak ada satu pun eksperimen yang mengisolasi sumbangan skema adaptasi
> populasi.

### Periksa lintasan parameternya, jangan diasumsikan

Rekam nilai parameter tiap generasi dan periksa. Skema bisa saja **tidak pernah
aktif** tanpa ketahuan dari metrik akhir. Pada KMA, `EvoPopSize` sudah tersedia
sebagai keluaran resmi `KMA2D` — lihat `experiments/octave/selfadapt_probe.m`.
Yang perlu dilihat: berapa kali tiap cabang aturan dijalankan, dan apakah kedua
arah benar-benar terpakai.

### Benchmark tidak boleh memihak

Dari 13 fungsi berdimensi tinggi pada suite klasik 23 fungsi, **tujuh optimumnya
persis di titik origin**. Algoritma apa pun yang punya bias ke origin — disengaja
atau tidak — akan menang di sana. Geser optimumnya (`f(x − o)`), sebaiknya juga
rotasi. Repositori ini adalah contoh nyata kenapa: lihat §Hasil utama.

### Anggaran evaluasi harus dihitung per panggilan objektif

Kalau tidak, varian dengan `n` kecil akan tampak unggul hanya karena salah hitung.
Pada KMA, `NumEva` dinaikkan per generasi, bukan per evaluasi — anggaran
terlampaui 13–29%.

## 7. Apa yang sebenarnya terjadi pada KMA

Diukur dengan `experiments/octave/selfadapt_probe.m`, yang membaca `EvoPopSize`
tanpa memodifikasi kode. 33 run pada fungsi yang benar-benar mencapai tahap dua:

| Pengamatan | Hasil |
|---|---|
| Tahap 1 berjalan pada `n = 5` tetap | 33/33 run |
| Tahap 2 dimulai pada `n = 200` | 33/33 run |
| Populasi **tidak pernah berubah** sepanjang tahap 2 | 8/33 run |
| Total langkah turun vs naik | **409 vs 57** |
| Generasi tahap 2 yang dihabiskan pada `n = 200` | 33% |

Penyebabnya adalah komponen keempat dari §4 — **nilai awal berimpit dengan
batas**. Tahap 2 dimulai tepat pada `n = 200 = n_max`, sehingga cabang `n + a`
**tidak terjangkau** sampai populasi sempat menyusut. Ketika stagnasi terjadi di
batas atas, kode tidak menambah individu melainkan menjalankan `Reposition` atas
seluruh populasi — operator **greedy** (perubahan hanya diterima bila lebih baik)
yang tidak ada di manuskrip, dan yang karena sifat greedy-nya tidak dapat
memulihkan keragaman sebagaimana penambahan individu baru.

Akibatnya, mekanisme yang dimaksudkan sebagai **penyeimbang dua arah** berperilaku
sebagai **ratchet penyusut satu arah**, dengan separuh perannya digantikan
operator intensifikasi yang tidak terdokumentasi.

Biayanya nyata: untuk F10, seluruh 75 generasi tahap dua berjalan pada `n = 200`
tanpa satu pun perubahan ukuran, tetapi stagnasi memicu `Reposition` setiap tiga
generasi — sekitar **20% anggaran evaluasi** habis untuk operator yang tidak
dideskripsikan, sementara "self-adaptation of population size" tidak mengubah
ukuran populasi sama sekali.

## 8. Pelajaran yang bisa dibawa ke kasus lain

Sebelas butir, semuanya berasal dari temuan konkret di repositori ini.

**Rancangan**

1. **Uji sensitivitas sebelum memilih parameter.** Jangan mengadaptasi parameter
   hanya karena "hipotetis paling sensitif". Ukur dulu.
2. **Jangan menaruh nilai awal di batas rentang.** Kalau `n₀ = n_max`, separuh
   aturan mati sejak awal. Mulai dari tengah, atau pastikan kedua cabang
   terjangkau.
3. **Pastikan kedua arah bisa dijalankan, lalu ukur keduanya.** Rasio 409:57 pada
   KMA baru terlihat setelah lintasannya dihitung.
4. **Jangan mengganti operator diam-diam saat parameter mentok.** Kalau `n` tidak
   bisa naik, catat kejadiannya — jangan jalankan operator lain yang tidak
   dideskripsikan. Ini membuat perilaku algoritma menyimpang dari spesifikasinya
   tanpa jejak.
5. **Beri histeresis pada sinyal umpan balik.** Bereaksi terhadap satu generasi
   berarti mengejar derau; terlalu lambat berarti tidak sempat bereaksi.
6. **Pakai langkah proporsional bila rentangnya lebar.** `n ± 5` bermakna berbeda
   pada `n = 20` dan `n = 200`.

**Untuk naik ke tingkat self-adaptive**

7. **Parameter harus menempel pada entitas yang diseleksi.** Ini syarat mati.
   Parameter tingkat populasi seperti `n` tidak punya lingkaran seleksi, jadi
   butuh encoding tak langsung (lifetime/umur seperti GAVaPS dan APGA).
8. **Periksa apakah tekanan seleksinya nyata.** Pada KMA, small male disimpan
   *"with no survivor selection"* — menempelkan `d` pada mereka tanpa mengubah itu
   akan menghasilkan gen yang tidak pernah tersaring.
9. **Amati distribusi parameter sepanjang run.** Kalau menyempit ke satu nilai,
   self-adaptation bekerja. Kalau tetap acak, tekanan seleksinya tidak cukup.

**Evaluasi**

10. **Ablation terhadap parameter tetap adalah wajib**, bukan pelengkap.
11. **Pilih benchmark yang tidak memihak** dan hitung anggaran evaluasi per
    panggilan fungsi objektif.

Peta jalan penerapannya pada KMA: [ROADMAP.md](ROADMAP.md).

---

# Ringkasan temuan audit

## Cacat perangkat lunak

| Kode | Lokasi | Inti masalah |
|---|---|---|
| **A1** | `kma/Evaluation.m:101` | Blok Foxholes diberi label `case 16`, padahal Foxholes adalah **F14**. Karena MATLAB mengeksekusi *case* pertama yang cocok, **F14 error** (`fx` tak pernah di-assign) dan **F16 diam-diam mengoptimalkan Foxholes**, bukan Six Hump Camel. |
| **A2** | `kma/KMA2D.m:174-175`<br>`kma/KMA3D.m:222-223` | Indeks baris `AllHQ` memakai indeks `Pop`. Array tumbuh dari 80 menjadi 197 baris, ~70 di antaranya **vektor nol berfitness 0** yang dipakai sebagai individu *high-quality*. Cacat ini berada tepat di dalam mekanisme self-adaptation tahap dua. |
| **A3** | `kma/KMA2D.m:484`, `:534`<br>`kma/KMA3D.m:538`, `:588` | Presedensi operator: baris itu dievaluasi sebagai `rand.*(HQ.*B) − (SM.*B)`, bukan `rand.*((HQ−SM).*B)` seperti Eq. (8). Efeknya **kontraksi menuju titik nol koordinat**. |
| **A4** | `kma/KMA2D.m:70`, `:181` | `NumEva` dinaikkan per generasi, bukan per evaluasi. Anggaran 25.000 terlampaui **13–29%**. |

**A2 dan A3 adalah dua jalur terpisah menuju bias yang sama.** Memperbaiki salah
satu saja tidak menghilangkan bias origin.

## Penyimpangan dan kesalahan lain

- **B1–B14** — kode tidak melakukan apa yang ditulis paper. Terbesar: inisialisasi
  populasi di **4 sudut** ruang pencarian (paper menulis "created randomly"),
  struktur **40 micro-swarm** pada tahap dua yang tidak dideskripsikan, dan **B13**
  — cabang "tambah individu" Eq. (10) yang tidak terjangkau lalu diam-diam
  digantikan operator lain (lihat §7).
- **C1–C7** — kesalahan di dalam manuskrip. Termasuk Eq. (1) `q = ⌊(p−1)n⌋` yang
  bernilai negatif, Eq. (2) yang lupa mengurangi satu female, dan §2.8 (`α = 0.1`)
  yang bertentangan dengan §4 ("mutation radius of 0.5").
- **D1–D4** — masalah minor.

---

# Hasil utama

## Angka andalan manuskrip bergantung pada bias origin

Guaranty diukur langsung di Octave dengan sumber MATLAB asli, 30 run per sel:

| | `kma/` (versi terbit) | `kma-fixed/` (A1–A4 diperbaiki) |
|---|---|---|
| Guaranty F1–F13 | **7/13 = 53,85%** | **0/13 = 0%** |

Angka 53,85% itu persis yang diklaim §3.4 manuskrip untuk mengunggulkan KMA di
atas SMA (23,08%), MPA dan EO (15,38%). Angka itu menjadi **0%** begitu kedua
jalur bias origin ditutup.

## Baseline mereproduksi Tabel 2 — kecuali F14 dan F16

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

## F5 melacak nilai fungsi di titik origin

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

## Yang tetap sah

**F15 dan F17–F23 tidak terpengaruh cacat mana pun.** `kma/` dan `kma-fixed/`
memberi hasil praktis identik — F18 dan F21 sama-sama eksak, F22 dan F23 sama
sampai enam angka penting. Optimum fungsi-fungsi itu jauh dari origin dan ruang
pencariannya kecil, sehingga bias origin tidak membantu maupun merugikan.

Gambaran akhirnya terpisah rapi menjadi tiga kelompok:

- **F1–F13** — bergantung penuh pada bias origin (A2+A3).
- **F14, F16** — rusak karena A1; angka di Tabel 2 tidak dapat dihasilkan kode ini.
- **F15, F17–F23** — sah apa adanya.

---

# Isi repositori

```
manuscript/     komodomelipiralgorithm.pdf — paper Applied Soft Computing 114 (2022) 108043
kma/            KMA v1.0.0 asli, TIDAK DISENTUH. Baseline untuk semua perbandingan.
kma-fixed/      Salinan dengan perbaikan minimal A1-A4 saja. Tiap perubahan ditandai
                komentar "FIX Ax". Diff lengkap di A1-A4.patch. Penyimpangan B1-B14
                sengaja dibiarkan agar efek A1-A4 terisolasi.
experiments/
  octave/       Menjalankan sumber MATLAB apa adanya di GNU Octave.
                run_one.m           satu run headless
                sweep.sh            sweep kma/ vs kma-fixed/, paralel
                summarize.py        ringkasan bergaya Tabel 2
                selfadapt_probe.m   jejak ukuran populasi lewat EvoPopSize
                allhq_index_demo.m  replay pengindeksan AllHQ (temuan A2)
                random.m            shim Octave untuk random('Normal',...)
  kma_py/       Port Python yang setia dari KMA2D.m dengan A1-A4 bisa di-toggle,
                plus 23 fungsi benchmark yang sudah diverifikasi terhadap Tabel 6.
  results/      octave_verification.txt  1.380 run Octave (23 fungsi x 30 seed x 2 versi)
                octave_summary.md        ringkasan Avg (Std), MFE, Guaranty
                selfadapt_probe.txt      jejak ukuran populasi, 33 run
                raw.csv                  4.830 run Python (23 fungsi x 7 konfigurasi x 30 seed)
                summary.md               ringkasan per konfigurasi
TEMUAN.md       Laporan audit lengkap.
ROADMAP.md      Peta jalan dari adaptive ke self-adaptive.
```

## Kenapa dua jalur eksperimen

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

# Reproduksi

## Menjalankan kode MATLAB

`Main2D.m`/`Main3D.m` memanggil `KMA2D`/`KMA3D` dengan nama yang sama di kedua
folder, jadi **hanya satu** yang boleh ada di path pada satu waktu:

```matlab
cd kma          % baseline asli
% atau: cd kma-fixed
Main2D
```

## Verifikasi dengan GNU Octave (tanpa root)

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

## Eksperimen Python

```bash
cd experiments
python3 run_experiments.py --seeds 30 --dim 50 --jobs 11    # butuh numpy
```

Detail: `experiments/README.md`.

---

# Status dan batasan verifikasi

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
  terbit dengan empat cacat dihapus; seluruh penyimpangan B1–B14 masih ada di
  dalamnya — terutama B1, inisialisasi di sudut.

---

# Rujukan

Periksa kembali detail sitasi sebelum dipakai di naskah.

- A.E. Eiben, R. Hinterding, Z. Michalewicz, *Parameter Control in Evolutionary
  Algorithms*, IEEE Transactions on Evolutionary Computation 3(2):124–141, 1999.
- D. Wolpert, W. Macready, *No Free Lunch Theorems for Optimization*, IEEE TEC
  1(1):67–82, 1997.
- J. Arabas, Z. Michalewicz, J. Mulawka, *GAVaPS — a Genetic Algorithm with
  Varying Population Size*, IEEE CEC, 1994.
- T. Bäck, A.E. Eiben, N.A.L. van der Vaart, *An Empirical Study on GAs "Without
  Parameters"*, PPSN VI, 2000.
- J. Brest dkk., *Self-Adapting Control Parameters in Differential Evolution*,
  IEEE TEC 10(6):646–657, 2006.
- R. Tanabe, A.S. Fukunaga, *Improving the search performance of SHADE using
  linear population size reduction*, IEEE CEC, 2014.
- S. Suyanto, A.A. Ariyanto, A.F. Ariyanto, *Komodo Mlipir Algorithm*, Applied
  Soft Computing 114:108043, 2022.

---

# Lisensi dan atribusi

- `kma/` dan `kma-fixed/` adalah karya **Suyanto Suyanto (Telkom University)**,
  dilisensikan **BSD 3-Clause** — lihat `kma/license.txt`. Lisensi itu tetap
  berlaku untuk kedua folder, termasuk salinan yang sudah dipatch.
- `manuscript/` adalah artikel akses terbuka Elsevier di bawah **CC BY-NC-ND 4.0**.
- Sisa repositori (audit, harness eksperimen, dokumentasi) di bawah **GPL-3.0**,
  lihat `LICENSE`.
