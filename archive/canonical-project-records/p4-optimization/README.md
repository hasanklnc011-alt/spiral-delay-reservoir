# P4 — Validation-only Robust Optimizasyon

## Amaç

P3'te nominal profili geçen mimariyi bağımsız donanım/noise realizasyonlarında
doğrulamak ve stres profilinde NMSE `<0.05` sağlayan en düşük port–güç maliyetli
adayı bulmak. Kör test P4 boyunca kapalıdır.

## Başarı kapısı

- Yalnız P0 development train/validation kullanılır; `test_evaluations=0`.
- En az 5 bağımsız hardware realization.
- Tüm data×hardware koşularının medyan validation NMSE'si `≤0.04`.
- On data seed'in en az 8'inin hardware-medyanı `≤0.05`.
- Bütün koşuların en az `%80`'i `≤0.05`.
- Delay, detector bandwidth, switch rate ve toplam optik güç kapıları birlikte geçer.

Discovery koşusu aday bulabilir fakat tek hardware realization kullandığı için P4'ü
kapatamaz. Seçilen aday ayrı confirmation config'iyle en az beş realizasyonda yeniden
çalıştırılır. Mevcut run dosyaları üzerine yazılmaz.

## Riskler

- P3 `signal_power_mw`, aktif detector kolu başına güçtür; P4 toplam eşzamanlı gücü
  `parallel_ports × (signal + LO)` olarak ayrıca sınırlar.
- Daha fazla güç NMSE'yi iyileştirirken enerji ve termal yükü büyütür.
- P4 sistem modeli layout, bend loss veya FDTD doğrulamasının yerini tutmaz.

## Sonuç

P4 kapısı geçti. Seçilen Pareto adayı 30 kanal, 10 photodiode × 3 slot ve detector
kolu başına 5 mW sinyal + 5 mW LO ölçeğidir; konservatif eşzamanlı toplam bütçe
100 mW'tır. Beş bağımsız hardware realization × 10 data seed üzerinde:

- Nominal medyan NMSE `0.027499`, koşuların `%90`'ı `≤0.05`.
- Stres medyan NMSE `0.033723`, koşuların `%90`'ı `≤0.05`.
- Her iki profilde 9/10 data seed hardware-medyanı `≤0.05`.

40 kanal aynı port ve güçte yalnız marjinal kazanç verdiğinden 30 kanal seçildi.
Ayrıntılar: [[🏰 300-Projects/Photonic-Reservoir/p4-optimization/RESULTS|P4 sonuçları]].

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Photonic Reservoir proje merkezi]]
- [[🏰 300-Projects/Photonic-Reservoir/p3-realistic/RESULTS|P3 gerçekçi sistem sonuçları]]
- [[🏰 300-Projects/Photonic-Reservoir/MODEL-AND-ACCEPTANCE|Kabul protokolü]]
- [[🏰 300-Projects/Photonic-Reservoir/HANDOFF|Güncel handoff]]
