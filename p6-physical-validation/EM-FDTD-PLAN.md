# P6 Seçilmiş EM / FDTD Doğrulama Planı

## İlke

14.24 cm devre tam 3D FDTD ile çözülmez. Kısa bileşen hücrelerinden
S-parametre, `n_g`, excess loss, reflection ve phase response çıkarılır; tam
devre `component_model.py` içinde compose edilir. Tidy3D job sırası bağımlılık
kapılıdır.

## G1 — Kesit ve mode solve (ilk hard gate)

- Başlangıç tohumu: 1550 nm'de 450×220 nm silicon-strip / SiO₂ cladding.
  Bu kabul edilmiş platform değil, `n_g≈4` hipotezini sınayan ilk düşük-maliyetli noktadır
  ve ayrı SOI/Lumerical iletim hattından sonuç devralmaz.
- Amaç: final platform/kesitte TE0 `n_eff`, `n_g`, mode area ve higher-mode margin.
- Sweep: 1520–1580 nm'de 13 nokta; nominalden sonra `w=430/450/470 nm` ve
  `t=210/220/230 nm` tek-faktör fabrication köşeleri.
- Frekans: 1550 nm merkez ve P5'in fiziksel bant iddiasına uygun dar grid.
- Yakınsama: transverse span/PML ve mesh için en az iki sıkılaştırma;
  `|Δn_g|/n_g < 0.5%` ve `|Δn_eff| < 1e-3`.
- Kabul: 14.240141755 cm'nin delay'i `1.9 ns ±2%`; aksi halde G2/G3 durur.

Eski 800×400 nm SiN sonucu (`n_g=2.1073186`) yalnızca regression/reference'tır
ve bu kapıyı geçmez.

## G3-A — Straight reference / de-embedding

- Amaç: port normalization, transition loss ve phase reference.
- Geometri: aynı portlarla iki kısa düz uzunluk.
- Başlangıç 3D zarfı: yaklaşık `16×4×3 µm`, hedef `2–6M` hücre.
- Kaynak: TE0 ModeSource; monitor: iki yönlü ModeMonitor/FluxMonitor.
- Çıktı: kompleks `S21`, `S11`, de-embedded phase/length.
- Not: ideal pürüzsüz FDTD sonucu fabricated propagation loss kanıtı değildir.
- Kabul: energy residual `<1%`, reflection `<-30 dB`, mesh değişiminde
  insertion `0.02 dB` ve phase `0.5°` içinde.

## G3-B — Bend hücresi

- Amaç: minimum-radius adayında radiation/mode-conversion loss.
- Tarama: `R=10/20/30/50 µm`, pitch `3/4/5/6 µm`; önce 2.5D/effective-index
  veya mode/EME eleme, sonra yalnızca worst/final noktada 3D FDTD.
- Kaynak/monitor: straight reference ile aynı TE0 portlar; 90° bend de-embed edilir.
- Çıktı: loss/90°, reflection, TE0→higher-mode leakage, phase.
- Kabul: spiral toplamıyla birlikte propagation+bend `≤1 dB/cm` P5 stress zarfı.
- Ayrı temsilî iki-paralel-turn hücresi: pitch'te adjacent-turn coupling/crosstalk;
  tam spiral FDTD yerine en kötü paralel etkileşim uzunluğu compact modele taşınır.
- Kabul: full paralel etkileşim uzunluğuna compose edilmiş crosstalk `<-30 dB`.

## G3-C1 — Progressive signal tap

- Amaç: signal-tap ve LO dağıtımı için split oranı/excess loss.
- Kaynak: tek TE0 input; iki output ModeMonitor ve input reflection monitor.
- Sweep: progressive-tap `κ_k` oranlarını temsil eden seçilmiş düşük/orta/yüksek
  coupling noktaları, final bandwidth ve fabrication tolerance; 19 hücre kopyası FDTD edilmez.
- Çıktı: kompleks 3-port S-matrisi, hedef `κ` sapması, excess loss,
  reflection ve phase.
- Kabul: kasıtlı asimetrik tap'e 50:50 imbalance metriği uygulanmaz. Mutlak
  `|κ_meas-κ_target|≤0.01`, göreli hata `≤%5`, excess `≤0.2 dB/cell`,
  reflection `<-30 dB`; full 20-tap power solve ayrı geçer.

## G3-C2 — 50:50 LO splitter

- Amaç: 10 coherent kola LO dağıtımı için dengeli 1×2 hücre.
- Kaynak/monitor: bir TE0 input, iki output ve input reflection modal portları.
- Kabul: `κ=0.5`, excess `≤0.2 dB/stage`, imbalance `≤0.5 dB`, phase mismatch
  `≤2°`, reflection `<-30 dB`.

## G3-D — 2×2 coherent combiner / MMI

- Amaç: reciprocal splitter/combiner ve square-law çapraz terimini doğrulamak.
- İki bağımsız port excitation ile kompleks S-matrisi çıkarılır.
- Faz kontrolü: compact S-matriste `0°/90°/180°/270°` iki-giriş compose;
  gereksiz dört ayrı FDTD coherent-source job'u koşulmaz.
- Çıktı: ideal 3.0103 dB tek-çıkış bölünmesinden ayrı excess insertion,
  imbalance, quadrature error, reflection/crosstalk,
  `|E1 + E2 exp(jφ)|²` uyumu.
- Kabul: hedef excess insertion `≤0.5 dB`, hard excess üst sınır `≤1.5 dB`,
  imbalance `≤0.5 dB`, phase error `≤5°`,
  mesh farkı `≤0.02 dB / 0.5°`; pasif S-matris için en büyük tekil değer
  sayısal tolerans içinde `≤1`.

## G4 — Phase shifter, PD ve thermal

- Optik phase-shifter kesiti: mode-solver ile `dn_eff/dT` veya PDK perturbation
  datasından `PπL`; yalnız optik insertion/reflection FDTD ile kontrol edilir.
- Heater thermal time constant/crosstalk: thermal solver, PDK veya ölçüm; FDTD değil.
- 30 GHz slot switching: EO aygıt S-parameter/bandwidth modeli; thermo-optic değil.
- PD: P5 eşlemesi için 50 GHz; minimum sistem ihtiyacı için 15 GHz ayrı raporlanır.
  Responsivity/bandwidth/noise/saturation için PDK veya deneysel compact model;
  yalnız optik absorber coupling gerekiyorsa ayrı EM hücresi.

## Maliyet ve gönderim kapısı

1. Her case yerelde serialize/validate edilir.
2. Tidy3D `estimate_cost` sonucu run manifest'ine yazılır.
3. Mode/2.5D/EME ile elenebilen sweep 3D FDTD'ye gönderilmez.
4. Nominal coarse mesh geçmeden fine mesh veya tolerance batch açılmaz.
5. Kullanıcı kredi onayı olmadan `web.run` çağrılmaz.
6. Job adı `p6_<gate>_<component>_<variant>_<mesh>` kalıbını kullanır.

Geçici maliyet durma eşikleri kullanıcı bütçesiyle değiştirilene kadar pilot için
`<0.5 FlexCredit/source`, nominal suite için `<3`, convergence+corner toplamı için
`<10`'dur. Bunlar harcama yetkisi değildir. Standart hücre `20M`, bend `40M` grid
cell'i aşarsa domain azaltılır veya EME'ye dönülür.

Yakınsama sırası: `min_steps_per_wvl=15/20/25`, kritik gap/tipte `10–15 nm`
override; PML padding `1.0/1.5/2.0 µm`; run-time `+%50`; shutoff `1e-6→1e-7`.
Kabul edilen son iki mesh arasında IL `<0.02 dB`, phase `<0.5°`, imbalance
`<0.05 dB` ve `|S|` değişimi `<%1` olmalıdır. Buradaki imbalance yakınsaması,
LO splitter/combiner için mutlak `≤0.5 dB` performans kapısından ayrıdır.

## Kanıt kaydı

Her accepted case: Tidy3D `2.12.0`, config/source SHA-256, task ID, tahmini/gerçek
kredi, grid cell sayısı, shutoff, port normalization, convergence delta ve ölçülen
S-parametreleri taşır. Ham `.hdf5` bu klasörde `runs/` altında tutulur; eski
Tidy3D `results/` alanına yazılmaz.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/P6-PROTOCOL|P6 protokolü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/COMPONENT-MODEL|Bileşen modeli]]
- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Proje merkezi]]
- [[🏰 300-Projects/3 halkalı Ring/Tidy3D-Small-Ring|Eski Tidy3D referansı]]
