# G3-B Bend ve Komşu-Sarım Kabulü

## Karar

G3-B, `R=10 µm` dairesel 90° bend ve `5 µm` spiral pitch için P6 bileşen
doğrulamasını geçti. Başlangıçtaki `R=20 µm` bend geniş bant yansıma kapısını
kaçırdığı için reddedildi; P5 sonucu kullanılmadan yalnız fiziksel S-parametre
kapılarına göre `R=10 µm` seçildi.

- Fine m25, 1550 nm bend transmission: `-0.00372 dB/90°`.
- Fine m25 geniş-bant en kötü yansıma: `-39.26 dB`.
- Fine m25 maksimum enerji artığı: `%0.1446`.
- m20→m25 insertion farkı: `0.00256 dB`.
- Düz-hat fazı çıkarılmış m20→m25 bend-faz farkı: `0.4459°`.
- `5 µm` pitch, `4.657 µm` edge gap için 2.2 mm muhafazakâr tek-segment
  crosstalk üst sonucu: `-127.27 dB` (m20 worst).

Komşu-sarım hesabı even/odd TE paritelerini ayrı çözerek dejenere-mod karışmasını
önler. `2.2 mm` etkileşim uzunluğu gerçek centerline envanteri üretilene dek
muhafazakâr üst sınırdır; nihai GDS bunu aşarsa kuplaj hesabı yeniden açılır.

Bilinen P6 remote harcaması en az `0.97748 FC`'dir. m25 task başarıyla bitti,
ancak Tidy3D fatura değeri kayıt anında henüz yayınlanmadığından bu toplama dahil
değildir.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G1-ACCEPTANCE|G1 kesit kabulü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G3A-ACCEPTANCE|G3-A straight kabulü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/EM-FDTD-PLAN|EM/FDTD planı]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/STATUS|P6 durum]]
- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Proje merkezi]]
