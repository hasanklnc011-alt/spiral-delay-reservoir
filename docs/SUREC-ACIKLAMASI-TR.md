# Süreç açıklaması — P0'dan P6'ya, sıfırdan anlatım (TR)

> Bu belge, İngilizce `docs/` klasörünün **gayriresmî, öğretici bir Türkçe eşlikçisidir**.
> Amacı: konuya hiç girmemiş birine (ör. yeni bir öğrenciye, ya da altı ay sonra
> projeyi unutmuş sana) her aşamanın **neden** var olduğunu benzetmelerle anlatmak.
> Resmî sayılar ve kanıt zinciri için `docs/RESULTS_SUMMARY.md` ve her fazın
> `RESULTS.md` dosyasına bak.

---

## 0. Büyük resim: neden 7 aşama?

Bu proje tek bir "modeli eğittim, şu sonucu aldım" işi değil. Bir **kanıt merdiveni**:
her basamakta iddia biraz daha güçlenir, ve her basamağın kendine ait bir **kabul
kapısı** (geçtin / geçemedin kuralı) vardır.

| Aşama | Tek cümlelik amacı | Kanıt seviyesi |
|---|---|---|
| **P0** | Sınavın kurallarını, verisini ve hedefini önceden dondur | protokol / bütünlük |
| **P1** | "Bu fikir prensipte NARMA-10'u çözebilir mi?" | ideal matematik (üst sınır) |
| **P2** | 230 ideal ölçümü, gerçekçi sayıda ölçüme indir | ideal mimari simülasyonu |
| **P3** | Gerçek kayıp / gürültü / faz hatası / bant genişliği ekle | fiziksel-parametreli sistem simülasyonu |
| **P4** | Farklı donanım + veri kombinasyonlarında hâlâ çalışıyor mu? | Monte-Carlo sistem simülasyonu |
| **P5** | Tek seferlik **kör sınav** | kilitli kör sonuç (yayınlanabilir) |
| **P6** | "Bu optik çipi gerçekten üretebilir misin?" | elektromanyetik / bileşen kanıtı |

### İki rol: "üretici" ve "doğrulayıcı"

Proje boyunca iki şapka var:
- **Üretici (producer):** P1–P4'te modeli kurar, ayarlar, iyileştirir — ama **yalnızca
  geliştirme verisine** dokunabilir.
- **Doğrulayıcı (verifier):** Veri parmak izlerini (hash), aday-kilidi hash'lerini ve
  "kör test yetkisi" bayrağını kontrol eder.

Kör test sonucu **hiçbir ayara geri beslenmez.** Bu ayrım, kendini kandırmayı
(farkında olmadan test verisine ezber yapmayı) engellemek için var.

---

## P0 — Sınavın kurallarını önceden dondurmak

### Soru
"Başarı"yı ne zaman iddia edebilirsin? Bunu **modeli kurmadan önce** yazmazsan,
sonradan kolayına gelen tanımı seçme riskin olur.

### Benzetme
Bir yarışmaya girmeden önce jüri **puanlama kriterlerini, soruları ve geçme notunu**
kasaya kilitler. Yarışmacı "ben aslında şu kriterle değerlendirilmeliydim" diyemez.

### Ne yapıldı
- **NARMA-10 verisi deterministik üretiliyor:** aynı seed → bit bit aynı veri.
  (Seed = "rastgele" diziyi başlatan sayı; bkz. `docs/references/glossary.md`.)
- **20 veri setinin SHA-256 parmak izi kaydedildi.** Sonradan veri değiştirilirse
  parmak izi tutmaz.
- Seed'ler ikiye bölündü: **geliştirme** (istediğin kadar bak/ayarla) ve
  **kör** (179–229; kilitli, P5'e kadar dokunulmaz).
- Kod, bir **aday-kilidi** olmadan kör testi çalıştırmayı **reddediyor.**

### Geçme kuralı (baştan yazıldı)
Kör medyan test NMSE `< 0.05`, **ve** 10 seed'in en az 8'i `< 0.05`, **ve** her
kontrole karşı en az %10 göreli kazanç, **ve** eşleştirilmiş %95 bootstrap farkının
üst sınırı `< 0`.

### P0'da "doğru" sonuç
`blind_test_authorized: false` — yani "kör test henüz kapalı". Bu aşamada bunu
görmek **başarıdır**, hata değil.

---

## P1 — "Fikir prensipte çalışır mı?" (ideal üst sınır)

### Soru
NARMA-10'un ihtiyacı olan şey: **bellek** (çıktı son 10 girdiye bağlı) + **çarpım
terimleri** (ör. `u[t-9]·u[t]`). Bizim önerdiğimiz optik yöntem — gecikmeli ışık
alanlarını girişimletip kare-yasa dedektörle ölçmek — bu terimleri üretebilir mi?

### Benzetme
Bir yemeği pişirmeden önce, gerekli tüm malzemelerin mutfakta **var olduğunu**
kontrol edersin. Henüz pişirmedin ama "en azından mümkün" dedin.

### Ne yapıldı
Işık alanı `E_i = u[t-i]` (girdinin `i` sembol gecikmişi) olarak modellendi.
Şu yoğunluk (intensity) kanalları oluşturuldu:
- `|E_i|²` → `u[t-i]²` (öz terimler)
- `|LO + E_i|²` → lineer `u[t-i]` terimleri (LO = referans ışık)
- `|E_i + E_j|²` → `u[t-i]·u[t-j]` (çapraz terimler — kilit nokta)

230 kanal. Üstüne bir **lineer okuyucu** (ridge regresyon) koyuldu.

### Sonuç
- İdeal koherent kare-yasa modeli: **medyan validation NMSE 0.022534**
- "Kusursuz oracle" (tüm quadratic terimleri bilen dijital referans): 0.022164
  → aradaki fark **çok küçük** (`3.75×10⁻⁴`). Yani optik özellik ailesi, ihtiyaç
  duyulan matematiksel uzayı neredeyse tam **kaplıyor.**
- Düz lineer 20-gecikme kontrolü: 0.154694 → yani nonlineerlik olmadan **olmuyor**.

### Kritik uyarı
Bu **230 bağımsız ideal kanal** demek. Kayıp yok, gürültü yok, geometri yok.
Bu bir **fiziksel çip sonucu DEĞİL** — sadece "tavan" ölçümü.

> **Seed 23 notu:** Bu veri seti her quadratic varyantta zorlu (NMSE 0.074).
> Medyan kapısı geçti ama bütün seed'ler `<0.04` değil. Seed 23 bu noktadan
> sonra P4'e kadar **ısrarla** sorun çıkaracak — ve bunun donanımla ilgisi yok,
> hipotezimizin o veri setine özgü bir sınırı.

---

## P2 — 230 ideal ölçümü gerçekçi sayıya indirmek

### Soru
230 ayrı dedektör kimse kurmaz. En az kaç ölçümle hâlâ geçebiliriz?

### Benzetme
Bir ankette 230 soru sordun ve mükemmel sonuç aldın. Şimdi: "aynı bilgiyi 20–30
soruyla alabilir miyim?" Gereksiz soruları at, en ayırt edici olanları tut.

### Ne yapıldı
- Kanallar **yalnızca eğitim verisine bakılarak** önem sırasına dizildi.
- Fiziksel bütçe: 20 gecikme tap'i, yeniden ayarlanabilir bir birleştirici
  (iki sinyal tap'i **veya** bir tap + LO), **tek** fotodiyot, sembol başına
  `N` zaman-multiplex slotu.
- Rastgele `0/π` maskeler denendi → verimsiz (kapıyı geçmek için ~230 maske
  gerekti). Bu yüzden **göreve odaklı seyrek (sparse)** ölçüm ailesi seçildi.

### Sonuç
| Slot sayısı | Medyan NMSE | `≤0.05` seed |
|---|---|---|
| 20 (minimum) | 0.039716 | 8/10 |
| **30 (seçilen)** | **0.026459** | **9/10** |
| 40 / 60 | 0.025559 / 0.023906 | 9/10 |

20 slot geçen **minimum** bütçe ama marjı çok ince (`0.0003`). P3'e güvenli
pay olması için **30 slot** ana aday seçildi; 20 slot "minimum kontrol" olarak
korundu.

### Hâlâ eksik olan
Bu model **hâlâ ideal ve kayıpsız.** Ayırıcı/birleştirici kaybı, sonlu
sönüm oranı, faz hatası, LO kayması, atış/termal gürültü, dedektör bant
genişliği, slot zamanlaması — hiçbiri yok. Bunlar P3'ün işi.

---

## P3 — Gerçek fiziği eklemek

### Soru
Gerçek bir sistemde kayıp, gürültü, faz hatası ve sınırlı bant genişliği var.
Model bunlar altında hâlâ çalışıyor mu?

### Benzetme
Arabayı rüzgar tünelinde test ettin (P2). Şimdi çamurlu yolda, yağmurda,
lastikler aşınmışken sür (P3). Aynı performansı veriyor mu?

### Ne yapıldı
İki "profil" tanımlandı:

**Nominal profil** (makul, iyimser): 0.5 dB/cm dalga kılavuzu kaybı, 2 dB anahtar
kaybı, 1 dB birleştirici kaybı, 25 dB sönüm oranı, 3° statik + 1° dinamik faz
hatası, %0.5 LO genlik kayması, 0.8 A/W duyarlılık, 15 pA/√Hz gürültü.

**Stres profili** (kötümser): 1 dB/cm, 3 dB anahtar, 1.5 dB birleştirici, 20 dB
sönüm, 5°/2° faz, %1 LO kayması, 20 pA/√Hz.

### Sonuç
- **Nominal profil GEÇTİ:** 30 özellik, 10 fotodiyot × 3 slot, medyan **0.038246**,
  9/10 seed.
- **Tek fotodiyot / 30 slot fikri REDDEDİLDİ:** 10 GBd'de bu, 300 GHz slot hızı ve
  150 GHz alıcı bant genişliği isterdi — gerçekçi değil. 10 fotodiyot × 3 slot ise
  sadece ~15 GHz istiyor.
- **Stres profili GEÇEMEDİ:** tam paralel 30 fotodiyotla bile medyan 0.05356'da
  kaldı. Bu sınır gizlenmedi — P4'ün güç/gürültü/kanal optimizasyonuna yön verdi.

### Kanıt seviyesi
Bu bir **fiziksel-parametreli sistem simülasyonu.** Bileşen ölçümü, layout veya
FDTD değil. 14.24 cm gecikme hattının alanı ve viraj kaybı P6'da ayrıca
doğrulanmalı.

---

## P4 — Sağlamlık: "sadece bu ayarda mı çalışıyor?"

### Soru
P3 sonucu belki tek bir şanslı donanım kombinasyonuna denk geldi. Farklı
üretim varyasyonları ve farklı veri setleri arasında **tutarlı** mı?

### Benzetme
Bir ilacı 1 hastada denedin, işe yaradı. Şimdi 50 farklı hastada (farklı yaş,
kilo, metabolizma) dene. Çoğunda işe yarıyor mu, yoksa o tek hasta özel miydi?

### Ne yapıldı
- **5 donanım gerçeklemesi × 10 veri seed'i = 50 koşu**, her profil için.
- Yalnızca geliştirme (validation) verisi. Kör test hâlâ kapalı.
- Seçilen aday: 30 kanal, 10 fotodiyot × 3 slot, kol başına 5 mW sinyal + 5 mW LO,
  muhafazakâr 100 mW toplam optik bütçe.

### Sonuç
| Profil | Medyan NMSE | P90 NMSE | Başarılı koşu |
|---|---|---|---|
| Nominal | 0.027499 | 0.044108 | 45/50 |
| Stres | 0.033723 | 0.051650 | 45/50 |

**Her iki profil de geçti.** 40 kanal sadece `0.0003` kazandırdığı için **30 kanal
Pareto adayı** seçildi (fazladan 10 ölçüm + 4. slota değmez).

> **Seed 23 yine:** Başarısız 5 koşunun **hepsi seed 23.** Yani sorun donanım
> gerçeklemesi değil, mevcut 20-gecikme / quadratic hipotezinin o veri setine
> özgü sınırı. Bu, P1'den beri tutarlı — ve **gizlenmiyor**, dürüstçe raporlanıyor.

### 100 mW notu
Bu "muhafazakâr eşzamanlı optik bütçe" — lazer duvar-prizi gücü **değil**,
kol-başına normalize ölçeklerden kurulmuş üst sınır.

---

## P5 — Kör sınav (yayınlanabilir sonuç)

### Soru
P1–P4 boyunca aynı geliştirme verilerine defalarca baktın. Aldığın 0.03'ler
**gerçek yetenek** mi, yoksa o spesifik verilere farkında olmadan yapılmış
**ezber** (overfit) mi?

### Benzetme — restoran eleştirmeni
İyi bir eleştirmen restorana **isimsiz** gider. Şef geldiğini bilmez, özel
muamele yapamaz. Aldığı puan **gerçek** kaliteyi ölçer.

### "Kör test" ne demek?
Modelini **kesinleştirdikten sonra**, daha önce hiç görmediğin veriyle, **tek
kez** sınanman.

### Nasıl garanti ediliyor (hile yapılmadığı nasıl kanıtlanıyor)?
1. **P0'da** kör seed'lerin (179–229) veri hash'leri kilitlendi.
2. **P5 öncesi** aday (config + kaynak kod) donduruldu → `candidate-lock-v2`,
   parmak izi `664904b3...`.
3. `run_p5_blind.py` bu kilidi kontrol ediyor; tutmuyorsa **çalışmıyor.**
4. Kör çıktının kendisi de hash'lendi → `b263292f...`. Sonradan "tekrar mı
   çalıştırdı?" sorulursa hash'ler kanıt.

### Neden sadece 1 kez?
Kör testi 20 kez çalıştırıp en iyisini seçebilseydin, artık kör değildi —
sonuca bakıp ayar yapmış olurdun. Yeni fikir = **yeni protokol sürümü + yepyeni
kör seed'ler.** (Nitekim v1 böyle emekliye ayrıldı — bkz. aşağıda.)

### v1 neden emekliye ayrıldı?
v1'in kapısı şuydu: "gürültülü fiziksel model, kendi **kayıpsız dijital ikizini**
%10 yensin." Bu **mantıksal olarak imkânsız** — kayıplı bir şey kayıpsız
kusursuz halini yenemez. Geliştirme preflight'ında fark edildi, v1 **hiç kör
test çalıştırılmadan** kapatıldı. v2'de dijital ikiz bir **üst sınır** (raporlanan
tavan) yapıldı, üstünlük ise `delayed_input` ve `no_photonic_core` kontrollerine
karşı ölçüldü.

### 3 kontrol
| Kontrol | Nedir | Sonuç |
|---|---|---|
| **delayed-input** | Aynı gecikme belleği, ama optik nonlineerlik yok | 0.153 → aday **%74.7 daha iyi** (nonlineerlik katkısı gerçek) |
| **no-PIC** | Ne bellek ne optik çekirdek | 0.761 → aday **%94.9 daha iyi** (bellek gerçekten gerekli) |
| **digital twin** | Aynı 30 özelliğin kayıpsız/gürültüsüz dijital hali | 0.0325 → aday **%19.2 daha kötü** (fiziksel uygulamanın bedeli) |

Ayrıca **bootstrap %95 güven aralığı**: üstünlük istatistiksel olarak anlamlı mı?
İki kontrolün de üst sınırı `< 0` → **anlamlı**.

### Sonuç
| Ölçüt | Değer |
|---|---|
| Kör medyan test NMSE | **0.0387049671** |
| `< 0.05` seed sayısı | **8 / 10** |
| Kalan 2 seed (227: 0.0636, 229: 0.1203) | **Sonuçtan çıkarılmadı** |
| Yayın kapısı | **GEÇTİ** |

### P5'in cümlesi
> "P0'da kilitlenmiş, hiç dokunulmamış 10 kör veri setinde, dondurulmuş modeli
> tek sefer çalıştırdık. Medyan 0.0387, 8/10 geçti, kontrolleri anlamlı şekilde
> yendi, fiziksel ceza (%19.2) açıkça raporlandı." — Bu **fiziksel-parametreli
> sistem simülasyonu** sonucudur; deney veya üretilmiş çip değil.

---

## P6 — "Bu çipi gerçekten üretebilir misin?"

### Soru
P5 harika ama P3–P5'te kaybı, gürültüyü, faz hatasını **sayı olarak varsaydın**
("0.5 dB/cm", "3° faz"). Gerçek optik bileşenler bu sayıları tutturabilir mi?

### Benzetme
Bir binanın **statik hesabını** yaptın, sayılar tutuyor (P5). Şimdi mühendis
geliyor: "bu kolon gerçekten bu yükü taşır mı, bu malzeme piyasada var mı, bu
birleşim noktası nasıl yapılacak?" (P6)

### Ne yapıldı — 11 kapı
Her parça elektromanyetik simülasyonla (mode solver, FDTD) kontrol edildi:

| Kapı | Soru | Sonuç |
|---|---|---|
| **G0** | P5 hash'leri tutuyor mu? | ✅ PASS |
| **G1** | `n_g ≈ 4` veren kesit var mı? (19 sembol gecikme 14 cm'e sığsın) | ✅ PASS — 343×180 nm silisyum, `n_g = 4.01297` |
| **G2** | 14.24 cm dalga kılavuzu ~1 mm²'ye sarılır mı? | ✅ PASS — spiral, 142 400.6 µm, tasarım kurallarını geçiyor |
| **G3-A** | Düz referans kısımlar | ✅ PASS |
| **G3-B** | Virajlar + komşu sarım paraziti | ✅ PASS — R=10 µm viraj, kayıp `−0.0037 dB/90°`, parazit `< −124 dB` |
| **G3-C** | Gecikme hattından sinyal çeken tap'ler + LO ayırıcı | ❌ **FAIL / YENİDEN TASARIM** — denenen her geometride (yönlü kuplör, Y-ayırıcı, MMI serisi, slot-Y, union-Y) kayıp/yansıma/dengesizlik fazla |
| **G3-D** | Girişimi yapan 2×2 birleştirici | ❌ **FAIL / YENİDEN TASARIM** — MMI, EME taraması ve ters-tasarım denendi, hepsi dengesizlik/faz kapılarında kaldı |
| **G4** | 30 GHz hızlı anahtar S-parametreleri | ⏳ **OPEN** — aygıt verisi yok |
| **G4** | 50 GHz fotodiyot + amplifikatör zinciri | ⏳ **OPEN** — ölçülmüş veri yok |
| **G4** | Termal bütçe (`Pπ`, çapraz ısınma) | ⏳ **OPEN** — çözüm yapılmadı |
| **G5** | Hepsini birleştir → tam kayıp bütçesi | ⏳ **OPEN** — parçalar eksik |
| **G6** | Genel hüküm | **`NOT_PHYSICALLY_ACCEPTED`** (11'in 5'i PASS) |

### Ayakta kalan fiziksel kanıtlar
Gecikme kesiti, tam spiral rota, R=10 µm viraj, komşu sarım paraziti — bunlar
geçerli. Varsayım-temelli propagation (`0.8 dB/cm`) + virajlar → `0.8974 dB/cm`,
P5 stres zarfının içinde ama **foundry/cutback verisi olmadan fiziksel kabul değil.**

### KRİTİK: P6'nın başarısız olması P5'i çürütmez
- P5 **donmuş bir hesaplama sonucu.** P6 "donanım fizibilitesi henüz kanıtlanmadı"
  diyor, "P5 yanlış" demiyor.
- P6, P5'e **geri beslenmez.** Bir bileşenin yapımı zor diye modeli yeniden
  ayarlamıyorsun. Fiziksel ceza P5 varsayımlarını aşarsa **iddiayı daraltıyorsun**,
  P5 sayısını değiştirmiyorsun.
- Kör P5 skoru P6 boyunca **bir kez bile** yeniden çalıştırılmadı.

### Neden bu bir zayıflık değil
Fotonik hesaplama makalelerinde en sık hata: "simülasyonda çalıştı" deyip
"yani çip hazır" imasında bulunmak. Bu proje ikisini **bilinçli olarak ayırıyor**
ve "fiziksel kabul henüz yok, şu bileşenler yeniden tasarlanmalı" demeyi
başarısızlık değil **dürüst bir bilimsel sonuç** olarak sunuyor.

---

## Özet: her aşamanın tek cümlesi

- **P0** — Sınavın kurallarını, verisini ve geçme notunu önceden kasaya kilitle.
- **P1** — İdeal durumda bu optik fikir NARMA-10'un ihtiyacı olan terimleri üretebiliyor (medyan 0.0225).
- **P2** — 230 ideal ölçüm, 30 gerçekçi ölçüme indirildi (medyan 0.0265).
- **P3** — Gerçek kayıp/gürültü/bant genişliği eklendi; nominal profil geçti (0.0382), stres geçemedi.
- **P4** — 50 donanım×veri kombinasyonunda sağlam (45/50); 30 kanal Pareto adayı.
- **P5** — Tek seferlik kör sınav: medyan **0.0387**, 8/10, kontrolleri anlamlı yendi. Yayınlanabilir sonuç.
- **P6** — Çip fizibilitesi: 5/11 kapı geçti, ışık ayırıcı/birleştirici yeniden tasarım istiyor, bazı aygıtlar foundry bekliyor. Hüküm: `NOT_PHYSICALLY_ACCEPTED`.

**İki farklı iddia:** P5 = "algoritma/mimari fikri çalışıyor". P6 = "çip inşa
edilebilir". Birincisi kanıtlandı; ikincisi henüz değil — ve bunu açıkça söylemek
projenin en güçlü yanı.
