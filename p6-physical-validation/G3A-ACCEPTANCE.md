# G3-A Straight Reference Kabulü

## Karar

G3-A, G1'de kabul edilen `343×180 nm` silicon strip / SiO₂ kesiti için lossless
scattering referansı olarak geçti. Dört ve sekiz mikrometre uzunlukların
`20/25 steps-per-wavelength` 3D FDTD karşılaştırmaları bütün yakınsama kapılarını
sağladı.

- 4 µm: insertion-loss farkı `0.000164 dB`, faz farkı `0.0319°`.
- 8 µm: insertion-loss farkı `0.000265 dB`, faz farkı `0.0481°`.
- Fine-mesh enerji artığı sırasıyla `%0.0349` ve `%0.0391`.
- Fine-mesh en kötü yansıma sırasıyla `-67.01 dB` ve `-67.18 dB`.
- Dört solve'un gerçek toplam maliyeti `0.1085072 FC`.

Bu kabul port normalization, kısa transition ve faz referansını doğrular. İdeal
FDTD'den fabricated propagation loss türetilmez. Uzun hattın `dB/cm` kaybı foundry
PDK, cutback ölçümü veya ayrıca belirtilmiş muhafazakâr sistem varsayımı olarak
tam devre modeline girer.

Kompleks `Li1993_293K` malzemeli ilk seri, 8 µm hücrede enerji-artığı kapısını
geçmedi; bunun nedeni bulk absorption'ın scattering artığına karışmasıydı. Bu seri
reddedilmiş tarihsel kanıt olarak korunur ve kabul edilen v2 sonucunu değiştirmez.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/P6-PROTOCOL|P6 protokolü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G1-ACCEPTANCE|G1 kesit kabulü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/EM-FDTD-PLAN|EM/FDTD planı]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/STATUS|P6 durum]]
- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Proje merkezi]]
