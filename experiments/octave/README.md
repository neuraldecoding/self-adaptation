# Verifikasi dengan GNU Octave

Menjalankan sumber MATLAB di `kma/` dan `kma-fixed/` **tanpa modifikasi apa pun**,
untuk memeriksa silang temuan yang diperoleh lewat port Python.

## Menyiapkan Octave tanpa root

MATLAB tidak tersedia dan `sudo` butuh password, jadi Octave dipasang dari
conda-forge ke direktori pengguna:

```bash
mkdir -p ~/.local/micromamba && cd ~/.local/micromamba
curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj bin/micromamba
export MAMBA_ROOT_PREFIX=~/.local/micromamba
./bin/micromamba create -y -n oct -c conda-forge octave
```

Jalankan selalu lewat `micromamba run`, bukan dengan menaruh `bin/` di `PATH`
saja — tanpa itu `OCTAVE_HOME` tidak terpasang dan Octave tidak menemukan pustaka
m-file bawaannya (`fileparts` dan kawan-kawan hilang).

```bash
export MAMBA_ROOT_PREFIX=~/.local/micromamba
~/.local/micromamba/bin/micromamba run -n oct octave-cli --version
```

Menghapusnya cukup dengan `rm -rf ~/.local/micromamba`.

## Isi direktori

| Berkas | Kegunaan |
|---|---|
| `run_one.m` | Menjalankan satu konfigurasi secara headless: `octave-cli run_one.m <codedir> <FunctionID> <Dimension> <seed>`. Memakai `KMA2D` (bukan `KMA3D`, yang membuka figure). |
| `sweep.sh` | Sweep pembanding `kma/` vs `kma-fixed/` untuk F1–F13 (dim 50) plus F14 dan F16, seed 1–3 — 90 run, ~25 menit. Tanpa argumen menjalankan semuanya; `./sweep.sh 2 3 4` hanya menjalankan fungsi berdimensi tinggi yang disebut. Keluaran ke stdout, alihkan ke `../results/octave_verification.txt`. |
| `allhq_index_demo.m` | Memutar ulang pengindeksan baris `AllHQ` tahap dua (temuan A2) dengan ukuran sebenarnya, memakai semantik array Octave/MATLAB. |
| `random.m` | **Shim khusus Octave.** `kma/levy.m` memanggil `random('Normal',…)` dari Statistics and Machine Learning Toolbox milik MATLAB; di Octave fungsi itu hanya ada lewat paket `statistics`. Shim ini mengimplementasikan persis satu bentuk panggilan yang dibutuhkan `levy.m`, yaitu `mu + sigma.*randn(n,m)`. **Jangan pernah menaruhnya di path MATLAB.** |

## Menjalankan

```bash
./sweep.sh > ../results/octave_verification.txt
export MAMBA_ROOT_PREFIX=~/.local/micromamba
~/.local/micromamba/bin/micromamba run -n oct octave-cli allhq_index_demo.m
```

Ringkasan hasilnya ada di `../../TEMUAN.md` §E.0.
