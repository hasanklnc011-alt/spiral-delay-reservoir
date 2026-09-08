# P4 Robust Optimizasyon Sonuçları

## Karar

P4 validation-only kapısı geçti. Seçilen aday:

- 30 sparse coherent intensity kanalı.
- 10 parallel photodiode × 3 time-multiplex slot.
- 10 GBd symbol rate, 30 GHz slot rate, 15 GHz gerekli receiver bandwidth.
- Kol başına 5 mW sinyal ölçeği + 5 mW LO.
- Konservatif toplam eşzamanlı optik bütçe: 100 mW.
- Maksimum delay: 14.240 cm.

`signal_power_mw_per_port`, normalize alan `u=1` için ölçek değeridir; gerçek NARMA
girdisi `u∈[0,0.5]` olduğundan signal kolunun anlık gücü bu üst ölçeğin altındadır.

## Çoklu-realization kanıtı

| Profil | Koşu | Medyan NMSE | P90 NMSE | `≤0.05` koşu | Başarılı data seed |
|---|---:|---:|---:|---:|---:|
| Nominal | 5 hardware × 10 data | 0.027499 | 0.044108 | 45/50 | 9/10 |
| Stres | 5 hardware × 10 data | 0.033723 | 0.051650 | 45/50 | 9/10 |

Her iki profil P4 kapısını geçti. Başarısız beş koşunun tamamı seed 23'tür. Bu seed
ideal P1 quadratic modellerinde de outlier olduğundan sorun donanım realization'ı
değil, mevcut 20-lag/quadratic hipotezin veri-setine özgü sınırıdır.

## Pareto gerekçesi

Discovery taramasında stres profilini geçen en düşük port sayısı 10, gerekli güç
ölçeği 5+5 mW/port oldu. Aynı 10 port ve güçte 40 kanalın stres medyanı `0.033419`,
30 kanalınki `0.033723` oldu. Yaklaşık `0.00030` kazanç için 10 ek ölçüm ve dördüncü
slot gerektiğinden 30 kanal seçildi.

## Sınırlar

- Bu seçim yalnız development validation sonuçlarına dayanır; kör test açılmadı.
- 100 mW konservatif sistem bütçesi yüksektir ve lazer wall-plug gücü değildir.
- Splitter ağacı, routing, bend loss, termal yük ve faz kontrol elektroniği layout
  seviyesinde henüz doğrulanmadı.
- P4 sistem-seviyesi Monte Carlo'dur; deney veya FDTD kanıtı değildir.

## Yeniden üretilebilirlik

- Discovery: `runs/discovery-v1.json`, SHA-256 `b7d9ae6f5af9c7f46ea477a96c5c639a72e662710fed6365c7463e7749e17f51`.
- Stres confirmation: `runs/confirmation-v1.json`, SHA-256 `44fa69e447ac10b1fd6564185eb30db7c9f8759b9b7758025d7c4a4a9a719a17`.
- Nominal confirmation: `runs/confirmation-nominal-v1.json`, SHA-256 `9de948e459f3f8f833a3da4a14d00fc0c09aea3e991823244468b0ba556e9416`.
- Hardware seeds: `101, 211, 307, 401, 503`.
- Kör/test değerlendirmesi: `0`.

## Araştırma hattı bağlantıları

- [Photonic Reservoir proje merkezi](../docs/_source_records/project-hub-note.md)
- [P3 sonuçları](../p3-realistic/RESULTS.md)
- [Kabul protokolü](../MODEL-AND-ACCEPTANCE.md)
- [Güncel handoff](../docs/_source_records/HANDOFF.md)
