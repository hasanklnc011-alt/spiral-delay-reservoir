# Model ve Kabul Protokolü

## Ana model

Durumlar enerji-normalize kompleks halka alanlarıdır. `|a_i|²` joule,
`|s_in|²` watt birimindedir. Üç halka karşılıklı nearest-neighbor coupling ile
bağlanır; direct-detection through-port örnekleri lineer ridge readout'a verilir.

Si'ye özgü TPA, FCA, FCD ve termal durumlar SiN modelinde bulunmaz. Delay kontrolü
kompleks çıkış alanının gecikmiş kopyasını girişe ekler. Tait weight-bank CTRNN ve
FDFD fixed-point çalışmaları bu paketin iddia kapsamı dışındadır.

## Zorunlu ablation'lar

- Fiziksel Kerr açık / kapalı.
- Üç-ring / tek-ring.
- Coupling açık / kapalı.
- Persistent state / her sembolde reset — cavity ve delay ayrı ayrı.
- Direct-detection / coherent-field.
- Input-only, delayed-input ve eşit boyutlu dijital ESN.

### Ablation sınırları

**Coupling kapalı, tek-ring'e özdeştir.** `model.py` yalnız `a[0]`'ı sürer ve
`through_field` yalnız `a[0]`'ı okur; coupling sıfırken ring 2 ve 3 ne uyarılır ne
gözlenir. Bu yüzden `three_ring_uncoupled` ve `single_ring` sayısal olarak aynı
çıkar. Bu ablation "coupling kapalı ⇒ etkin olarak tek halka" testidir; halkaların
birbirinin kopyası olduğunu **gösteremez**.

**Bellek reset'i iki ayrı kontroldür.** `DriveConfig.reset_each_symbol` yalnız
cavity state'ini sıfırlar; delay hattı `FeedbackParams.reset_each_symbol` ile ayrıca
sıfırlanır. Delay açık koşularda intrinsic bellek ile external echo belleğini
ayırmak için dört kombinasyon da raporlanır.

**"Eşit boyutlu ESN" eşit readout-feature demektir.** ESN 20 recurrent nonlinear
state taşır; fotonik tarafta 20 sayı, üç kompleks mode'un tek through-port'tan
alınan 20 ardışık örneğidir. Ölçülen participation rank `1.03` (delay yok) ve
`1.35` (delay var); 10 explicit lag için `9.92`. Bu baseline eşit dinamik-state
karşılaştırması olarak sunulmaz.

## Fiziksel geçerlilik kapısı

Model her halka için **tek** rezonans genliği taşır. Bu, sürüşün spektral içeriği
kalibre edilen pencerenin içinde kaldığı sürece savunulabilir. Pencere ölçülmüştür,
varsayılmamıştır — `results/explicit_three_ring_spectrum_best.csv`:

- **193.623 – 196.023 THz**, 121 nokta, 20 GHz adım → **2.400 THz** genişlik
- Ring FSR'i `2.264 THz`; yani kalibrasyon **1.06 FSR**
- Rezonans merkezi `194.823 THz = 1538.79 nm` (`ringdown_tau_refined.json`,
  Tidy3D ResonanceFinder, `Q_loaded = 569.3`, `τ_field = 0.930 ps`)

Sürüş bandı `n_virtual / symbol_time_s`'tir: dalga biçimi her virtual node'da
değişir. `physical_validity()` bu oranları hesaplar ve her run manifest'ine yazar.

**Bilinen iki uyumsuzluk:**

1. Ring config'leri `wavelength_m = 1.55e-6` (193.414 THz) kullanıyor; bu, kalibre
   edilen pencerenin alt kenarının 209 GHz altında, merkeze `-0.62 FSR` uzaklıkta.
   Yani model, FDTD'nin hiç ölçmediği bir dalga boyunda parametrelendirilmiş.
   Türetilen büyüklüklere etkisi küçük (`τ_f = 2Q/ω₀`, ~%0.7), ama
   `FDTD-calibrated TCMT` etiketi bu kayma yazılmadan kullanılmaz.

2. Mevcut arama ızgarasının (`search.py`) **altı noktasının altısı da** bandın
   dışında: en yavaş aday (`n_virtual=10`, `T_sym=1.0 ps`) bile 10 THz node-rate
   ile bandın `4.2` katı. Seçilmiş aday `41.7` katı.

Bandın içinde kalmak için `T_sym ≥ n_virtual / 2.400 THz` — `n_virtual=20` için
`≥ 8.33 ps`. O rejimde `τ_f ≥ 1 sembol` istemek `Q ≳ 5100` gerektiriyor; mevcut
halkalar `462–1081`. **Fiziksel olarak geçerli rejim ile hesaplama açısından
yararlı rejim, bu Q değerlerinde örtüşmüyor.** Bu, high-Q yönünün gerekçesidir.

## P0 sonrası NMSE < 0.05 yayın kapıları

Yeni mimari hattının kanonik benchmark sözleşmesi
[[🏰 300-Projects/Photonic-Reservoir/P0-BENCHMARK-AND-BLIND-PROTOCOL|P0 — NARMA-10 Benchmark ve Kör Test Protokolü]]
ve `configs/p0_narma10_protocol.json` dosyasındadır.

- Geliştirme seçimi yalnız train/validation üzerinde yapılır; medyan validation
  NMSE hedefi `≤0.04`.
- Aday config ve kaynak kod SHA-256 ile kilitlenmeden kör test açılmaz.
- Kör 10-seed başarı kapısı: medyan test NMSE `<0.05`, en az `8/10` seed `<0.05`,
  zorunlu kontrollerin her birine karşı en az `%10` kazanç ve eşleştirilmiş `%95`
  bootstrap farkının üst sınırı `<0`.
- İlk kör test başarısız olursa aynı suite tuning için kullanılamaz.

## Eski üç-ring hattının yayın kapıları

NARMA-10 için medyan NMSE `<0.30`, delayed-input'a göre en az `%10` iyileşme,
seed'lerin en az `%80`'inde üstünlük ve eşleştirilmiş farkın `%95` bootstrap üst
sınırının sıfırın altında olması gerekir. Kerr avantajı aynı istatistik kuralı ve
en az `%10` iyileşme olmadan iddia edilmez.

Yeni Tidy3D cloud koşuları bu kapı açılmadan başlatılmaz. Statik kompleks spektrum
için normalize hata `<0.2` ve güç korelasyonu `>0.95`; kısa transient için
korelasyon `>0.95` ve NMSE `<0.2` hedeflenir.
