# P6 — Fiziksel Doğrulama

P6, P5'te kilitlenmiş 30-kanal / 10-PD × 3-slot coherent readout adayının
fiziksel kanıt borcunu kapatır. P5 kör sonucu bu fazın optimizasyon hedefi değildir;
yeniden çalıştırılmaz ve P6 kararlarına geri beslenmez.

## Bu klasörde ne var?

- `P6-PROTOCOL.md`: amaç, kapsam, bağımlılık grafiği, kapılar ve durma koşulları.
- `COMPONENT-MODEL.md`: delay, spiral, kayıp, optik güç, faz ve termal denklemler.
- `EM-FDTD-PLAN.md`: Tidy3D 2.12.0 için seçilmiş, maliyet-kapılı EM planı.
- `G1-ACCEPTANCE.md`: kabul edilen kesit, yakınsama ve zorunlu proses penceresi.
- `configs/baseline-v1.json`: P5'ten dondurulan girdiler ve P6'nın açık varsayımları.
- `component_model.py`: deterministik bileşen/alan/güç bütçesi hesabı.
- `em_plan.py`: makine-okunur EM iş sırası ve yerel Tidy3D sürüm kapısı.
- `g1_mode_solver.py`: provisional kesit için yalnızca yerel, no-cloud mode solve.
- `g1_remote_preflight.py`: 13 noktalı remote/subpixel ModeSolver payload'ını
  upload etmeden serialize/hash eden kredi-kapılı preflight.
- `g1_cloud_gate.py`: kilitli payload'ı yalnız upload edip maliyet tahmini alır;
  solve/start yolu içermez ve açık kullanıcı onayı bayrağı ister.
- `tests/`: kör teste dokunmadan protokol, birim ve model tutarlılık testleri.

## İlk durum

P6 başlatıldı, fakat fiziksel kabul henüz verilmedi. İlk hard gate, seçilecek
fotonik kesitin `n_g = 4.0` değerini doğrulamasıdır. Salt-okunur eski
`tidy3d_small_ring` SiN 800×400 nm sonucu `n_g = 2.1073186` verdiğinden bu geometri
14.24 cm / 19-sembol delay için doğrudan kullanılamaz.

Yerel kontroller:

```powershell
python component_model.py --check-provenance
python -m unittest discover -s tests -v
"C:\Users\hasan\OneDrive\Desktop\eski dosyalarım\tidy3d_small_ring\.venv-tidy3d\Scripts\python.exe" em_plan.py --check-local
"C:\Users\hasan\OneDrive\Desktop\eski dosyalarım\tidy3d_small_ring\.venv-tidy3d\Scripts\python.exe" g1_mode_solver.py --solve-local --mesh 20
"C:\Users\hasan\OneDrive\Desktop\eski dosyalarım\tidy3d_small_ring\.venv-tidy3d\Scripts\python.exe" g1_remote_preflight.py
```

`em_plan.py --check-local` yalnızca import/sürüm ve minimal in-memory simulation
kontrolü yapar. `g1_mode_solver.py --solve-local` gerçek bir yerel eigensolve yapar;
`g1_remote_preflight.py` de 13-nokta payload'ı yalnız bellekte serialize/hash eder.
Üçü de bulut işi göndermez veya kredi tüketmez.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Photonic Reservoir proje merkezi]]
- [[🏰 300-Projects/Photonic-Reservoir/p5-publication/RESULTS|P5 tek kör test sonucu]]
- [[🏰 300-Projects/Photonic-Reservoir/MODEL-AND-ACCEPTANCE|Model ve kabul protokolü]]
- [[🏰 300-Projects/Photonic-Reservoir/HANDOFF|Güncel handoff]]
- [[🏰 300-Projects/3 halkalı Ring/Tidy3D-Small-Ring|Salt-okunur Tidy3D referansı]]
