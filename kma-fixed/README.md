# kma-fixed — KMA v1.0.0 dengan perbaikan minimal A1–A4

Salinan kode di `../kma/` **tidak diubah** dan tetap menjadi baseline (rilis asli
Suyanto et al., BSD 3-clause, lihat `license.txt`). Folder ini memuat salinan yang
sama dengan **empat perbaikan minimal** yang didokumentasikan di `../TEMUAN.md`.

Setiap perubahan diberi tanda komentar `FIX Ax` di dalam kode. Diff lengkap ada di
`A1-A4.patch`.

## Yang diperbaiki

| Kode | Berkas | Perubahan |
|---|---|---|
| **A1** | `Evaluation.m` | Blok Foxholes yang berlabel `case 16` diubah menjadi `case 14`. Sebelumnya F14 tidak cocok dengan case mana pun (`fx` tidak ter-assign → error) dan F16 diam-diam menjalankan Foxholes, bukan Six Hump Camel. |
| **A2** | `KMA2D.m`, `KMA3D.m` | Indeks baris `AllHQ`/`AllHQFX` pada tahap kedua: `((ind-1)/SwarmSize)*NumBM + 1`, bukan `ind`. Sebelumnya array tumbuh dengan baris nol sehingga individu semu di titik origin berfitness 0 masuk ke himpunan *high-quality*. |
| **A3** | `KMA2D.m`, `KMA3D.m` | Tanda kurung pada kecepatan mlipir: `rand .* ((HQ - SM) .* B)` sesuai Eq. (8). Presedensi MATLAB membuat baris lama dievaluasi sebagai `rand.*(HQ.*B) - (SM.*B)`, yaitu kontraksi menuju origin. |
| **A4** | `Evaluation.m`, `KMA2D.m`, `KMA3D.m` | `NumEva` dihitung di dalam `Evaluation` (satu panggilan = satu evaluasi), bukan `+PopSize` per generasi. Populasi awal dan 195 individu `ConsPop` tahap dua kini ikut terhitung; mesh permukaan 3D pada `KMA3D` sengaja dikecualikan karena itu untuk plot, bukan pencarian. |

## Yang sengaja TIDAK diubah

Penyimpangan B1–B12 di `../TEMUAN.md` (inisialisasi di sudut, struktur micro-swarm
tahap dua, `MutRadius = 0.5`, ambang improve/stagnasi `> 2`, `MutRadius` ganda di
`Reposition`, dsb.) **dibiarkan apa adanya**. Tujuan folder ini adalah mengisolasi
efek A1–A4, bukan menulis ulang algoritmanya.

## Cara menjalankan

`Main2D.m`/`Main3D.m` memanggil `KMA2D`/`KMA3D` dengan nama yang sama seperti
versi asli, jadi **hanya satu dari kedua folder** yang boleh ada di MATLAB path
pada satu waktu:

```matlab
cd kma-fixed        % atau: cd kma  untuk menjalankan baseline
Main2D
```

Perbaikan ini belum pernah dieksekusi di MATLAB/Octave (tidak tersedia di mesin
tempat audit dilakukan) — kebenarannya diverifikasi lewat pembacaan kode dan lewat
replika Python di `../experiments/`. Jalankan sekali di MATLAB sebelum dipakai
untuk publikasi.
