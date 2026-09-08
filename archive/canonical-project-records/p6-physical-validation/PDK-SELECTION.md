# P6 Foundry/PDK Seçim Kapısı

Güncelleme: 2026-09-04

## Karar

`SELECTED_CUSTOM_PROCESS` — Hasan 2026-09-04'te ikinci yolu seçti. `343×180 nm`,
`180±5 nm` G1 kesiti korunacak; hazır 220 nm aktif PDK'ya göç edilmeyecek ve
G1–G3 bu nedenle yeniden açılmayacak. P6 sonuçları, fabricated custom-process
ve ölçüm kanıtı gelene kadar ön-tasarım zarfı olarak etiketlenecek.

P5 kör sonucu yeniden çalıştırılmadı ve PDK seçimi kör skora göre yapılmadı.

## Birincil kaynaklarla adaylar

| Aday | Kamuya açık güçlü kanıt | P6 uyumsuzluğu / eksik kanıt | Sonuç |
|---|---|---|---|
| imec iSiPP50G | Silicon-validated PDK; 50Gbaud aktif/pasif bloklar; yayımlanmış Ge PD responsivity `1 A/W`; yüksek hızlı modülatör ve heater seçenekleri | Sabit platform `220 nm` Si etch katmanları kullanıyor. G1'in `180±5 nm` koşuluyla uyumsuz; PD saturation/noise, switch kompleks S-parametresi ve thermal crosstalk kamu sayfasında yeterli değil | `REOPEN_G1_IF_SELECTED` |
| AIM Photonics Active/Low-Loss | Güncel PDK erişimi; waveguide, splitter/coupler, Ge PD, modülatör/switch ve thermo-optic kütüphane bulunduğu resmi olarak belirtiliyor | Nicel layer stack, kompleks S-parametre, PD saturation/noise ve heater matrisi lisanslı PDK erişimi gerektiriyor; kamu verisi mevcut kesiti doğrulamıyor | `REQUEST_PDK_DATA` |
| Tower PH18 | Low-loss waveguide, PD ve modülatör içeren açık foundry SiPho platformu | Resmi duyuruda `220 nm SOI`; G1 kesitiyle uyumsuz. G4 sayısal aygıt verileri kamu kaynağında eksik | `REOPEN_G1_IF_SELECTED` |

## Kaynaklar

- [imec iSiPP50G platform özeti ve 220 nm katman yapısı](https://www.imec-int.com/drupal/sites/default/files/2019-03/Photonic%20integrated%20circuit_EN_v4_MPW_yi_0.pdf)
- [imec 50G platform: 1 A/W Ge PD, >50 GHz modülatör ve PDK](https://www.imec-int.com/en/articles/imec-enhances-its-silicon-photonics-platform-to-support-50gb-s-non-return-to-zero-optical-lane-rates)
- [AIM Photonics mevcut PDK'lar ve erişim](https://www.aimphotonics.com/pdk)
- [AIM Low-Loss Active PDK v2.5 ve Ge PD modülü](https://www.aimphotonics.com/low-loss-pdk)
- [Tower PH18/PH18DB ve 220 nm SOI platformu](https://towersemi.com/2023/03/02/03022023/)

## İki meşru yol

1. **Üretilebilirlik öncelikli:** imec/AIM/Tower gibi gerçek bir aktif PDK seç;
   layer stack ve PCells'i içe al; G1 group-index/corner, G2 DRC, G3 bend/splitter/
   combiner ve G4 aygıt verilerini seçilen PDK üzerinde yeniden doğrula.
2. **Mevcut araştırma kesitini koru:** `343×180 nm` için custom foundry process,
   cutback, aktif aygıt ve heater/PD test yapısı gereksinimlerini kabul et; mevcut
   G1–G3 kanıtı yalnız custom-process ön tasarımı olarak kalsın.

Seçilen yol: **2**. 220 nm göç alternatifi yerel no-subpixel etki probunda da
kabul edilmedi: en yakın `310×220 nm` aday m15/m20/m25'te `n_g=3.918/3.957/4.339`
ve `%10.33` span verdi. Bu yalnız reddedilen göç alternatifinin tanısıdır.

Kamuya açık pazarlama metrikleri G4 kabulü için yeterli değildir. Seçilen PDK'nın
lisanslı model/S-parametre/measurement verileri gelmeden G4 ve G5 `OPEN` kalır.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/P6-PROTOCOL|P6 protokolü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G1-ACCEPTANCE|G1 kabulü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G4-STATUS|G4 durumu]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G6-PHYSICAL-ACCEPTANCE|G6 denetimi]]
- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Proje merkezi]]
