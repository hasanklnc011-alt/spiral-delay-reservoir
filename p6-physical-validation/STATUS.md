# P6 Başlangıç Durumu

Güncelleme: 2026-09-04

## Sonuç

P6 iskeleti ve ilk deterministik bileşen bütçesi kuruldu. Fiziksel kabul henüz
verilmedi; doğru başlangıç durumu `p6_accepted=false`'dur. P5 kör koşusu
çalıştırılmadı ve hiçbir P6 kararında skor geri beslemesi kullanılmadı.

## 2026-09-04 ilerleme — G1, G3-A ve G3-B

- G1 koşullu geçti: `343×180 nm` silicon strip, `n_g=4.01297`, proses penceresi
  `width=343±10 nm`, `thickness=180±5 nm`.
- G3-A geçti: lossless 4/8 µm straight referans m20/m25 yakınsaması sağlandı;
  fabricated propagation loss PDK/cutback girdisi olarak açık tutuldu.
- G3-B geçti: `R=10 µm` bend fine-mesh transmission `-0.00372 dB/90°`, worst
  reflection `-39.26 dB`; de-embedded faz yakınsaması `0.4459°`.
- `5 µm` pitch komşu-sarım kuplajı, 2.2 mm muhafazakâr paralel segmentte
  `<-127 dB` bulundu. Bu sınır exact centerline/GDS ile yeniden kontrol edilecek.
- P5 blind ve candidate-lock hash'leri değişmedi; kör koşu yeniden çalıştırılmadı.
- Sıradaki bağımlılık: exact spiral centerline/DRC, ardından G3-C progressive tap
  ve LO splitter modeli.

## G2 exact centerline

- Tek-seri Archimedean spiral GDS/CSV/SVG üretildi ve geri okunarak doğrulandı.
- GDS uzunluğu `142400.61041 µm`; hedefe bağıl hata `%0.000567`.
- Minimum eğrilik `10 µm`, pitch `5 µm`, edge gap `4.657 µm`, bbox
  `982.34×982.34 µm`, 20 tap ve kesintisiz dokuz GDS PATH parçası geçti.
- Exact dış-turn uzunluğu `2991.86 µm` ile adjacent-turn bound güncellendi;
  seçilmiş pitch sonucu `<-124.60 dB` ile geçiyor.

## G3-C yönlü-kuplör denemesi

- Uniform `200 nm` gap bölümü remote m20/m25 mode solve'da yakınsadı; 50:50
  merkez interaction uzunluğu `2.70022 µm`.
- Transition dahil iki seçilmiş 3D FDTD hücresi imbalance ve reflection kapılarını
  geçmedi. En iyi excess `0.106 dB` olsa da imbalance `7.85 dB`, merkez reflection
  `-11.83 dB` ve enerji artığı `%4.64`.
- G3-C fail-closed; uniform bölüm sonucu kabul edilmiş splitter/combiner gibi
  kullanılmayacak. Sıradaki tasarım MMI/Y-splitter veya foundry adiabatic coupler.

## G3-C alternatif splitter sonucu

- Simetrik Y-splitter balance/fazı geçti, ancak merkez reflection `-15.00 dB`,
  worst reflection `-9.27 dB` ve enerji artığı `%4.51`; reddedildi.
- Beş noktalı (`4/6/8/10/12 µm`) 1×2 MMI uzunluk taramasının tamamı
  fail-closed oldu. En iyi `10 µm` adayı `0.991 dB` merkez excess ve
  `-17.60 dB` merkez reflection verdi; kabul kapılarına yeterli değil.
- G3-C artık jenerik geometri taramasıyla ilerletilmeyecek; foundry-qualified
  splitter/tap S-parametresi ya da mode/EME-optimize yeni hücre gerektiriyor.
- No-cloud parity-mode ekranıyla `18.4056 µm` temel beat-length bulundu ve
  `8.8/9.2/9.6 µm` dar FDTD serisi koşuldu. En iyi `9.6 µm` adayı `0.611 dB`
  excess'e ulaştı, fakat reflection/energy kapılarında kaldı. Bundan sonraki
  G3-C adımı transition/topoloji yeniden tasarımı veya foundry S-parametresidir.
- Slot-opening Y redesign'inin ilk task'ı builder hatası nedeniyle kanıt dışı
  tutuldu. Düzeltilmiş v2 balance/faz/decay'i geçti; excess `0.498 dB`, merkez
  reflection `-13.11 dB` ve `%6.68` enerji artığıyla yine reddedildi.
- 80 µm adiabatic uzatma excess/energy'yi iyileştirdi, reflection'ı iyileştirmedi.
  Taper-only tanı `w→2w` giriş transition'ında `-9.58 dB` reflection buldu;
  sonraki topoloji bu width-doubling taper'ını kaldırmalı.

## G4 compact-model sonucu

- 10 PD × 3 slot routing geçti; `30 GHz` slot seçimi hızlı EO/switch,
  `10 kHz` thermal katman yalnızca statik trim olarak kilitlendi.
- `1.4 ns` diferansiyel gecikmede tüm `2° RMS` bütçe lazere ayrılırsa
  linewidth zarfı `138.5 kHz`.
- İdeal combiner varsayımında receiver'ın `4.5 mA` tepe photocurrent'ta
  lineer kalması gerekiyor; 50 GHz PD/TIA saturation kanıtı açık.
- Thermal zarf `395 mW` ortalama / `770 mW` maksimum; `800 mW` sınırındaki
  `30 mW` pay assumptions-only'dir. G4 fiziksel kabulü PDK/thermal solve bekliyor.

## G5 fail-closed bileşim

- Exact GDS rotası `372.91` eşdeğer 90° bend; fine FDTD ile compose edilen
  bend kaybı `1.386 dB`.
- `0.8 dB/cm` assumption-only propagation ile delay hattı `12.778 dB`,
  `0.8974 dB/cm`; stress zarfı içinde ama PDK/cutback olmadan fiziksel PASS değil.
- G3-C/G3-D splitter/combiner, hızlı switch ve PD/thermal girdileri eksik
  olduğundan G5 ve P6 kabulü fail-closed açık kaldı.

## G6 fiziksel kabul denetimi

- 11 kapının 5'i PASS; G3-C ve G3-D `FAIL/REDESIGN`, dört kapı OPEN.
- Nihai mevcut hüküm `NOT_PHYSICALLY_ACCEPTED`; bu bir P5 performans reddi değil,
  fiziksel bileşen kanıtının henüz tamamlanmadığı anlamına gelir.
- Ayrıntılı kanıt matrisi `G6-PHYSICAL-ACCEPTANCE.md` ve
  `runs/g6-acceptance-audit-v1.json` içindedir.

## Geçen başlangıç kapıları

- P5 blind JSON SHA-256:
  `b263292fd0226c10cc3b0096350176cb14771e258f2eacd89c2952ace9219028` — eşleşti.
- P5 candidate-lock SHA-256:
  `664904b350efaa84a65e5f57a5119042f196753ccd4e7e6d11e851395e5c247d` — eşleşti.
- `n_g=4`, 10 GBd ve 19 lag aritmetiği: `1.9 ns` ve `14.240141755 cm` — eşleşti.
- 30 feature, 10 PD × 3 slot routing snapshot'ı — eşleşti.
- Tidy3D `2.12.0` import ve yerel `td.Simulation` oluşturma — geçti;
  `cloud_called=false`.
- P6 unit/protokol testleri: `26/26` geçti.
- Bağımsız verifier turundaki 7 model/plan/provenance bulgusu kapatıldı.

## G1 yerel seed sonucu

450×220 nm silicon / SiO₂ seed kesiti Tidy3D 2.12.0 local mode solver ile
`15/20/25` steps-per-wavelength seviyelerinde koştu. Fundamental `n_g` sırasıyla
`4.21735 / 4.27472 / 4.26478` oldu; medium→fine fark `%0.233` ile `n_g` mesh
eşiğini geçti. Ancak `n_eff` farkı `0.08564` ve local solver subpixel averaging
kullanmadığı için yakınsama kapısı geçmedi.

Fine-mesh `n_g=4.26478`, 14.240141755 cm'de `2.02577 ns = 20.2577 sembol`
verir; kilitli 19 sembolden `%6.62` sapar. Medium/fine gridlerde higher-mode
proxy ayrıca üç guided mode işaret eder. Bu seed G1'i geçmedi. Güncel, hash'e
bağlı sonuç `runs/g1-local-seed-v2.json` içinde `g1_passed=false` olarak kaydedildi.

13 noktalı `1520–1580 nm` remote/subpixel ModeSolver adayı gerçek Tidy3D 2.12.0
nesnesi olarak bellekte serialize edildi. Source/config/payload hash'leri
`runs/g1-remote-subpixel-preflight-v1.json` içinde kilitli; preflight geçti,
başlangıç preflight'ında `upload_allowed=false`, `solve_allowed=false` idi.

Kullanıcının G1 upload/maliyet onayıyla aynı payload Tidy3D'ye draft olarak
yüklenip `0.0107155 FlexCredit` tahmini alındı. Task
`mo-e4a92867-2a30-4d8a-8e4b-8c53de716263` hâlâ `draft` durumunda ve
`solve_started=false`. Kanıt `runs/g1-upload-estimate-v1.json` içindedir.

## İlk analitik zarf — kanıt değil

- Geçici double-spiral: pitch `5 µm`, inner radius `20 µm`, keepout dahil
  yaklaşık `1.153 × 1.153 mm`, `1.329 mm²`.
- Varsayımsal bend loss toplamı `0.734 dB`; `0.8 dB/cm` propagation ile bileşik
  `0.852 dB/cm`. Bu yalnızca G3 öncesi tasarım zarfıdır.
- Lossless progressive tap oranları `1/20, 1/19, …, 1/2, 1`; tek-kaynak eş tap
  ideal division alt sınırı `13.010 dB`.
- Aynı-slot maksimum tap fanout `2`; ek ideal multicast division `3.010 dB`.
- En yüksek slot kol-bütçesi `u=1` referansında `85 mW`, gerçek `u≤0.5`
  sınırında `32.5 mW`. Bunlar lazer launch/wall-plug gücü değildir.
- Maksimum coherent differential delay `1.4 ns`; `2° RMS` bütçenin tamamı lazere
  ayrılırsa ilk linewidth zarfı yaklaşık `138.5 kHz`.
- Thermal varsayım: 30 statik trim için ortalama `395 mW`, maksimum `770 mW`;
  PDK/thermal solve olmadan kabul kanıtı değildir.
- 5 mW LO, `0.8 A/W` ile combiner öncesi `4 mA`, ideal 3-dB tek çıkışta
  `2 mA` photocurrent verir; PD/TIA saturation açıktır.

## Açık hard gate'ler

1. Foundry-qualified progressive tap/LO splitter kompleks S-matrisi; jenerik DC,
   Y-splitter ve ilk MMI ailesi reddedildi.
2. 2×2 coherent combiner kompleks S-matrisi ve pasif `S†S≤I` doğrulaması.
3. Fabricated propagation loss için PDK/cutback girdisi.
4. 30 GHz hızlı selector S-parametresi ve bandwidth kanıtı.
5. 50 GHz P5 uyumlu PD/TIA responsivity, noise, saturation ve lineerlik.
6. Laser shared-noise bütçesi, phase-shifter `PπL`, thermal crosstalk/time
   constant ve tam elektriksel/optik wall-plug güç defteri.

## Foundry/PDK seçim kapısı

Kamuya açık birincil foundry kaynakları incelendi. imec iSiPP50G ve Tower PH18
50G sınıfı aktif aygıtlar sunuyor, fakat yayımlanmış süreçleri `220 nm` Si ve
G1'in `180±5 nm` kilidiyle uyumsuz. AIM aktif/low-loss PDK gerekli bileşen
sınıflarını sunuyor; ancak nicel layer stack ve aygıt modelleri lisanslı PDK
erişimi gerektiriyor. Seçim iki yoldan biridir: gerçek bir aktif PDK seçip G1–G4'ü
yeniden açmak veya `343×180 nm` kesiti custom-process ön tasarımı olarak korumak.
Kayıt: `PDK-SELECTION.md` ve `configs/pdk-selection-v1.json`.

Hasan ikinci yolu seçti: `343×180 nm` kesit custom-process ön tasarımı olarak
korunacak. Hazır 220 nm PDK göçü yapılmayacak. Gerekli process manifest, cutback,
kompleks S-parametre, 30 GHz switch, 50 GHz PD/TIA ve `30×30` thermal test
sözleşmesi `CUSTOM-PROCESS-VALIDATION.md` içinde donduruldu.

## Sıradaki tek adım

G3-C ve G3-D jenerik splitter/MMI yolları doğrulanmış başarısız sonuçlarla durdu.
Sonraki teknik adım foundry-qualified splitter/combiner kompleks S-parametrelerini
edinmek veya ayrı inverse-design/transition-redesign hücresi açmaktır. Bununla
birlikte propagation PDK/cutback, hızlı switch, PD/TIA ve thermal fiziksel girdileri
gelmeden G5 fail-closed kalır.

## G3-C union-branch Y kapanış deneyi

- Width-doubling içermeyen, `80 µm` sabit-kol-genişlikli union-branch Y için
  kilitli draft tahmini `0.30434 FC`; aynı task başarıyla tamamlandı.
- Excess `0.403 dB`, merkez/worst reflection `-12.89/-12.23 dB`, enerji artığı
  `%5.14` ve final decay `4.08e-6`: dört nominal kapının hiçbiri geçmedi.
- Jenerik FDTD geometri taraması durduruldu. G3-C `FAIL/REDESIGN`; sonraki
  yetkili girdi foundry-qualified kompleks S-matris veya ayrı EME/inverse-design
  hücresidir. P5 blind yeniden çalıştırılmadı.

## G3-D iki-kaynak MMI ve EME sonucu

- `0.8575 µm` genişlikli 2×2 MMI, iki bağımsız kaynaklı broadband FDTD'de
  `0.09583 FC` gerçek maliyet ve yaklaşık `5.9e-8` decay ile tamamlandı.
- Merkez imbalance `20.73 dB`, worst excess `1.584 dB`, reflection `-11.61 dB`
  ve quadrature error `74.41°`; geometri reddedildi ve convergence'a taşınmadı.
- `2–14 µm` EME uzunluk ekranında en iyi birleşik aday `11.0 µm` oldu; imbalance
  `0.365 dB` olsa da excess `4.615 dB`, reflection `-11.18 dB` ve quadrature
  error `79.34°` nedeniyle FDTD'ye yükseltilmedi.
- G3-D güncel durumu `FAIL/REDESIGN`; çözülmüş kaynaklar yeniden başlatılmadı ve
  P5 blind yeniden çalıştırılmadı.
- Fizik-temelli `1.2/1.4 µm`, `3–24 µm` EME ekranı da geçmedi. En iyi
  `1.4×23.75 µm` aday excess `4.570 dB`, imbalance `0.756 dB`, quadrature error
  `17.89°` ve reflection `-10.31 dB` verdi; broadband FDTD'ye yükseltilmedi.

## Custom-process inverse-design kapanışı

- ID0 ve hash-kilitli ID1 maliyet kapısı geçti. Olası başarısız forward maliyetleri
  rezerve edilerek splitter/combiner üçer kaydedilmiş adımla tamamlandı.
- Binary ID2 toplam tahmini `0.16920 FC`; üç broadband solve tamamlandı.
- Splitter: worst excess `3.494 dB`, imbalance `0.348 dB`, reflection `-16.22 dB`.
- Combiner: worst excess `5.466 dB`, imbalance `5.160 dB`, quadrature `15.62°`,
  reflection `-15.42 dB`, max singular value `0.639`.
- Her iki seed ID2'de başarısız oldu; ID3 çalıştırılmadı. G6 sayacı değişmedi:
  `5/11 PASS`, G3-C/G3-D `FAIL/REDESIGN`, dört fiziksel kapı `OPEN`.
- Sıradaki teknik seçenek, ucuz effective-index continuation ile yeni seed üretmek
  veya custom foundry'den qualified kompleks S-parametre almaktır. P5 blind
  yeniden çalıştırılmadı.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Photonic Reservoir proje merkezi]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/P6-PROTOCOL|P6 protokolü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/COMPONENT-MODEL|Bileşen modeli]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/EM-FDTD-PLAN|EM/FDTD planı]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/PDK-SELECTION|PDK seçim kapısı]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/CUSTOM-PROCESS-VALIDATION|Custom-process doğrulama planı]]
- [[🏰 300-Projects/Photonic-Reservoir/p5-publication/RESULTS|P5 dondurulmuş sonucu]]
