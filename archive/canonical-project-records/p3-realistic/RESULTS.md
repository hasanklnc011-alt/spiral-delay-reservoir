# P3 Gerçekçi Sistem Modeli Sonuçları

## Seçilen aday

- 30 sparse coherent intensity özelliği.
- 10 parallel photodiode, sembol başına 3 time-multiplex slot.
- 10 GBd sembol hızı; 30 GHz slot hızı.
- Gerekli receiver bandwidth: 15 GHz; modelde detector bandwidth: 50 GHz.
- En uzun optik gecikme: 14.240 cm (`n_g=4`, 19 sembol).
- Nominal validation medyan NMSE: `0.038246`.
- 9/10 seed `≤0.05`; en kötü seed 23: `0.097665`.
- Kör/test değerlendirmesi: `0`.

Nominal profil; `0.5 dB/cm` waveguide loss, `2 dB` switch loss, `1 dB` combiner
loss, `25 dB` extinction, `3°` statik ve `1°` dinamik faz hatası, `%0.5` LO
amplitude drift, `0.8 A/W` responsivity ve `15 pA/√Hz` thermal noise içerir.

## Mimari kararı

P2'nin tek-PD 30-slot yorumu 10 GBd gerçek zamanda 300 GHz slot hızı ve 150 GHz
receiver bandwidth istediği için reddedildi. Nominal doğruluk kapısını geçen en az
detector sayısı 10'dur. 20 özellikli minimum P2 adayı nominal profilde hiçbir port
bölüşümünde P3 doğruluk kapısını geçmedi.

## Tolerans sınırı

Stres profili (`1 dB/cm`, `3 dB` switch, `1.5 dB` combiner, `20 dB` extinction,
`5°/2°` phase error, `%1` LO drift, `20 pA/√Hz`) geçmedi. Tam paralel 30-PD durumda
dahi medyan `0.05356` kaldı. Bu sınır P4'te güç, receiver noise ve kanal bütçesi
optimizasyonuna yön verecek; stres sonucu gizlenmeyecek.

## Yeniden üretilebilirlik

- Başarısız V1: `runs/screen-v1.json`.
- Kanonik V2: `runs/screen-v2-receiver-bandwidth.json`.
- V2 sonuç SHA-256: `0f08e6291bde6ed26144a14e8ea7481f9e1e65939697d87a1db51eeb3095129f`.
- Config SHA-256: `078399ad702eeb97f82bc7c04e1675263158392ddd2fabfde7f410ae3b7c7593`.
- Source SHA-256: `61b6702715a5ef0b697d3245b336e6f559483b8074f78d36804b744a18a60067`.
- Kör/test değerlendirmesi: `0`.

## Kanıt seviyesi

Bu sonuç fiziksel parametreli sistem-seviyesi simülasyondur. Bileşen ölçümü, layout,
EM/FDTD doğrulaması veya tape-out kanıtı değildir. 14.24 cm gecikme hattının alanı,
bend loss'u ve faz stabilitesi P6 öncesinde ayrıca doğrulanmalıdır.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Photonic Reservoir proje merkezi]]
- [[🏰 300-Projects/Photonic-Reservoir/p2-architecture/RESULTS|P2 mimari sonuçları]]
- [[🏰 300-Projects/Photonic-Reservoir/MODEL-AND-ACCEPTANCE|Kabul protokolü]]
- [[🏰 300-Projects/Photonic-Reservoir/HANDOFF|Güncel handoff]]
