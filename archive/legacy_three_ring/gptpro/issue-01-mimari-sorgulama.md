<ROLE>
Sen fotonik reservoir computing ve coupled-mode teorisi üzerine çalışmış kıdemli
bir araştırmacısın: hem entegre fotonik cihaz fiziğini (mikro-ring rezonatörler,
Q/lifetime dengeleri, SiN ve Si platform farkları, Kerr nonlineerliğinin
gerçekçi büyüklükleri) hem de makine öğrenmesi değerlendirme metodolojisini
(reservoir kapasitesi, memory-nonlinearity dengesi, baseline seçimi, leakage)
biliyorsun.

Genel literatür folklorunu tekrarlama. Ekteki koddan ve ölçülen sayılardan
cevap ver; bir mekanizma önerdiğinde onu bu modelin denklemlerine bağla.
</ROLE>

<TASK>
Bu proje, NARMA-10'da fiziksel olarak savunulabilir bir üstünlük gösteremedi ve
biz bunun neden olduğunu yanlış teşhis etmiş olabiliriz. Senden istediğim bir
düzeltme listesi değil, bir YARGI.

Üç şeye cevap ver:

1. TEŞHİS — Ölçülen sonuçlar (aşağıda) mimarinin hangi özelliğinden çıkıyor?
   Üç-ring coupling'in neden ölü olduğunu, kazancın neden yalnız delay
   feedback'ten geldiğini ve eşit durum sayılı dijital ESN'in neden hepsini
   yendiğini kodun yaptığı işe bakarak açıkla. Bizim teşhisimiz "Q/lifetime
   NARMA-10 belleği için kısa" — bunu doğrula, çürüt veya yerine daha iyisini koy.

2. YARGI — Bu problem kurulumu (enerji-normalize üç-ring TCMT + tek delay loop +
   direct-detection + lineer ridge readout, NARMA-10 hedefi) savunulabilir bir
   fiziksel RNN iddiası üretebilir mi? Üretemezse, kurulumun hangi parçası
   kırık: topoloji mi, okuma şeması mı, görev seçimi mi, parametre rejimi mi,
   yoksa "fiziksel reservoir dijital ESN'i yenmeli" beklentisinin kendisi mi?

3. YÖN — Bu kod tabanının makul bir uzantısıyla ulaşılabilir, fiziksel olarak
   dürüst bir iddia hangisi? Bizim sormadığımız yönleri de getir.
</TASK>

<CONTEXT>

## Sistem

FDTD ile kalibre edilmiş SiN mikro-ring üç-ring temporal coupled-mode (TCMT)
reservoir. Durumlar enerji-normalize kompleks halka alanları: `|a_i|²` joule,
`|s_in|²` watt. Üç halka karşılıklı nearest-neighbor coupling ile bağlı.
Direct-detection through-port örnekleri lineer ridge readout'a veriliyor.
Delay kontrolü, kompleks çıkış alanının gecikmiş kopyasını girişe ekliyor.
Giriş, maskeli virtual-node kodlamasıyla sürülüyor. Hedef benchmark NARMA-10.

## Önce oku

`docs` paketinde: `MODEL-AND-ACCEPTANCE.md` (kabul protokolü, yayın kapıları,
zorunlu ablation'lar), `README.md` (iddia seviyeleri), `HANDOFF.md` (kapsam,
tamamlananlar, açık riskler).

## Dosya çapaları

- `model` paketi: `src/model.py` — TCMT çekirdeği, `rhs`, integrator, Kerr,
  coupling, delay-feedback, virtual-node maskesi. `src/config.py` — RingParams
  (Q_loaded, tau_field, tau_external, detuning, çevre uzunluğu), DriveConfig,
  FeedbackParams, SolverConfig, TopologyParams.
- `benchmark` paketi: `src/benchmark.py` — NARMA üretimi, leakage-safe split,
  standardizasyon, ridge fit, delayed_input_features, esn_features,
  mean_baseline, paired_bootstrap_ci. `src/search.py` ve `src/delay_search.py` —
  validation-only bounded aramalar.
- `pipeline` paketi: `src/experiment.py` — ablation matrisi ve yayın kapılarının
  uygulandığı yer. `configs/` — smoke, screening, selected, publication.
- `evidence` paketi: `runs/**/metrics.json` ve `manifest.json` (ham tahmin
  dizileri bilerek dışarıda), `runs/search_narma10.json`,
  `runs/search_delay_narma10.json`, `evidence/legacy_fdtd_validation.json`.

## Snapshot

Paketler 2026-09-02T13:27:34Z (UTC) export'landı, commit `789f9fa`. Bu tarihten
sonraki değişiklikleri göremezsin. Bir yerde kodun anlattığıyla dokümanın iddia
ettiği kaymışsa bunu ayrıca işaretle.

## Ampirik sinyaller

Bunlar DOĞRULANACAK İZ, sonuç değil. Hepsi medyan NMSE (düşük iyi):

NARMA-10:
- seçilmiş üç-ring-only: 0.4281
- delayed-input baseline: 0.3609
- eşit durum sayılı dijital ESN: 0.2759
- seçilmiş delay (1 sembol, η=0.8, φ=0) + üç-ring: 0.3502
- AYNI delay ile uncoupled / tek-ring: 0.3492

NARMA-3 (kontrol görevi):
- üç-ring 0.0687, delayed-input 0.2032, ESN 0.1040

İstatistik: delay adayının delayed-input'a medyan üstünlüğü yalnız %3;
eşleştirilmiş %95 bootstrap CI `[-0.0475, 0.0207]` — sıfırı kapsıyor, yayın
kapısı geçilmedi.

Fizik: fiziksel Kerr açık/kapalı farkı yaklaşık 10⁻⁶ göreli seviyede, ve avantaj
yönünde değil.

Eski FDTD kanıtı: üç-ring statik spektrum power NMSE 0.154, power korelasyon
0.980; fakat global kompleks gain düzeltmesinden sonra kompleks NMSE 1.180 —
sıkı fiziksel kapı BAŞARISIZ. Tek-ring transient: korelasyon 0.971, NMSE 0.202
(<0.2 kapısını az farkla geçemedi). Dinamik üç-ring FDTD benchmarkı YOKTUR.

Kod sağlığı: 17 test geçiyor — analitik steady-state, zaman-adımı yakınsaması,
determinism, delay davranışı, NARMA hizalaması, split güvenliği, cloud-gate.

## Bizim hipotezlerimiz

Her birini gerçek koda karşı DOĞRULA, ÇÜRÜT veya GENİŞLET. Bize katılmanı
istemiyorum; yanıldığımız yeri göstermeni istiyorum.

H1. Mevcut Q/lifetime, NARMA-10'un istediği bellek derinliği için çok kısa;
    halka alanları sembol süresi ölçeğinde yeterince uzun hafıza tutmuyor.

H2. Üç halka hesaplamaya anlamlı ek durum sağlamıyor — coupling ablation'ında
    sonuç korunuyor, yani halkalar birbirinin kopyası gibi davranıyor ve
    efektif durum boyutu ilan edilenden çok küçük.

H3. Direct-detection okuma, kompleks alandaki bilginin faz kısmını atarak
    reservoir'ın taşıdığı zenginliğin çoğunu okumadan önce yok ediyor.

H4. Fiziksel SiN Kerr kayması, mevcut güç ve Q aralığında sayısal olarak
    çözünür değil; nonlineerlik pratikte yalnızca fotodedeksiyonun karesinden
    geliyor ve bu NARMA-10 için yetersiz.

H5. NARMA-10 bu cihaz sınıfı için yanlış hedef olabilir; kontrol görevi
    NARMA-3'te üç-ring açık ara kazanıyor (0.0687 vs 0.2032) ve bu fark
    tesadüfi değil, kapasite sınırının işareti.

## Değişmezler

Bunlar tartışmaya kapalı. Fikirde serbestsin, kısıtta değil.

- Model seçimi YALNIZ validation üzerinde yapılır. Test seti ancak aday
  kilitlendikten sonra bir kez değerlendirilir. Hiperparametreyi test
  performansına göre ayarlamayı ima eden hiçbir öneri kabul edilmez.
- Yayın kapısı: medyan NMSE < 0.30, delayed-input'a göre en az %10 iyileşme,
  seed'lerin en az %80'inde üstünlük, eşleştirilmiş %95 bootstrap üst sınırı
  sıfırın altında. Kerr avantajı da aynı kurala tabidir.
- Fiziksel Kerr koşuları `kerr_sensitivity_multiplier = 1` kullanır. Bu çarpanı
  büyütmek bir duyarlılık taramasıdır, fiziksel sonuç değildir.
- İddia seviyeleri karıştırılmaz: `TCMT` (yalnız reduced-order dinamik),
  `FDTD-calibrated TCMT` (parametreleri FDTD'den), `dynamic FDTD validation`
  (kısa zaman-alanı FDTD iziyle doğrulanmış). Statik FDTD spektrumuna
  uydurulmuş TCMT, FDTD benchmark'ı olarak adlandırılamaz.
- Si'ye özgü TPA, FCA, FCD ve termal durumlar bu SiN modelinde YOKTUR ve
  eklenmesi önerilmez.
- FDFD fixed-point iterasyonu ve Tait weight-bank CTRNN bu paketin iddia
  kapsamı DIŞINDADIR.
- Zorunlu ablation matrisi korunur: Kerr açık/kapalı, üç-ring/tek-ring,
  coupling açık/kapalı, persistent state / sembolde reset, direct-detection /
  coherent-field, ve input-only + delayed-input + eşit boyutlu ESN baseline'ları.
- Yeni Tidy3D cloud koşusu `fdtd_cloud_gate_open = true` olmadan başlatılmaz.
  Senin raporun bu kapıyı açan bir gerekçe değildir.
- Eski `tidy3d_small_ring` kanıtları salt-okunurdur, SHA-256 ile bağlıdır.

</CONTEXT>

<exploration>
Yukarıdaki hipotezler bir ZEMİN, çit değil. Çerçevemizi sorgulamakta tamamen
serbestsin.

Özellikle şunları yapmanı istiyorum:

- Sormadığımız soruyu sor. Eğer bu sonuçların asıl anlamı bizim listemizde yoksa,
  onu söyle — bu, sorduklarımıza iyi cevap vermenden daha değerli.
- Bizim "başarısızlık" dediğimiz şeyin aslında doğru ve yayınlanabilir bir
  negatif sonuç olup olmadığını değerlendir. Öyleyse hangi çerçevede dürüstçe
  sunulabileceğini söyle.
- "Fiziksel reservoir eşit boyutlu dijital ESN'i yenmeli" beklentisinin kendisini
  sorgula. Bu alandaki dürüst iddia ne olmalı — ham doğruluk mu, enerji/gecikme
  başına doğruluk mu, başka bir şey mi?
- Literatürde bu modelin ölçtüğü büyüklükleri açıklayan bilinen bir mekanizma
  varsa (memory capacity teorisi, echo state property koşulları, consistency
  ölçütleri, kayıplı rezonatörlerde memory-nonlinearity dengesi) adıyla getir ve
  bizim sayılarımıza uygula.

Bir yöne işaret ettiğinde, o yönün bu kod tabanında hangi somut değişikliğe
karşılık geldiğini söyle. "CRDT kullanın" tarzı belirsiz referans istemiyorum:
sistemi VE ödünç alınabilir tekniği adlandır.
</exploration>

<self_reflection>
Cevaplamadan önce BU görev için dünya çapında bir cevabın iç rubriğini kur
(6–8 kategori). Örnek eksenler: ekteki koda gerçekten temellenmiş mi;
VERIFIED ile HYPOTHESIS'i ayırıyor mu; fiziksel mekanizmayı model denklemlerine
bağlıyor mu; istatistik iddiasını leakage ve kapı kurallarına göre kuruyor mu;
bizim hipotezlerimizden en az birini gerçekten çürütüyor mu; sormadığımız bir
yön getiriyor mu; değişmezlere saygılı mı; önerileri bu kod tabanında artımlı
uygulanabilir mi.

Hepsinden tam not alana dek iç döngüde yinele. Yalnızca nihai cevabı göster.
</self_reflection>

<long_context_handling>
Önce koddan ve dokümandan iç bir taslak çıkar. Önermeden önce taşıyıcı kısıtları
kendi cümlenle yeniden ifade et. Her iddiayı bir dosyaya veya bölüme çapala;
mekanizmayı soyut anlatmak yerine spesifik fonksiyonu, `dosya:satır`'ı veya
konfigürasyon anahtarını alıntıla.
</long_context_handling>

<uncertainty_handling>
Her bulguyu VERIFIED (ekli kaynakta doğrulandı) veya HYPOTHESIS (makul,
doğrulanmamış) diye etiketle. Satır numarası, metrik, parametre değeri veya API
uydurma; ekte yoksa "pakette yok" yaz.

Bir fizik iddiası için ayrıca ayır: modelin denklemlerinden mi çıkıyor
(ANALİTİK), yoksa koşu çıktısından mı (AMPİRİK)? İkisini birbirinin kanıtı gibi
sunma.

Bir performans cümlesi kurduğunda hangi iddia seviyesinde konuştuğunu söyle:
`TCMT`, `FDTD-calibrated TCMT`, yoksa `dynamic FDTD validation`.

Hipotezlerimiz yanlışsa açıkça söyle ve onları çürüten kodu veya sayıyı göster.
</uncertainty_handling>

<OUTPUT_FORMAT>
1. YÖNETİCİ ÖZETİ — en fazla bir paragraf. Yargın ne?

2. TEŞHİS — ölçülen davranışın mekanizması, koda çapalı. H1–H5'in her biri için
   açık bir hüküm: DOĞRULANDI / ÇÜRÜTÜLDÜ / KISMEN, ve gerekçesi.

3. YARGI — problem kurulumu savunulabilir bir iddia üretebilir mi? Üretemezse
   hangi parça kırık.

4. YÖNLER — açık sentez. Her yön için: fiziksel mekanizma, bu kod tabanındaki
   somut karşılığı, hangi ablation'la test edilir, ve dürüst iddia seviyesi ne
   olur. Sıralı ver (etki × efor), ama katı bir tabloya sıkıştırma —
   gerekçeyi düzyazı olarak yaz.

5. YAPMAYIN — bir değişmezi delecek veya iddia seviyesini kaydıracak olan,
   yüzeysel bakınca cazip görünen adımlar. Her biri için neden tuzak olduğunu
   yaz. Bu bölüm boş kalmamalı.

6. AÇIK SORULAR — operatöre en fazla 5 soru. Yalnızca cevabı senin yönünü
   değiştirecek olanları sor.
</OUTPUT_FORMAT>

<CONSTRAINTS>
Her şeyi ekteki kod tabanına ve dokümanlara temellendir; kodun yaptığı ile
dokümanın iddia ettiği arasındaki kaymayı işaretle.

DEĞİŞMEZLER bölümündeki maddelerin hiçbiri gevşetilemez. Bir öneri onlardan
birini delmeyi gerektiriyorsa, öneriyi verme — YAPMAYIN bölümüne yaz.

Sıfırdan yeniden yazım önerme; ancak kanıtlanabilir biçimde tek çözüm ise.

Endüstriyel veya literatür referansları sistemi VE ödünç alınabilir tekniği
adlandırmalı. Belirsiz "X kullanın" yok.

Ölçemediğin bir sayıyı verme. Bir iyileşme öngörüyorsan bunu HYPOTHESIS olarak
etiketle ve hangi koşunun onu sınayacağını söyle.

Dolgu yok. Nazik giriş paragrafı yok. Doğrudan yargıyla başla.
</CONSTRAINTS>
