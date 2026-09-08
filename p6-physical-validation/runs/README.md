# P6 Run Kayıtları

Bu klasör yalnızca P6 bileşen/EM doğrulama kayıtlarını tutar. P5 blind
sonucu buraya kopyalanmaz veya yeniden üretilmez.

- `g1-local-seed-v1.json`: 450×220 nm provisional high-index strip için Tidy3D
  2.12.0 local mode-solver ilk mesh kontrolü; tarihsel kayıttır.
- `g1-local-seed-v2.json`: güncel solver/config hash'lerine bağlı, mode area ve
  higher-mode proxy içeren tekrar üretim; cloud çağrısı yoktur ve `g1_passed=false`.
- `g1-remote-subpixel-preflight-v1.json`: 13 noktalı ModeSolver payload'ının
  source/config/serialization hash'leri; upload ve solve kapalıdır.
- `g1-upload-estimate-v1.json`: kilitli payload'ın Tidy3D draft task ID'si ve
  `0.0107155 FC` maliyet tahmini; `solve_started=false`.
- `g1-remote-subpixel-result-v1.json` / `.hdf5`: onaylı 450×220 nm remote
  subpixel sonucu; `n_g=4.25685`, tek TE-like mod, delay hatası `%6.42`, G1 fail.
- `g1-candidate-batch-result-v1.json`: dört adayın remote merkez-frekans taraması;
  üç aday nominal kapıyı geçti, 343×180 nm hedef-braket merkezi seçildi.
- `g1-selected-validation-result-v1.json`: nominal üç-mesh ve ±10 nm width/height;
  nominal/width geçti, ±10 nm thickness geçmedi.
- `g1-thickness-refinement-result-v1.json`: açık proses şartı `180±5 nm` iki
  köşede geçti; G1 kabulü `configs/g1-accepted-v1.json` içinde kilitlendi.
- `g1-220nm-pdk-migration-local-probe-v1.json`: seçilmeyen 220 nm PDK göçünün
  ücretsiz/no-subpixel etki tanısı; `310×220 nm` aday `%10.33` mesh span ile
  yakınsamadı ve hiçbir G1 kabulü üretmedi.
- `g3a-straight-result-v1.json` ve `g3a-straight-convergence-result-v1.json`:
  kompleks `Li1993_293K` malzemeli reddedilmiş tarihsel seri; bulk absorption
  enerji-artığı metriğine karıştığı için G3-A kabul kanıtı değildir.
- `g3a-straight-lossless-result-v2.json`: lossless scattering referansının dört
  remote 3D FDTD çözümü; 4/8 µm ve 20/25 mesh yakınsaması geçti. Fabricated
  propagation loss harici PDK/cutback girdisi olarak tutulur.
- `g3b-bend-r20-result-v1.json` ve `v2.json`: geniş bant yansıma kapısını
  kaçıran, reddedilmiş R=20 µm bend pilotları.
- `g3b-bend-r10-result-v3.json`: seçilmiş R=10 µm coarse pilot; bütün performans
  kapılarını geçti.
- `g3b-bend-r10-deembedded-fine-convergence-v1.json`: m20/m25 straight-reference
  de-embedded faz yakınsaması; G3-B bend kabulünün ana kanıtı.
- `g3b-adjacent-turn-supermode-v2.json`: 5 µm pitch even/odd TE kuplaj üst sınırı;
  exact dış-turn `2.992 mm` segmentinde `<-124.6 dB`.
- `g3c-coupler-mode-result-v1.json`: 200 nm-gap uniform coupling bölümünün remote
  m20/m25 sonucu; mode bölümü yakınsak, 50:50 merkez uzunluğu `2.70022 µm`.
- `g3c-coupler-fdtd-result-v1/v2.json`: transition dahil iki reddedilmiş 3D hücre;
  imbalance/reflection/energy/decay kapıları nedeniyle G3-C kabulü değildir.
- `g3c-y-splitter-result-v1.json`: dengeli fakat reflection ve enerji artığı
  kapılarını kaçıran, reddedilmiş adiabatik Y-splitter pilotu.
- `g3c-mmi-sweep-estimate/result-v1.json`: `4–12 µm` beş uzunluklu 1×2 MMI
  taraması; hiçbir aday excess/reflection/energy kapılarını birlikte geçmedi.
- `g3cd-mmi-mode-screen-result-v1.json` ve `g3cd-mmi-targeted-*`: no-cloud
  parity-mode beat-length ekranı ve buna dayalı `8.8/9.2/9.6 µm` FDTD serisi;
  excess iyileşti fakat reflection/energy kapıları nedeniyle yine reddedildi.
- `g3c-slot-y-result-v1.json`: polygon builder kusuru nedeniyle fiziksel kanıt
  sayılmayan `INVALID_GEOMETRY` task; maliyet ve ham HDF5 korunur.
- `g3c-slot-y-result-v2.json`: düzeltilmiş simetrik slot-opening transition;
  balance/faz/decay geçti, excess/reflection/energy nedeniyle reddedildi.
- `g3c-slot-y-result-v3.json`: 80 µm yarım-domain adiabatic-length adayı;
  excess/energy iyileşti, reflection ve decay geçmedi.
- `g3c-slot-y-taper-result-v1.json`: `w→2w` taper-only tanısı; reflection
  `-9.58 dB`. Multimode output normalization pasifliği ihlal ettiğinden yalnız
  giriş reflection metriği kanıt olarak kullanılır.
- `g3c-union-y-estimate-v1.json`: width-doubling içermeyen `80 µm` union-branch
  Y için kilitli draft; tahmin `0.30434 FC`, `solve_started=false`.
- `g3c-union-y-result-v1.json` / `.hdf5`: aynı task/hash üzerinde tamamlanan
  pilot; excess `0.403 dB`, worst reflection `-12.23 dB`, enerji artığı `%5.14`
  ve final decay `4.08e-6` nedeniyle reddedildi.
- `g3d-mmi-preflight/estimate/result-v1.json` ve iki kaynak `.hdf5`: resmi 2×2
  MMI tohumunun `343×180 nm` kesite ölçeklenmiş broadband pilotu; iki bağımsız
  excitation tamamlandı, fakat imbalance/excess/reflection/faz kapıları geçmedi.
- `g3d-mmi-eme-preflight/estimate/screen-result-v1.json` ve `.hdf5`: aynı dar
  MMI için `2–14 µm` EME uzunluk ekranı; en iyi `11.0 µm` aday da optik kapıları
  birlikte geçmedi ve FDTD'ye yükseltilmedi.
- `g3d-mmi-eme-width-preflight/estimate/screen-result-v1.json` ve iki `.hdf5`:
  mode tanısıyla seçilmiş `1.2/1.4 µm` gövdelerin `3–24 µm` EME ekranı; toplam
  `0.49937 FC`. İki genişlik de geçmedi, jenerik MMI yolu durduruldu.
- `inverse-design-id0-preflight-v1.json` ve `inverse-design-simulation-preflight-v1.json`:
  custom-process topology region, port ve kompleks objective için no-cloud kilitler.
- `inverse-design-id1-estimate-v1.json`, iki ID1 `.json/.hdf5`: bütçe-kilitli
  coarse 3D seed optimizasyonları; ID1 kabul üretmez.
- `inverse-design-id2-binary-preflight-v1.json`: cache→density→binary zinciri,
  özel ortam verisini de kapsayan güçlü simülasyon hash'leri ve feature proxy.
- `inverse-design-id2-estimate-v1.json`: üç binary broadband solve için
  `0.16920 FC` tahmin; kayıt anında tüm task'lar draft.
- `inverse-design-id2-binary-fdtd-v1.json` ve üç `.hdf5`: splitter ve iki-kaynak
  combiner binary doğrulaması; iki cihaz da ID2 metriklerinde `FAIL/REDESIGN`.
- `g4-compact-validation-result-v1.json`: 10 PD × 3 slot, faz-koherens,
  PD/TIA lineer akım gereksinimi ve termal güç defteri; model semantiği geçti,
  PDK/thermal/receiver fiziksel kapıları açık kaldı.
- `g5-composition-result-v1.json`: kabul edilmiş layout/bend kanıtları ve
  assumption-only propagation ile tam-link bileşim; eksik G3-C/G3-D/G4 girdileri
  gizlenmeden `g5_composition_complete=false` kaldı.
- `g6-acceptance-audit-v1.json`: 11 fiziksel kapının makine-okunur nihai denetimi;
  5 PASS, G3-C/G3-D FAIL/REDESIGN ve dört OPEN ile `NOT_PHYSICALLY_ACCEPTED`.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/STATUS|P6 durum]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/EM-FDTD-PLAN|EM/FDTD planı]]
- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Proje merkezi]]
