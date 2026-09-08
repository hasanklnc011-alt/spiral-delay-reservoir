# issue-01 — Mimari sorgulama · rapor ve doğrulama kaydı

- **Gönderim:** GPT Pro, ChatGPT web arayüzü, Project (bölünmüş zip paketleri)
- **Snapshot:** `2026-09-02T13:27:34Z` · commit `789f9fa`
- **Rapor alındı:** 2026-09-02
- **Doğrulama:** 2026-09-02, canlı ağaç `789f9fa`, Claude Code

> Raporun ham metni oturum dökümündedir. Bu dosya, `gptpro-handoff` 6. adımının
> çıktısıdır: her iddianın canlı kodda kontrol edilmiş hâli ve triyajı.

---

## ÖNEMLİ: modelin ortamı hakkındaki varsayımımız yanlıştı

Skill "kabuk yok, dosya sistemi yok" diyordu. Bu koşuda **model kod çalıştırdı**:
paketteki `linear_memory_capacity()` fonksiyonunu ve SVD diagnostic'ini gerçekten
koşturmuş. Rapordaki sayılar bağımsız koşumla eşleşti.

Bu, doğrulama kapısını kaldırmıyor — kaldırmadı da: ESN sayısında sapma çıktı.
Ama "VERIFIED" etiketinin anlamını güçlendiriyor.

---

## Bağımsız üretilen diagnostic

Betik: model seçimi yapmaz, hiçbir parametreyi test performansına göre ayarlamaz;
yalnız train dilimi üzerinde tanı hesaplar. Seed 11, seçilmiş delay config.

| Durum | MC rapor | MC benim | part.rank rapor | part.rank benim |
|---|---:|---:|---:|---:|
| three-ring, delay yok | 3.42 | **3.42** | 1.03 | **1.03** |
| three-ring + delay | 3.80 | **3.80** | 1.35 | **1.35** |
| uncoupled + delay | 3.70 | **3.70** | — | 1.37 |
| ESN-20 | 7.64 | 7.39 | 2.07 | 2.11 |
| delayed-input-10 | 10.02 | **10.02** | 9.92 | **9.92** |

Birinci singular yönde varyans, three-ring/delay-yok: rapor %98.7, benim %98.7.

**Tek sapma:** ESN MC 7.64 → 7.39 ve rank 2.07 → 2.11. ESN'in kendi RNG'si ve
varsayılan `spectral_radius/leak/input_scale` parametrelerinden geliyor olabilir.
Sonucu değiştirmiyor (ESN her iki değerde de fotoniğin ~2 katı), ama raporun
ESN sayısı birebir yeniden üretilebilir değil.

---

## Bulgu bazında hüküm

### B1 — Memory-reset ablation'ı tam reset değil · CONFIRMED · uygula

`model.py:132` `history = _DelayHistory(dt)` sembol döngüsünün **dışında**, bir kez
kuruluyor. `model.py:136-137`:

```python
if drive.reset_each_symbol:
    state.fill(0.0)
```

yalnız cavity state'ini sıfırlıyor; `history` dokunulmadan kalıyor.

Sonuç: `three_ring_memory_reset = 0.3615` (normal 0.3502) satırı "hafıza
sıfırlansa bile performans korunuyor" demek **değil**. Doğrusu: *intrinsic ring
state sıfırlandı, external delay hafızası bırakıldı.* Bu, delay'in asıl hafıza
kaynağı olduğu teşhisini zayıflatmıyor — güçlendiriyor.

Delay kapalıyken (`feedback.enabled=False`) ablation doğru çalışıyor; sorun yalnız
delay açık koşularda.

### B2 — `three_ring_uncoupled` ≡ `single_ring`, matematiksel zorunluluk · CONFIRMED · dokümante et

`experiment.py:33-35` `_uncoupled()` coupling'i sıfırlıyor. Ama `model.py:47`
yalnız `a[0]`'ı sürüyor ve `model.py:88-89` `through_field` yalnız `a[0]`'ı
okuyor. Coupling sıfırken ring 2 ve 3: sürülmüyor, okunmuyor, sıfırdan başlıyor,
sıfır kalıyor.

Beş koşunun **hepsinde** dört ondalık basamağa kadar aynı:

| Koşu | uncoupled | single_ring |
|---|---:|---:|
| NARMA-3 | 0.2324 | 0.2324 |
| NARMA-10 (170452) | 0.7166 | 0.7166 |
| NARMA-10 (171015) | 0.5684 | 0.5684 |
| NARMA-10 delay (171535/171854) | 0.3492 | 0.3492 |

Bu ablation "halkalar birbirinin kopyası" iddiasını **destekleyemez** — çünkü
çıktı, fizikten değil koddan zorunlu. `MODEL-AND-ACCEPTANCE.md`'nin zorunlu
ablation listesindeki "coupling açık/kapalı" maddesi bu sınırla birlikte
okunmalı.

### B3 — Erişilebilir state boyutu çöküyor · CONFIRMED · en önemli bulgu

Participation rank 1.03 (delay yok) / 1.35 (delay var). Varyansın %98.7'si tek
yönde. Buna karşılık 10 explicit lag → 9.92, ESN-20 → ~2.1.

20 virtual node, 20 bağımsız dinamik state **değil**: üç kompleks cavity mode'un
tek through-port'tan alınan 20 ardışık örneği. Bağımsız olarak yeniden ürettim.

Bu, ESN karşılaştırmasının adını değiştiriyor: baseline **eşit readout-feature
sayılı** ESN'dir, eşit dinamik-state sayılı değil. `MODEL-AND-ACCEPTANCE.md` ve
`HANDOFF.md` "eşit boyutlu dijital ESN" derken bu ayrımı yapmıyor.

### B4 — Fiziksel geçerlilik kapısı yok · CONFIRMED (analitik) · Hasan'ın kararı

Seçilmiş config: `symbol_time_s = 2e-13`, `n_virtual = 20` → node başına 10 fs →
**100 THz node-rate**. Config'den (`radius_m=1e-5`, `group_index=2.1073`):

- round-trip: `n_g·2πR/c = 0.442 ps`
- FSR ≈ **2.26 THz**

Sembol hızı (5 THz) bile FSR'yi aşıyor. `model.py` her ring için tek rezonans
genliği taşıyor; tek-mode TCMT'nin geçerliliği sinyal bandı FSR'nin altındayken
savunulabilir.

`search.py:27` grid'i `(0.2, 0.5, 1.0) ps` ve **tüm en iyi adaylar 0.2 ps
sınırına yığılıyor** — arama, Q'yu artırmak yerine görev saatini hızlandırarak
τ/T_sym oranını büyütüyor.

Q değerleri doğrulandı: ring1 `Q_L=461.9` (τ_f 0.760 ps), ring2 `828.4`
(1.363 ps), ring3 `1080.5` (1.778 ps) — `config.py:33-38`'deki `τ_f = 2Q_L/ω₀`
ile birebir.

Eşiği kod tarafında uyduramayız: hangi bandın FDTD kalibrasyonuyla doğrulandığı
paket içinde yazmıyor. Bu, raporun 2. açık sorusu.

### B5 — Reproducibility zinciri açık · CONFIRMED · uygula

`experiment.py:103-107` yalnız `git rev-parse HEAD` kaydediyor; dirty working-tree
durumunu veya kaynak hash'ini kaydetmiyor.

`20260828T171535Z_eb8cd12479` ve `20260828T171854Z_eb8cd12479`: aynı config hash
(`eb8cd12479`), aynı commit (`d870a2c62b`), fakat ikincide
`three_ring_coherent_equal_features` var, birincide yok. Ana NMSE satırları aynı,
yani performans teşhisi bozulmuyor — ama "config + commit = tam tekrarlanabilirlik"
iddiası bozuluyor.

### B6 — H2 çürütüldü: coupling ölü değil · CONFIRMED · HANDOFF'u düzelt

Delay **yokken** coupling ciddi katkı veriyor:

- NARMA-10: three-ring `0.4281` vs uncoupled `0.5684`
- NARMA-3: three-ring `0.0687` vs uncoupled `0.2324`

`HANDOFF.md`'deki "kazanç üç-ring coupling'den değil feedback memory'den geliyor"
cümlesi yalnız **delay açık** rejimde doğru. Genel hâliyle yanlış ve bir sonraki
oturumu yanlış yönlendirir.

### B7 — H3 (faz atma) ana suçlu değil · KISMEN · sıraya al

`three_ring_coherent_equal_features = 0.3584` vs direct `0.3502` — faz korunduğunda
iyileşme yok. Ama `experiment.py:44` feature sayısını eşitlemek için
`n_virtual // 2` yapıyor, yani detection ile birlikte temporal çözünürlük de
yarıya iniyor. Temiz bir "yalnız detection değişti" deneyi değil. Rapor bunu
doğru teşhis etmiş ve H3'ü ana sıralamada aşağı koymuş.

### B8 — H4 (Kerr yok) doğrulandı

`three_ring_physical_kerr` ve `three_ring_kerr_off` beş koşunun hepsinde
**dört ondalıkta aynı** (0.0687/0.0687, 0.6677, 0.4281, 0.3502). `10⁻⁶` göreli
seviye iddiasıyla tutarlı. `encoded_power` (`model.py:28-30`) güç aralığı
`[5, 95] mW`; `minimum_power_w = 0.2 mW` clipping hiç devreye girmiyor →
threshold nonlineerliği de yok. Doğrulandı.

---

## Değişmez ihlali taraması

Raporun hiçbir önerisi `invariants.md`'yi delmiyor. YAPMAYIN bölümü kendi
kısıtlarımızla hizalı: T_sym'i daha da küçültme, 20 node = 20 state deme, Kerr
çarpanını büyütme, Si fiziğini taşıma, statik FDTD'yi dynamic'e yükseltme, cloud
başlatma, enerji üstünlüğüne pivot etme. **İhlal yok.**

---

## Triyaj

**Şimdi uygula (kod, düşük risk):**
- B1 — delay history reset'i ayrı kontrol olarak ekle
- B5 — run manifest'ine dirty-tree / kaynak hash alanı ekle
- B6 — `HANDOFF.md`'deki coupling cümlesini rejime bağla
- B2/B3 — `MODEL-AND-ACCEPTANCE.md`'ye ablation sınırı ve "eşit readout-feature"
  adlandırması notu

**Karar gerek (Hasan):**
- B4 — fiziksel geçerlilik kapısı: FDTD kalibrasyonunun geçerli bant aralığı ne?
- Ring 2/3'ten fiziksel drop/tap output alınabilir mi? (state observability yönü)
- Ren et al. için gerçekçi `Q_int/Q_ext` kartı var mı?

**Şimdilik bekle:**
- B7 — temiz detection ablation'ı (feature bütçesi sabit, temporal çözünürlük
  sabit) B4 çözülmeden anlamlı değil; geçersiz parametre rejiminde ölçüm olur.

---

## Uygulama kaydı

| Bulgu | Durum | Tarih |
|---|---|---|
| B1 | **uygulandı** — `FeedbackParams.reset_each_symbol`, `_DelayHistory.clear()`, iki yeni ablation varyantı, iki yeni test | 2026-09-02 |
| B2 | **uygulandı** — `MODEL-AND-ACCEPTANCE.md` "Ablation sınırları", `HANDOFF.md` notu | 2026-09-02 |
| B3 | **uygulandı** — `MODEL-AND-ACCEPTANCE.md` "eşit readout-feature" adlandırması | 2026-09-02 |
| B4 | **uygulandı** — kalibre bant kanıttan ölçüldü, `physical_validity()` eklendi, manifest'e yazılıyor | 2026-09-02 |
| B5 | **uygulandı** — manifest'e `git_worktree_dirty` + `source_sha256` | 2026-09-02 |
| B6 | **uygulandı** — `HANDOFF.md` coupling cümlesi rejime bağlandı | 2026-09-02 |
| B7 | hâlâ ertelendi — temiz detection ablation'ı ancak geçerli rejimde anlamlı, oraya Q artmadan gidilemiyor | — |
| B8 | eylem gerekmiyor | 2026-09-02 |

### B1 uygulaması — ilk sonuç

Smoke config (NARMA-3, tek seed), delay açık. Üç alt sistem artık ayrışıyor:

| Varyant | NMSE |
|---|---:|
| normal (cavity + delay) | 0.1000 |
| cavity reset, delay kalıyor (`three_ring_memory_reset`) | 0.2629 |
| delay reset, cavity kalıyor (`three_ring_delay_reset`) | 0.0687 |
| ikisi birden (`three_ring_full_memory_reset`) | 0.6616 |

Bu smoke/NARMA-3'tür, NARMA-10 sonucu değil. Ama kontrol çalışıyor: eski tek
`memory_reset` satırı bu üç durumu tek sayıya sıkıştırıyordu.

`three_ring_delay_reset = 0.0687`, delay'siz NARMA-3 koşusunun (`170316`) üç-ring
değeriyle birebir aynı — bir-sembol gecikmede her sembolde history temizlemek
feedback'i kapatmaya denk, testte de bu iddia edildi.

### Ek olarak bulunan kusur

`_json_safe` içinde `int` şubesi `bool` şubesinden önce geliyordu; `bool` Python'da
`int` alt sınıfı olduğu için yeni `git_worktree_dirty` alanı manifest'e `1` diye
yazıldı. Sıra düzeltildi. Mevcut manifest'lerde boolean alan bulunmadığı için eski
kayıtlar etkilenmemiş.

`_source_sha256` ilk hâlinde `project_root/src/photonic_reservoir` arıyordu, ama
`cli.py:40` git kökünü (`project_dir.parents[1]` = MayOS) geçiriyor; alan `None`
kalıyordu. Artık `__file__` üzerinden **çalışan paketi** hash'liyor — semantik
olarak da doğrusu bu.


---

## B4 çözümü — kalibre edilmiş bant

Hasan "1.55 µm'de geçerli" dedi; bu merkez dalga boyu, band genişliği değil.
Genişlik salt-okunur kanıt kaynağından **okundu**, sorulmadı:

`results/explicit_three_ring_spectrum_best.csv` — 121 nokta, 20 GHz adım,
**193.623–196.023 THz = 2.400 THz**. Ring FSR'i 2.264 THz → kalibrasyon 1.06 FSR.

`results/ringdown_tau_refined.json` — Tidy3D ResonanceFinder, rezonans
**194.823 THz = 1538.79 nm**, `Q_loaded = 569.3`, `τ_field = 0.930 ps`.

### İki uyumsuzluk

**Merkez kayması.** Ring config'leri `1.55e-6 m` = 193.414 THz kullanıyor. Bu,
kalibre pencerenin alt kenarının 209 GHz altında; merkeze `-0.62 FSR`. Model,
FDTD'nin ölçmediği bir dalga boyunda parametrelendirilmiş. Türetilen büyüklüklere
etkisi ~%0.7 (`τ_f = 2Q/ω₀`), ama iddia seviyesi açısından önemli.

Ayrıca ringdown tek halka için `Q_L = 569.3` veriyor; model üç halkaya
`462 / 828 / 1081` atıyor. Bunların nasıl türetildiği pakette yazmıyor.

**Arama ızgarasının tamamı bandın dışında.**

| n_virtual | T_sym (ps) | node (THz) | node/bant | geçerli |
|---:|---:|---:|---:|---|
| 10 | 0.2 | 50 | 20.8× | hayır |
| 10 | 0.5 | 20 | 8.3× | hayır |
| 10 | 1.0 | 10 | 4.2× | hayır |
| 20 | 0.2 | 100 | 41.7× | hayır |
| 20 | 0.5 | 40 | 16.7× | hayır |
| 20 | 1.0 | 20 | 8.3× | hayır |

Seçilmiş aday (`20 / 0.2 ps`) bandın **41.7 katı**.

### Sonuç

`T_sym ≥ n_virtual / 2.400 THz` → `n_virtual=20` için `≥ 8.33 ps`. O rejimde
`τ_f ≥ 1 sembol` istemek `Q ≳ 5100` gerektiriyor; mevcut halkalar `462–1081`,
yani **5–11× yetersiz**.

Fiziksel olarak geçerli rejim ile hesaplama açısından yararlı rejim bu Q
değerlerinde örtüşmüyor. Rapor "arama modelin geçerlilik bölgesinden çıkmış"
derken haklıydı, ama tablo daha sert: çıkılacak geçerli bir bölge zaten yoktu.

Bu, high-Q yönünün gerekçesini bir tercihten zorunluluğa çeviriyor — ve state
observability yönü onunla birlikte gitmeli, çünkü yüksek-Q bir array de aynı tek
through-port'tan gözlenirse participation rank yine çökük kalır.

Uygulama: `RingParams.fsr_hz`, `drive_bandwidth_hz()`, `physical_validity()`,
`CALIBRATED_BAND_HZ` / `CALIBRATED_CENTER_HZ` sabitleri; her run manifest'inde
`physical_validity` bloğu; 2 yeni test. Arama **filtrelenmedi** — mevcut ızgarayı
susturmak yerine geçersizliği görünür kılmak doğru olan; ızgarayı yeniden kurmak
Hasan'ın kararı.
