# SiN Three-Ring Photonic Reservoir

Bu paket, FDTD ile kalibre edilmiş SiN mikro-ring parametrelerinden başlayarak
üç-ring temporal coupled-mode reservoir deneylerini tekrarlanabilir biçimde
çalıştırır. Eski `tidy3d_small_ring` ve `photonic_reservoir` klasörleri salt-okunur
kanıt kaynağıdır; bu paket onların üzerine yazmaz.

## Bilimsel iddia seviyeleri

- `TCMT`: yalnız reduced-order zaman dinamiği.
- `FDTD-calibrated TCMT`: parametreleri FDTD'den çıkarılmış TCMT.
- `dynamic FDTD validation`: kısa zaman-alanı FDTD iziyle doğrulanmış model.

Statik bir FDTD spektrumuna uydurulan TCMT benchmarkı doğrudan FDTD benchmarkı
olarak adlandırılmaz. Fiziksel Kerr koşuları `kerr_sensitivity_multiplier=1` kullanır.

## Çalıştırma

Tekrarlanabilir geliştirme ortamını OneDrive dışında oluştur:

```powershell
$prVenv = Join-Path $env:LOCALAPPDATA 'MayOS\venvs\photonic-reservoir-py314'
py -3.14 -m venv $prVenv
& "$prVenv\Scripts\python.exe" -m pip install -r requirements-lock.txt
& "$prVenv\Scripts\python.exe" -m pip install -e . --no-deps
$env:PYTHONPATH = "$PWD\src"
& "$prVenv\Scripts\python.exe" -m unittest discover -s tests -v
```

Test paketi standart kütüphanedeki `unittest` tabanlıdır; `pytest` gerekmez. Hızlı test için mevcut
Python ortamında aşağıdaki kanonik komut da kullanılabilir:

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m unittest discover -s tests -v
python -m photonic_reservoir run --config configs/smoke.json
python -m photonic_reservoir evidence `
  --source "C:\Users\hasan\OneDrive\Desktop\eski dosyalarım\tidy3d_small_ring" `
  --output evidence/legacy_tidy3d_manifest.json
```

`configs/publication_narma10.json`, test setini model seçiminde kullanmayan sabit
10-seed yayın protokolüdür. Cloud FDTD koşusu ancak run özetindeki
`fdtd_cloud_gate_open=true` olduğunda açılır.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Photonic Reservoir proje hafızası]]
- [[🏰 300-Projects/Photonic-Reservoir/MRR-RNN-Literatur-Taramasi|MRR RNN literatür taraması]]
- [[🏰 300-Projects/3 halkalı Ring/Tidy3D-Small-Ring|Tidy3D Small-Ring FDTD]]
