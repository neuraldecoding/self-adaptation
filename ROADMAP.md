# ROADMAP — dari *adaptive* ke *self-adaptive* pada KMA

Peta jalan pengembangan mekanisme self-adaptation KMA. Dasarnya adalah hasil audit
di [TEMUAN.md](TEMUAN.md); konsep dan taksonominya dijelaskan di
[README.md](README.md#mekanisme-self-adaptation).

## Titik berangkat

Skema KMA sekarang tergolong **adaptive** menurut taksonomi Eiben, Hinterding &
Michalewicz (1999): satu parameter tingkat populasi (`n`) digerakkan oleh umpan
balik membaik/stagnan. Ia **belum self-adaptive**, karena parameternya tidak
dikodekan di dalam individu dan tidak melewati seleksi.

Sasarannya: menaikkannya ke tingkat self-adaptive, dengan hasil yang bisa
dipertahankan secara metodologis.

---

## Prasyarat — kerjakan sebelum apa pun diukur

Tanpa tiga hal ini, angka apa pun yang dihasilkan tidak bisa ditafsirkan.

### P1. Baseline yang bersih

Jangan membandingkan varian baru dengan `kma/`. Angka andalan versi itu berasal
dari bias menuju titik origin (A2 dan A3): Guaranty F1–F13 turun dari 53,85%
menjadi **0%** begitu keduanya diperbaiki. Peningkatan apa pun yang diukur
terhadap baseline itu tidak bermakna.

**Pakai `kma-fixed/`** sebagai baseline. Kalau perlu baseline yang lebih ketat
lagi, perbaiki juga B1 (inisialisasi di empat sudut) dan B11 (`MutRadius` ganda),
lalu catat baseline mana yang dipakai.

### P2. Benchmark yang tidak memihak

Dari 13 fungsi berdimensi tinggi pada suite klasik, **tujuh** optimumnya persis di
titik origin. Algoritma apa pun yang punya bias ke origin — disengaja atau tidak —
akan menang di sana. Suite itu tidak bisa membedakan pencarian yang baik dari
artefak implementasi.

Minimal: geser optimum (`f(x − o)`) dengan `o` acak per fungsi per run.
Lebih baik: pakai CEC (shifted **dan** rotated), yang juga menghilangkan
separability. Paper KMA sendiri mengakui keterbatasan ini di bagian limitation.

### P3. Anggaran evaluasi yang jujur

Perbaiki A4 — hitung evaluasi di dalam fungsi objektif. Versi terbit melampaui
anggaran 13–29%. Tanpa ini, varian dengan `n` lebih kecil akan tampak unggul
hanya karena salah hitung.

---

## Tahap 0 — Instrumentasi dan ablation baseline

Belum ada perubahan algoritma. Tujuannya: tahu apa yang sebenarnya dilakukan
skema yang ada.

- [ ] Rekam lintasan parameter tiap run (`EvoPopSize` sudah tersedia; lihat
      `experiments/octave/selfadapt_probe.m`).
- [ ] Hitung berapa kali tiap cabang aturan benar-benar dijalankan.
- [ ] **Ablation yang belum pernah dilakukan paper**: bandingkan skema adaptif
      terhadap `n` **tetap** yang disetel baik — misalnya `n ∈ {20, 50, 100, 200}`
      tetap sepanjang run. Kalau skema adaptif tidak mengalahkan `n` tetap
      terbaik, skema itu tidak memberi nilai tambah.

> Ini titik lemah metodologis terbesar pada paper aslinya. §2.10 hanya menyatakan
> *"Hypothetically, n is more sensitive than p and d"* — hipotesis yang tidak
> pernah diuji, dan tidak ada satu pun eksperimen di §3 yang mengisolasi
> sumbangan skema adaptasi populasi.

**Keluaran**: baseline terukur + bukti bahwa adaptasi memang perlu (atau tidak).

---

## Tahap 1 — Perbaiki asimetri skema *adaptive* yang ada

Langkah termurah dengan hasil paling pasti. Masih di tingkat *adaptive*.

Masalahnya (B13): tahap dua dimulai tepat pada `n = 200 = n_max`, sehingga cabang
`n + a` **tidak terjangkau** sampai populasi sempat menyusut. Terukur **409
langkah turun berbanding 57 naik**. Saat stagnasi di batas atas, kode diam-diam
menjalankan `Reposition` — operator greedy yang tidak ada di manuskrip dan tidak
bisa memulihkan keragaman. Penyeimbang dua arah berperilaku sebagai ratchet satu
arah.

Yang bisa dicoba:

- [ ] **Mulai dari tengah**, misalnya `n₀ = (n_min + n_max)/2`, supaya kedua
      cabang hidup sejak awal.
- [ ] Buat cabang tambah benar-benar berfungsi saat `n < n_max`, dan **jangan**
      mengganti operator diam-diam saat mentok di batas — kalau `n` tidak bisa
      naik, catat dan biarkan, atau naikkan `n_max`.
- [ ] Uji histeresis selain `> 2` generasi (`MaxGenImprove`/`MaxGenStagnan`).
- [ ] Uji ukuran langkah `a` selain 5, termasuk langkah proporsional
      (`n ± ⌈0,05·n⌉`) agar tidak bergantung pada skala `n`.

**Keluaran**: skema adaptif yang benar-benar dua arah, dengan lintasan `n` yang
terdokumentasi. Ini pembanding bersih untuk Tahap 2.

---

## Tahap 2 — Self-adaptive pada `d` dan `p` (jalur utama)

Ini jalur yang paling menjanjikan, dan **paper sendiri sudah menunjuk ke sana**:

> *"In the future, an advanced self-adaptation scheme can be developed to
> dynamically update the two parameters: big male portion and mlipir rate."*

Alasannya teknis, bukan sekadar mengikuti saran paper. `n` adalah parameter
**tingkat populasi** — tidak ada individu yang "memilikinya", sehingga tidak ada
lingkaran seleksi yang bisa menyaringnya. Sebaliknya `d` (mlipir rate) bersifat
**per individu secara alami**: tiap small male bisa membawa `dᵢ` sendiri yang
dipakai di gerakannya sendiri, memengaruhi fitness-nya sendiri, lalu diseleksi.
Itu persis pola jDE (Brest dkk. 2006) yang menyetel `F` dan `CR` per individu —
dan jDE/SHADE ada di daftar kompetitor KMA sendiri.

### Jebakan yang harus diselesaikan lebih dulu

§2.3 dan Algoritma 1 menyatakan posisi baru small male disimpan **"with no
survivor selection"** — semua diterima tanpa kecuali. **Tanpa seleksi,
self-adaptation mati di tempat**: `dᵢ` yang buruk tidak pernah tersingkir,
sehingga tidak ada tekanan yang membuatnya membaik. Ini bukan detail
implementasi, melainkan keputusan desain yang harus diambil sadar.

Tiga pilihan:

1. Beri small male survivor selection (`(μ+λ)` atas TempWM vs SmallMales).
   Konsekuensi: mengurangi eksplorasi yang justru menjadi peran LIHE.
2. Tempelkan `d` pada individu yang **memang** diseleksi — big male (lewat
   `Replacement`) atau female (offspring hanya diterima bila lebih baik).
3. Seleksi hanya atas gen `d`-nya, bukan atas posisinya: posisi small male tetap
   diterima semua, tetapi `dᵢ` yang menghasilkan perbaikan diwariskan lebih
   sering. Kompromi yang mempertahankan sifat eksploratif LIHE.

### Langkah kerja

- [ ] Perluas representasi individu: `k = (x₁…x_m, d, p_pref)`.
- [ ] Tentukan mekanisme variasi `d` — misalnya `d' = d·exp(τ·N(0,1))` dengan
      pembatas ke `(0,1)`, mengikuti pola self-adaptation σ pada ES.
- [ ] Putuskan jalur seleksi (salah satu dari tiga di atas) dan **catat
      alasannya**.
- [ ] Bandingkan terhadap Tahap 1, bukan terhadap `kma/`.
- [ ] Periksa distribusi `d` sepanjang run: kalau seluruh populasi menuju nilai
      yang sama, self-adaptation-nya bekerja; kalau acak, tekanan seleksinya tidak
      cukup.

**Keluaran**: KMA dengan `d` (dan mungkin `p`) yang self-adaptive dalam arti
ketat. Sekaligus menutup satu sumbu yang bahkan belum pernah diuji — B10: paper
berhipotesis `q = 3` lebih baik untuk multimodal, tetapi kode selalu `q = 2`.

---

## Tahap 3 — `n` self-adaptive lewat encoding tak langsung (opsional)

Kalau `n` tetap ingin dinaikkan ke tingkat self-adaptive, jangan mengkodekannya
langsung. Pakai pendekatan yang sudah ada literaturnya:

- **Lifetime / umur individu** — GAVaPS (Arabas, Michalewicz & Mulawka, 1994) dan
  APGA (Bäck, Eiben & van der Vaart, 2000). Tiap individu mendapat umur yang
  dihitung dari fitness relatifnya; `n` **muncul** sebagai akibat kelahiran dan
  kematian, tidak pernah disetel langsung. Cocok dengan struktur KMA karena
  micro-swarm bisa lahir dan mati sebagai unit kelipatan 5.
- **Agregasi preferensi** — tiap individu membawa `nᵢ`, dan `n` aktual adalah
  median atas individu yang bertahan. Secara formal self-adaptive, tetapi paling
  spekulatif dan paling lemah tekanan seleksinya.

- [ ] Prototipe skema lifetime pada tingkat micro-swarm.
- [ ] Bandingkan terhadap Tahap 1 dan Tahap 2.

---

## Protokol evaluasi

Berlaku untuk semua tahap.

| Butir | Ketentuan |
|---|---|
| Baseline | `kma-fixed/`, bukan `kma/` |
| Benchmark | shifted, sebaiknya juga rotated; laporkan pergeserannya |
| Anggaran | dihitung per panggilan fungsi objektif (A4 sudah diperbaiki) |
| Ulangan | 30 run independen, seed dicatat |
| Metrik | Avg, Std, Guaranty, MFE — dan **lintasan parameter** |
| Uji statistik | Wilcoxon rank-sum, α = 0,05, sebagaimana paper aslinya |
| Ablation | wajib: bandingkan terhadap parameter tetap yang disetel baik |

Harness yang sudah tersedia: `experiments/octave/` untuk sumber MATLAB,
`experiments/kma_py/` untuk eksperimen berskala besar.

---

## Hal yang bisa membatalkan hasil

Daftar periksa sebelum menyimpulkan bahwa varian baru lebih unggul.

- Optimum benchmark ada di titik origin → kemenangan bisa berasal dari bias, bukan
  dari mekanisme. **Ini yang terjadi pada paper aslinya.**
- Anggaran evaluasi tidak dihitung per panggilan objektif → varian dengan `n`
  kecil tampak unggul secara palsu.
- Tidak ada ablation terhadap parameter tetap → tidak bisa mengklaim bahwa
  adaptasinya yang berjasa.
- Lintasan parameter tidak diperiksa → skema bisa saja tidak pernah aktif, seperti
  F10 pada versi terbit: 75 generasi tanpa satu pun perubahan ukuran populasi.
- Parameter menempel pada entitas yang tidak diseleksi → yang didapat hanya angka
  acak yang menumpang, bukan self-adaptation.

---

## Rujukan

Periksa kembali detail sitasi sebelum dipakai di naskah.

- A.E. Eiben, R. Hinterding, Z. Michalewicz, *Parameter Control in Evolutionary
  Algorithms*, IEEE Transactions on Evolutionary Computation 3(2):124–141, 1999.
  — taksonomi tuning / deterministic / adaptive / self-adaptive.
- J. Arabas, Z. Michalewicz, J. Mulawka, *GAVaPS — a Genetic Algorithm with
  Varying Population Size*, IEEE CEC, 1994. — ukuran populasi lewat lifetime.
- T. Bäck, A.E. Eiben, N.A.L. van der Vaart, *An Empirical Study on GAs "Without
  Parameters"*, PPSN VI, 2000. — APGA.
- J. Brest dkk., *Self-Adapting Control Parameters in Differential Evolution*,
  IEEE TEC 10(6):646–657, 2006. — jDE, pola self-adaptation per individu.
- R. Tanabe, A.S. Fukunaga, *Improving the search performance of SHADE using
  linear population size reduction*, IEEE CEC, 2014. — contoh kendali `n` yang
  deterministic; ref [10] pada paper KMA.
- S. Suyanto, A.A. Ariyanto, A.F. Ariyanto, *Komodo Mlipir Algorithm*, Applied
  Soft Computing 114:108043, 2022. — objek studi.
