# P6 Fiziksel Doğrulama Protokolü

## Amaç

P5'te dondurulan coherent-delay adayını; 14.240141755 cm delay hattı, spiral
floorplan, bend/splitter/combiner kayıpları, 10 coherent receiver kolu,
photodiode, faz kontrolü ve termal güç açısından bileşen seviyesinde sınamak.

## Kapsam

- 20 tap (`0…19`) ve 10 GBd için 19 sembollük maksimum delay.
- 30 kilitli özelliğin 10 PD × 3 slot fiziksel eşlemesi.
- Tam layout yerine izlenebilir spiral/floorplan tahmini ve bileşen sayımı.
- Seçilmiş kısa bileşenlerde mode-solver ve FDTD/EM doğrulaması.
- PDK/ölçüm gerektiren propagation loss, PD ve heater niceliklerini ayrı kanıt sınıfında tutmak.

## Kapsam dışı

- P5 kör koşusunu veya seed 179…229 verilerini yeniden çalıştırmak.
- Kör NMSE'ye göre kanal, güç, delay, faz veya geometri tuning'i.
- 14.24 cm yapının tamamını brute-force 3D FDTD ile çözmek.
- `legacy-three-ring/` ya da eski `tidy3d_small_ring` dosyalarını değiştirmek.
- EM simülasyonunu fabricated-device veya tape-out kanıtı diye sunmak.

## Kanonik girdiler ve yazma sınırı

- P5 sonucu: `p5-publication/runs/blind-v2.json`, salt-okunur.
- P5 aday kilidi: `p5-publication/candidate-lock-v2.json`, salt-okunur.
- P5 aday config'i: `p5-publication/configs/candidate-v2.json`, salt-okunur.
- P3/P4 fiziksel zarfları: salt-okunur.
- Eski Tidy3D proje ve sonuçları: salt-okunur referans.
- Yeni teknik çalışmanın tek yazma alanı: `p6-physical-validation/`.

P5 kör sonuç dosyasının kilitli SHA-256 değeri
`b263292fd0226c10cc3b0096350176cb14771e258f2eacd89c2952ace9219028`'dir.

## Bilinen gerçekler, varsayımlar ve belirsizlikler

Bilinenler:

- `10 GBd`, `20 tap`, `30 kanal`, `10 PD`, `3 slot`, `15 GHz` minimum receiver bandwidth.
- P5 stress zarfı: `1 dB/cm` waveguide, `3 dB` switch, `1.5 dB` combiner,
  `5°` statik / `2°` dinamik faz, `%1` LO drift, `20 pA/√Hz`, `0.8 A/W`.
- P4'teki `100 mW`, wall-plug veya tek-lazer launch gücü değil; kol-başına
  normalize optik ölçeklerden kurulmuş konservatif eşzamanlı bütçedir.

Açık varsayımlar:

- Platform/kesit henüz seçilmedi. `n_g=4.0`, doğrulanacak tasarım girdisidir.
- Spiral pitch, minimum bend yarıçapı ve bend loss ilk floorplan zarfıdır;
  layout veya EM sonucu değildir.
- Splitter/tap ağacının ideal bölünme kaybı ile excess loss'u ayrı tutulur.
- İlk layout adayı toplam waveguide'i 14.24 cm'de tutan tek seri, progressive-tap
  double spiral'dır. Alternatif `1×20 + bağımsız delay` yaklaşık 1.424 m toplam
  waveguide ister ve baseline değildir.
- Termal faz trimleri slot hızında anahtarlanmaz. 30 kanal için statik preset,
  30 GHz routing için ayrı hızlı EO/switch katmanı gerekir.

Kritik belirsizlikler:

- Eski 800×400 nm SiN kesitte `n_g=2.1073186`; 14.24 cm ancak yaklaşık 10 sembol
  verir. `n_g≈4` sağlayan kesit/platform bulunmazsa uzunluk kilidi ile bellek kilidi
  aynı anda sağlanamaz.
- P3/P5 splitter/tap dağıtımını ve ideal fanout cezasını açıkça modellemedi.
- 30 GHz dinamik thermo-optic faz kontrolü fiziksel bir seçenek değildir.
- Propagation loss ve PD/heater değerleri FDTD'den tek başına çıkarılamaz;
  PDK, foundry veya ölçüm kanıtı gerekir.

## Bağımlılık grafiği

`G0 P5 provenance kilidi`
→ `G1 platform/kesit mode solve ve n_g`
→ `G2 14.24 cm double-spiral floorplan + tap/routing topolojisi`
→ `G3 straight de-embedding, bend ve splitter/combiner EM`
→ `G4 10 kol + 3 slot faz/routing/PD/termal compact model`
→ `G5 full-link loss, optical launch ve thermal composition`
→ `G6 fiziksel kabul raporu`.

G3'teki kompakt bileşen hücreleri G1'den sonra birbirinden bağımsız koşabilir.
Nihai parametre ve kabul kararı G5/G6'da merkezî olarak verilir.

## Kabul kapıları

1. **Provenance:** P5 blind JSON ve candidate-lock hash'leri birebir eşleşir.
2. **Delay:** mode-solver `n_g`, 14.240141755 cm'de `1.9 ns` gecikmeyi `%2` içinde verir.
3. **Layout:** gerçek route centerline uzunluğu hedefe `%0.1` içinde gelir; minimum
   radius, pitch/DRC ve tap konumları geçer; alan ve toplam bend açısı raporlanır.
4. **Propagation+bend:** bileşik gecikme-hattı kaybı P5 stress `1 dB/cm`
   zarfını aşmaz. Straight ve bend katkıları ayrı raporlanır.
5. **Splitter/tap:** progressive signal tap için hedef `κ` hatası; 50:50 LO splitter
   için imbalance; ikisinde de excess loss/reflection/crosstalk ölçülür. İdeal
   fanout cezası gizlenmez ve source-power normalizasyonu kapanır.
6. **Combiner:** 10 kolun kullandığı 2×2/MMI hücresi, ideal `3.0103 dB`
   tek-çıkış bölünmesinden ayrı hard `≤1.5 dB` excess insertion,
   hedef dengesizlik/faz hatası ve coherent transfer kapılarını geçer.
7. **Timing/faz:** 30 GHz slot routing'i hızlı aygıtla yapılır; thermal heater
   yalnız statik trim/stabilizasyon içindir. Residual `≤5°` statik, `≤2° RMS`
   dinamik ve LO drift `≤%1` olur.
8. **PD:** sistem Nyquist alt sınırı `15 GHz` olsa da P5 modelini birebir fiziksel
   eşlemek için her 10 PD/TIA kolunda `BW≥50 GHz`, `R≥0.8 A/W` ve input noise
   `≤20 pA/√Hz`; saturation, dark current, capacitance ve TIA swing ayrı raporlanır.
9. **Thermal:** heater sayısı, `Pπ`, ortalama/maksimum trim, kontrol elektroniği
   hariç/dahil sınırlar ve thermal crosstalk matrisi raporlanır.
10. **Composition:** yeni splitter/bend/routing cezaları P5 parametrelerinin içine
    sessizce gömülmez. Aşım varsa P5 skoru tekrar koşulmaz; iddia sınırı daraltılır.

## Başarı ölçütü ve bitirme kanıtı

P6, G1–G5 kapılarının her biri için kaynak dosyası, config hash'i, mesh/port
yakınsaması, sayısal metrik ve PASS/FAIL kaydı bulununca tamamlanır. Sadece Tidy3D
job'unun başarıyla bitmesi yeterli değildir.

## Durma koşulları

- `n_g` kapısı geçmeden spiral veya tam bileşen sweep'ine para harcanmaz.
- Kayıt altına alınmış kredi tahmini ve kullanıcı onayı olmadan cloud job gönderilmez.
- Full 14.24 cm 3D FDTD denenmez; kısa hücre S-parametreleri compact modele taşınır.
- Fiziksel zarf P5 varsayımlarını aşarsa blind tuning veya blind tekrar yapılmaz.
- Non-finite sonuç, yetersiz de-embedding veya mesh/port yakınsaması job'u reddeder.

## Başlangıç risk sırası

1. `n_g=4` sağlayan platform/kesit belirsizliği.
2. 30 GHz dinamik selector ile yavaş thermal trim'in ayrı fiziksel katmanlar olması.
3. Ortak kaynaktan 20 tap ve aynı-slot multicast için bölünme/launch-power hesabı.
4. 1.4 ns maksimum koherent diferansiyel gecikmede laser linewidth ve thermal drift.
5. 5 mW LO sınıfında 50 GHz PD/TIA saturation ve lineerlik.
6. P3'teki normalize edilmemiş alan toplamının pasif S-matris referans düzlemine eşlenmesi.

## Geçici fiziksel topoloji

- Tek input, 19 aralıkla yerleştirilmiş 20 tap, maksimum centerline `14.240141755 cm`.
- Tap aralığı `n_g=4` geçerse `7.49481145 mm`; gerçek route her `k` için
  `τ_k=k·100 ps` vermelidir.
- Lossless eş-güç tap başlangıcı `κ_k=1/(20-k)`'dir; excess loss ve gecikmeye
  bağlı attenuation geldikten sonra coupling oranları blind'e bakmadan power-balance
  denklemiyle yeniden çözülür.
- Aynı slotta aynı tap'i iki receiver kullanıyorsa ayrı multicast splitter gerekir.
  İdeal `3.0103 dB` division ile excess loss farklı kalemlerdir.

## Araştırma hattı bağlantıları

- [Photonic Reservoir proje merkezi](../docs/_source_records/project-hub-note.md)
- [P5 yayın sonucu](../p5-publication/RESULTS.md)
- [P4 fiziksel zarfı](../p4-optimization/RESULTS.md)
- [P3 sistem modeli](../p3-realistic/RESULTS.md)
- Eski Tidy3D referansı (MayOS vault note, outside this repository)
