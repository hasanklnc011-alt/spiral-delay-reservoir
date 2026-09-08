# P6 Custom-Process Inverse-Design Protokolü

Güncelleme: 2026-09-05

## Amaç ve sınır

G3-C splitter/tap ve G3-D 2×2 combiner için reddedilmiş jenerik geometri
tarama yolundan bağımsız, üretim-kısıtlı iki inverse-design hattı kurulur.
`343×180 nm` kesit sabittir. P5 blind hiçbir objective'e girmez.

Flexcompute'un resmi `invdes` akışı ortak bir design region'ı bir veya birden
fazla kaynak simülasyonu arasında paylaşabiliyor. G3-D bu nedenle iki bağımsız
girişli `InverseDesignMulti` problemi olarak kurulacaktır. Adjoint yönteminin
parametre sayısından bağımsız gradient maliyeti sağlaması, yüksek boyutlu topology
alanını uygulanabilir kılar; yine de her aşama öncesi gerçek cloud tahmini zorunludur.

Resmi yöntem kaynakları:

- [Tidy3D inverse-design plugin ve multi-port yaklaşımı](https://www.flexcompute.com/tidy3d/examples/notebooks/InverseDesign/)
- [Adjoint inverse-design çalışma ilkesi](https://www.flexcompute.com/tidy3d/examples/notebooks/Autograd0Overview/)
- [Resmi 90° optical hybrid ve 2×2 MMI metrikleri](https://www.flexcompute.com/tidy3d/examples/notebooks/90OpticalHybrid/)

## Ayrı problemler

### ID-G3C — 1×2 splitter

- Design region `6×4×0.18 µm`, tek giriş ve iki fiziksel çıkış.
- Üç design wavelength: `1530/1550/1575 nm`.
- Objective: iki çıkışın en düşük gücünü yükseltirken imbalance, reflection ve
  excess'i cezalandır; iki çıkış aynı fazda olmalı.
- Progressive tap oranları bu ilk hücreye zorlanmaz. Önce broadband, düşük-kayıplı
  50:50 primitive bulunur; farklı κ değerleri ayrı türetilmiş hücre/corner görevidir.

### ID-G3D — reciprocal 2×2 combiner

- Design region `8×5×0.18 µm`; üst ve alt giriş iki ayrı simülasyondur.
- Objective aynı topology'yi iki excitation ve üç wavelength arasında paylaşır.
- Kompleks mode amplitude üzerinden eşit genlik, `±90°` quadrature, düşük
  reflection ve pasiflik birlikte değerlendirilir. Yalnız power objective yeterli değildir.

## Üretim kısıtları

CP0 gelene kadar açıkça provisional: `40 nm` pixel, `200 nm` minimum feature/gap,
`400 nm` conic filter radius ve `200 nm` erosion/dilation length scale. Binary
export sonrası minimum feature/gap ve bağlantılılık yeniden ölçülür. CP0 bu
değerlerden daha sıkıysa tasarım tekrar filtrelenir; daha gevşekse otomatik
olarak küçültülmez.

## Aşama ve maliyet kapıları

1. `ID0`: yalnız yerel serialization/API/port/objective preflight; cloud yok.
2. `ID1`: coarse/effective-index seed; toplam tahmin `<1.5 FC`, kullanıcı solve
   onayı olmadan başlamaz. Bu aşama kabul üretemez.
3. `ID2`: binary seçilmiş geometri, iki-kaynak broadband 3D FDTD; toplam `<3 FC`.
4. `ID3`: m20/m25 ve `±10 nm width / ±5 nm thickness` corner; toplam `<10 FC`.

Yalnız ID2 metriklerini geçen ve ID3'te yakınsayan binary hücre G3-C/G3-D
hükmünü değiştirebilir. Optimizasyon history'sinden P5 blind'a dönmek yasaktır.

## Gerçekleşen ID0–ID2 sonucu

- ID0 yerel API/port/objective ve serialization kontrolleri geçti; cloud solve yoktu.
- ID1 tahmini toplam `1.5 FC` sınırındaydı. İki yerel yürütme hatasının olası
  maliyeti fail-closed rezerve edildi; splitter `3`, combiner `3` kaydedilmiş
  Adam adımıyla tamamlandı. Son post-process skorları sırasıyla `0.7411` ve
  `0.3888`; ID1 kabul üretmedi.
- Binary export cache→density→threshold zinciri ayrı SHA-256 değerleriyle
  kilitlendi. Minimum-feature proxy her iki seed'de de ihlal pikselleri buldu;
  CP0 kapanmadan üretilebilirlik iddiası yapılamaz.
- ID2 üç broadband FDTD solve'u için `0.16920 FC` tahmin verdi. Splitter worst
  excess/reflection `3.494 dB / -16.22 dB`; combiner worst excess/imbalance/
  quadrature/reflection `5.466 dB / 5.160 dB / 15.62° / -15.42 dB` oldu.
- İki binary seed de ID2 metriklerini geçmedi. ID3'e yükseltme yapılmadı;
  G3-C ve G3-D `FAIL/REDESIGN` kalır. Sonraki geçerli yol daha uzun ve ucuz
  effective-index continuation ya da foundry-qualified kompleks S-parametresidir.

## Araştırma hattı bağlantıları

- [Custom-process planı](CUSTOM-PROCESS-VALIDATION.md)
- [G3-C durumu](G3C-STATUS.md)
- [G3-D durumu](G3D-STATUS.md)
- [EM/FDTD planı](EM-FDTD-PLAN.md)
- [Proje merkezi](../docs/_source_records/project-hub-note.md)
