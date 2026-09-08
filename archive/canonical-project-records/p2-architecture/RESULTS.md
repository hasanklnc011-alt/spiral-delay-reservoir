# P2 Fiziksel Mimari Sonuçları

## Sonuç

P2 kapısı kör teste dokunmadan geçildi. Seçilen minimum mimari, 20 gecikme tap'inden
eğitim verisiyle seçilmiş self/LO/pair intensity ölçümlerini tek photodiode üzerinde
20 zaman slotunda sırayla okur.

| Zaman slotu | Medyan validation NMSE | En kötü seed | `≤0.05` seed | P2 kapısı |
|---:|---:|---:|---:|:---:|
| 20 | 0.039716 | 0.102674 | 8/10 | Geçti |
| 30 | 0.026459 | 0.085271 | 9/10 | Geçti |
| 40 | 0.025559 | 0.084534 | 9/10 | Geçti |
| 60 | 0.023906 | 0.082075 | 9/10 | Geçti |

18 ve 19 slot yalnız 7/10 seed'i `≤0.05` tuttu; 20 slot bu nedenle taranan ince
ızgaradaki gerçek minimumdur. 20-slot adayın geçiş marjı çok küçüktür. P3'te ana aday
30 slot olacak, 20 slot minimum/Pareto kontrolü olarak birlikte taşınacaktır.

## Fiziksel yorum

- Gecikme bütçesi: en fazla 19 sembol.
- Ölçüm: tek photodiode, sembol başına 20 veya 30 ardışık ayar/slot.
- Combiner: her slotta self, tap+LO veya iki-tap girişimi.
- Paralel eşdeğer: sırasıyla 20 veya 30 photodiode portu.
- İlk 20 seçimde baskın yapı, NARMA-10'un `u[t-9]u[t]` terimiyle uyumlu olan
  dokuz-sembol aralıklı tap çiftleridir.

Rastgele eşit-genlikli `0/π` MZI maskeleri verimsiz kaldı: 20–150 maske P2 kapısını
geçemedi, kapı ancak yaklaşık 230 maskede geçildi. Bu yüzden görev-odaklı sparse ölçüm
ailesi seçildi.

## Sınırlar

Bu P2 sonucu ideal ve kayıpsızdır. Splitter/combiner insertion loss, finite extinction,
faz hatası, LO drift'i, shot/thermal noise, detector bandwidth, slot değiştirme süresi
ve optik güç bütçesi henüz modellenmedi. Bunlar P3 kabul kapılarıdır. Seed 23 ve seed 41,
20-slot adayda sırasıyla `0.102674` ve `0.054658` ile eşik üstündedir.

## Yeniden üretilebilirlik

- Kanonik koşu: `runs/screen-v4-pareto.json`
- Config SHA-256: `83db356d85026abb880a4338c222d62d80e3fba129f6884d9466f16e9e2fb2f7`
- Sonuç SHA-256: `9207253bd00634da699c6d13c82a8025977cef20d6e4bb530d0d165d6e87405d`
- P0 protokol SHA-256: `2a66934d024178a15cacfccd282a3c27ca4d96a357b0820f3fcae59360ebc95a`
- Kör/test değerlendirmesi: `0`

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Photonic Reservoir proje merkezi]]
- [[🏰 300-Projects/Photonic-Reservoir/p1-coherent-delay/RESULTS|P1 ideal üst sınır]]
- [[🏰 300-Projects/Photonic-Reservoir/MODEL-AND-ACCEPTANCE|Güncel kabul protokolü]]
