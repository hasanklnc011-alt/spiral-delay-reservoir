# P2 — Fiziksel Kanal ve Multiplex Mimarisi

P2 tamamlandı. P1'deki 230 ideal intensity kanalı, yalnız P0 development
train/validation kullanılarak fiziksel olarak yorumlanabilir bir ölçüm bütçesine indirildi.

## Seçilen mimari

- 20 erişilebilir gecikme tap'i (`0…19` sembol).
- En fazla iki sinyal tap'ini veya bir tap ile LO'yu birleştiren yeniden ayarlanabilir combiner.
- Tek photodiode.
- Sembol başına 20 zaman-multiplex ölçüm slotu.
- İdeal/kayıpsız validation medyan NMSE: `0.039716`.
- 10 seed'in 8'i `≤0.05`; kör/test değerlendirmesi `0`.

20 slot P2 kapısını geçen minimum bütçedir; fakat marjı yalnız `0.000284` olduğu için
P3'te kayıp, gürültü ve tolerans taraması 30-slot adayla başlayacaktır. 30-slot adayın
medyanı `0.026459`, başarı oranı 9/10'dur. 20-slot mimari Pareto/minimum ablation olarak korunur.

Ayrıntılar: [[🏰 300-Projects/Photonic-Reservoir/p2-architecture/RESULTS|P2 sonuçları]].

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Photonic Reservoir proje merkezi]]
- [[🏰 300-Projects/Photonic-Reservoir/p1-coherent-delay/RESULTS|P1 ideal üst sınır]]
- [[🏰 300-Projects/Photonic-Reservoir/MODEL-AND-ACCEPTANCE|Güncel kabul protokolü]]
