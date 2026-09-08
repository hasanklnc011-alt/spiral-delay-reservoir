# İkinci görüş talebi — issue-01 doğrulaması ve uygulanan değişiklikler

<ROLE>
Sen fotonik reservoir computing, coupled-mode teorisi ve sayısal deney
metodolojisi bilen kıdemli bir araştırmacısın. Aynı zamanda kod incelemesi
yapabiliyorsun.

Bu dosyayı sana veren kişi (Hasan) projenin sahibi. Aşağıda anlatılan işi
Claude adlı bir kodlama ajanı yaptı. Senden o ajanın işini **denetlemeni**
istiyoruz — onaylamanı değil.
</ROLE>

<TASK>
Aşağıda: (1) projenin ne olduğu, (2) dış bir modelin (GPT Pro) verdiği rapor,
(3) ajanın o raporu nasıl doğruladığı, (4) ajanın koda ve dokümana yaptığı
değişiklikler, (5) ajanın kendi belirttiği zayıf halkalar var.

Üç şey söyle:

1. **Yanlış olan ne?** Ajanın vardığı hangi sonuç kanıtı aşıyor, hangi
   çıkarımı hatalı, hangi kod değişikliği yanlış veya eksik?
2. **Kaçırılan ne?** Bu bulgular karşısında sorulmayan hangi soru daha önemli?
3. **Fiziksel geçerlilik kapısı doğru mu kuruldu?** Bu, ajanın en emin
   olmadığı kısım ve aşağıda ayrıca işaretlendi.

Bize katılman gerekmiyor. Ajanın haklı olduğu yerleri kısa geç; hatalı veya
fazla ileri gittiği yerlere odaklan.
</TASK>

---

## 1. Sistem

FDTD ile kalibre edilmiş SiN mikro-ring **üç-ring temporal coupled-mode (TCMT)
reservoir**. Python paketi, ~1200 satır, 21 test.

- Durumlar enerji-normalize kompleks halka alanları: `|a_i|²` joule, `|s_in|²` watt.
- Üç halka karşılıklı nearest-neighbor coupling ile bağlı.
- **Yalnız 1. halka sürülüyor**, **yalnız 1. halkanın through-port'u okunuyor.**
- Direct-detection (`|s_out|²`) → lineer ridge readout.
- Giriş maskeli virtual-node kodlamasıyla: sembol başına `n_virtual` düğüm.
- Opsiyonel delay feedback: kompleks çıkış alanının gecikmiş kopyası girişe eklenir.
- Hedef benchmark NARMA-10.

Model denklemi (`model.py`):

```
da/dt = (-1/τ - iΔ)·a  +  [ring 0'a] √(2/τ_ext)·s_drive  -  i·K·a  -  i·g_Kerr·|a|²·a
s_out = s_drive - √(2/τ_ext,0)·a[0]
s_drive = s_ext + η·e^(iφ)·s_out(t - τ_d)
```

**Değişmezler (proje kuralları, tartışmaya kapalı):**

- Model seçimi yalnız validation'da; test seti aday kilitlendikten sonra bir kez.
- Yayın kapısı: medyan NMSE < 0.30, delayed-input'a göre ≥ %10 iyileşme,
  seed'lerin ≥ %80'inde üstünlük, eşleştirilmiş %95 bootstrap üst sınırı < 0.
- Fiziksel Kerr koşuları `kerr_sensitivity_multiplier = 1`.
- İddia seviyeleri karışmaz: `TCMT` / `FDTD-calibrated TCMT` / `dynamic FDTD validation`.
- Si TPA/FCA/FCD ve termal fizik bu SiN modelinde yok, eklenmiyor.

## 2. Ölçülmüş sonuçlar (medyan test NMSE, düşük = iyi)

NARMA-10, 3 seed, seçilmiş konfigürasyon:

| Varyant | delay yok | delay var |
|---|---:|---:|
| üç-ring | 0.4281 | 0.3502 |
| uncoupled / tek-ring | 0.5684 | 0.3492 |
| delayed-input baseline | 0.3609 | 0.3609 |
| dijital ESN (20 durum) | 0.2759 | 0.2759 |
| coherent readout | — | 0.3584 |
| memory_reset | 0.7758 | 0.3615 |

NARMA-3 (kontrol görevi): üç-ring 0.0687, uncoupled 0.2324, delayed-input 0.2032, ESN 0.1040.

Delay adayının delayed-input'a üstünlüğü yalnız **%3**; eşleştirilmiş %95 bootstrap
CI `[-0.0475, 0.0207]` — sıfırı kapsıyor, **yayın kapısı geçilmedi**.

Fiziksel Kerr açık/kapalı farkı beş koşunun hepsinde dört ondalıkta **sıfır**
(~10⁻⁶ göreli).

Eski FDTD kanıtı: statik spektrum power NMSE 0.154, power korelasyon 0.980;
ama global kompleks gain sonrası **kompleks NMSE 1.180** — sıkı kapı başarısız.
Dinamik üç-ring FDTD benchmarkı yok.

## 3. GPT Pro'nun yargısı (özet)

Bu kurulum savunulabilir bir "fiziksel RNN üstünlüğü" iddiası üretemez. Üç neden:

1. **Erişilebilir state boyutu çöküyor** — 20 virtual node, 20 bağımsız dinamik
   state değil; üç kompleks mode'un tek porttan 20 ardışık örneği.
2. **Recurrence neredeyse lineer** — Kerr pratikte sıfır olduğu için tek
   nonlineerlik photodetection'ın karesi, ve o da geri besleme döngüsünün *dışında*.
3. **Arama fiziksel saati aşırı hızlandırmış** — `T_sym=0.2 ps / 20 node` =
   100 THz node-rate; ring FSR'i ~2.26 THz.

Ayrıca: "coupling ölü" teşhisi yanlış (delay yokken coupling ciddi katkı veriyor),
ve `memory_reset` ablation'ı tam reset değil.

## 4. Ajanın yaptığı doğrulama

Rapor donmuş bir snapshot'a bakan bir modelden geldiği için ajan her iddiayı
canlı kodda kontrol etti:

- Her `dosya:satır` çapası açıldı — hepsi tutuyordu.
- Her NMSE sayısı arşiv `metrics.json`'larıyla karşılaştırıldı — hepsi birebir.
- Raporun "hesapladım" dediği tanı sayıları bağımsız betikle yeniden üretildi:

| Durum | rapor MC | ajan MC | rapor rank | ajan rank |
|---|---:|---:|---:|---:|
| üç-ring, delay yok | 3.42 | 3.42 | 1.03 | 1.03 |
| üç-ring + delay | 3.80 | 3.80 | 1.35 | 1.35 |
| uncoupled + delay | 3.70 | 3.70 | — | 1.37 |
| ESN-20 | 7.64 | **7.39** | 2.07 | **2.11** |
| 10 açık lag | 10.02 | 10.02 | 9.92 | 9.92 |

MC = paketteki `linear_memory_capacity()` (Jaeger tarzı, kilitli split'lerde
gecikme başına `test_correlation²` toplamı, max_delay=20).

rank = participation ratio `(Σσ²)²/Σσ⁴`, train dilimindeki feature matrisinin
sütun-standardize edilmiş SVD'sinden.

**Sürpriz:** GPT Pro yüklenen paketin içinde gerçekten Python çalıştırmış.

## 5. Ajanın yaptığı değişiklikler

### 5.1 Delay hafızası ayrı kontrol oldu

**Sorun:** `_DelayHistory` sembol döngüsünün dışında bir kez kuruluyordu ve
`DriveConfig.reset_each_symbol` yalnız `state.fill(0)` yapıyordu. Yani
`memory_reset` ablation'ı delay hattını hiç sıfırlamıyordu.

**Değişiklik:**

```python
class _DelayHistory:
    def __init__(self, dt_s):
        self.values = []
        self.discarded = 0          # YENİ

    def clear(self):                # YENİ
        self.discarded += len(self.values)
        self.values = []

    def interpolate(self, time_s):
        if not self.values or time_s < 0.0: return 0j
        position = time_s / self.dt_s - self.discarded   # YENİ offset
        if position < 0.0: return 0j                     # YENİ
        ...
```

ve sembol döngüsünde `if feedback.reset_each_symbol: history.clear()`.

Delay açıkken iki yeni ablation eklendi: `three_ring_delay_reset` ve
`three_ring_full_memory_reset`.

İlk sonuç (smoke/NARMA-3, delay açık): normal 0.1000, cavity-reset 0.2629,
delay-reset 0.0687, ikisi-birden 0.6616.

### 5.2 Fiziksel geçerlilik kapısı (EN TARTIŞMALI KISIM — bkz. §6)

Ajan, salt-okunur FDTD kanıt dosyalarından kalibrasyon penceresini **okudu**:

- `explicit_three_ring_spectrum_best.csv`: 121 nokta, 20 GHz adım,
  **193.623–196.023 THz = 2.400 THz**
- `ringdown_tau_refined.json`: rezonans **194.823 THz = 1538.79 nm**,
  `Q_loaded = 569.3`, `τ_field = 0.930 ps`
- Ring FSR'i (config'den): `c/(n_g·2πR) = 2.264 THz` → kalibrasyon 1.06 FSR

Eklenen fonksiyon:

```python
def drive_bandwidth_hz(drive):
    return drive.n_virtual / drive.symbol_time_s     # "node rate"

def physical_validity(topology, drive, band_hz=2.400e12):
    ...
    "within_calibrated_band": node_rate <= band_hz
```

Bu her run manifest'ine yazılıyor. **Arama filtrelenmedi**, yalnız raporlanıyor.

Çıkan tablo — arama ızgarasının altı noktasının **altısı da** bandın dışında:

| n_virtual | T_sym (ps) | node rate (THz) | bandın katı |
|---:|---:|---:|---:|
| 10 | 0.2 | 50 | 20.8× |
| 10 | 0.5 | 20 | 8.3× |
| 10 | 1.0 | 10 | 4.2× |
| 20 | 0.2 | 100 | 41.7× |
| 20 | 0.5 | 40 | 16.7× |
| 20 | 1.0 | 20 | 8.3× |

Ajanın çıkarımı: bandın içinde kalmak `n_virtual=20` için `T_sym ≥ 8.33 ps`;
o rejimde `τ_f ≥ 1 sembol` istemek `Q ≳ 5100` gerektiriyor (mevcut 462–1081).
Sonuç: *"geçerli rejim ile yararlı rejim bu Q'larda örtüşmüyor."*

### 5.3 Kayıt bütünlüğü

Manifest'e `git_worktree_dirty` ve çalışan paketin `source_sha256`'sı eklendi
(iki arşiv koşusu aynı commit + aynı config altında farklı ablation setleri
kaydetmişti). Ayrıca `_json_safe`'te `bool`, `int`'ten önce kontrol edilecek
şekilde düzeltildi.

### 5.4 Doküman düzeltmeleri

- "Coupling kapalı" ablation'ının tek-ring'e **matematiksel olarak özdeş**
  olduğu yazıldı: coupling=0 iken ring 2-3 ne sürülüyor ne okunuyor, sıfır
  kalıyorlar. Beş koşuda dört ondalıkta aynı çıkmasının sebebi bu.
- "Eşit boyutlu ESN" ifadesi **"eşit readout-feature sayılı"** olarak düzeltildi.
- "Kazanç coupling'den değil feedback'ten geliyor" cümlesi delay-on rejimine bağlandı.

---

## 6. Ajanın kendi belirttiği zayıf halkalar

**Bunlara özellikle bak. Ajan bunlarda emin değil.**

### Z1 — Sürüş bandı ölçütü bir vekil (proxy)

Ajan sürüş bandını `n_virtual / T_sym` (node rate) aldı ve bunu kalibre edilen
2.400 THz pencereyle karşılaştırdı. Gerekçe: dalga biçimi her virtual node'da
değişiyor, dolayısıyla spektral içerik ~1/T_node'a uzanıyor.

**Ama:** maskelenmiş bir sinyalin güç spektrumu 1/T_node'da sert kesilmez.
Doğru soru muhtemelen "komşu longitudinal mode'lara ne kadar güç düşüyor" ve
bu, ±FSR ofsetlerindeki PSD'ye bağlı — ajan bunu hesaplamadı. Node rate,
birinci mertebe bir vekil.

Bu ölçüt yanlışsa, "ızgaranın tamamı geçersiz" tablosu da yanlış olur.

### Z2 — İki farklı kavram sayısal yakınlıkları yüzünden birleştirildi

"FDTD'nin ölçtüğü pencere" (2.400 THz) ile "tek-mode TCMT'nin geçerlilik
sınırı" (~FSR = 2.264 THz) aynı şey değil. Ajan bunların yakın çıkmasını
gate'in sağlamlığı lehine yorumladı. Bu bir tesadüf olabilir ve iki ayrı
gerekçenin birbirini desteklediği izlenimi yanıltıcı olabilir.

### Z3 — `Q ≳ 5100` sayısı bir tercihe dayanıyor

Ajan `τ_f ≥ 1 sembol` şartı koydu. Neden 1 sembol? NARMA-10 ~10 sembol
geçmiş istiyor. Öte yandan delay feedback, cavity lifetime olmadan da hafıza
sağlayabilir — belki `τ_f ≥ 1 sembol` hiç gerekli değil. Bu durumda 5100
ne taban ne hedef; anlamsız olabilir.

### Z4 — Participation ratio metodolojisi

Ajan SVD öncesi sütunları standardize etti. Rapor farklı bir ön işlem kullanmış
olmalı (ESN'de 2.07 vs 2.11, MC'de 7.64 vs 7.39). Hangisinin doğru olduğu
çözülmedi.

Daha önemlisi: **düşük participation ratio, kötü NARMA-10 performansının
nedeni mi yoksa yalnızca eşlik eden bir gösterge mi?** Ajan nedensellik ima
etti ama kanıtlamadı.

### Z5 — `clear()` fiziksel olarak ne demek?

Ajanın uygulaması, temizlemeden önceki zamanlar için `interpolate` → 0
döndürüyor; yani "hattaki ışık boşaltıldı" idealizasyonu. Gerçek bir cihazda
bunun karşılığı ne? Ayrıca `discarded` ofsetiyle indeks eşlemesinde birim
hatası olabilir — kontrol edilmeye değer.

### Z6 — Arşiv koşuları yeni kodla üretilmedi

Yeni ablation varyantları yalnız bundan sonraki koşularda var. Arşivdeki
NARMA-10 sayıları eski kodla üretildi. Ajan tam yayın protokolünü (10 seed)
yeniden koşmadı — pahalı ve model seçimini etkileyebilirdi. Yani buradaki
düzeltmeler henüz ana sonuçlara yansımadı.

### Z7 — `1.55 µm` vs `1538.79 nm`

Ring config'leri `wavelength_m = 1.55e-6` (193.414 THz) kullanıyor; kalibre
pencerenin alt kenarının 209 GHz altında, merkeze −0.62 FSR. Ajan bunu bir
tutarsızlık olarak işaretledi.

**Ama** `wavelength_m` nominal tasarım dalga boyu olarak kullanılıyor olabilir
ve kalibrasyon eşlemesi başka türlü yapılmış olabilir. Ajan bunu doğrulayamadı.

İlgili çözülmemiş nokta: ringdown tek halka için `Q_L = 569.3` veriyor, ama
model üç halkaya `462 / 828 / 1081` atıyor ve bu değerlerin nasıl türetildiği
pakette **hiçbir yerde yazmıyor**.

### Z8 — Araştırma koduna dış rapor üzerine müdahale edildi

Ajan, dış bir modelin raporu üzerine ablation matrisini büyüttü ve kabul
dokümanını değiştirdi. Bunların hepsi doğrulanmış bulgulara dayanıyor, ama
"ablation matrisi büyümeli miydi" ayrı bir metodolojik karar.

---

## 7. Cevabını nasıl ver

- Her bulguyu **DOĞRULANDI** (verdiğim veriden çıkarılabiliyor) veya
  **HİPOTEZ** (makul, doğrulanmamış) diye etiketle. Elinde kod yok, yalnız bu
  dosya var — bunu hesaba kat ve sahip olmadığın bilgiyi uydurma; "bu dosyadan
  anlaşılmıyor" yaz.
- Bir fizik iddiası için modelin denklemlerinden mi (ANALİTİK) yoksa ölçülen
  sayılardan mı (AMPİRİK) çıktığını ayır.
- Yukarıdaki değişmezler senin için de bağlayıcı. Onları gevşetmek gerektiren
  bir öneri varsa, öneri olarak değil "bu değişmez sorgulanmalı" başlığı altında
  yaz.
- Ajanın haklı olduğu yerleri tek cümleyle geç. Değerli olan, hatalı veya fazla
  ileri gittiği yerler.
- Sonunda en fazla 5 soru sor — yalnız cevabı yönünü değiştirecek olanları.
