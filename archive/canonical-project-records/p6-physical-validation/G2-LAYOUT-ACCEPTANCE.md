# G2 Delay-Spiral Layout Kabulü

## Karar

G2, 20 progressive tap taşıyan tek-seri Archimedean spiral için geçti. Provisional
double-spiral, merkezde `R=10 µm` altına düşen bir U dönüşü gerektirdiği için
seçilmedi; bu karar yalnız fiziksel geometriye dayanır ve P5 kör sonucunu kullanmaz.

- Hedef centerline: `142401.41755 µm`.
- GDS-quantized polyline: `142400.61041 µm`; bağıl hata `%0.000567`.
- Pitch `5 µm`, waveguide `0.343 µm`, edge gap `4.657 µm`.
- Minimum eğrilik yarıçapı `10.000 µm`.
- Dış centerline yarıçapı `476.169 µm`; keepout'lu bbox `982.34×982.34 µm`.
- `93.228` tur; en uzun komşu-sarım üst sınırı `2991.86 µm`.
- 20 tap aralığı `7494.81145 µm`; G1 `n_g` ile toplam gecikme `1906.159 ps`.
- GDS 1-nm database unit ve dokuz kesintisiz PATH parçası taşır; join gap `0`.

Üretilen GDS bir centerline/doğrulama maskesidir; foundry layer map, density fill,
metal/heater katmanları ve sign-off DRC içermez. Bu nedenle G2 kabulü fiziksel
topoloji içindir, tape-out kabulü değildir.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/P6-PROTOCOL|P6 protokolü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G1-ACCEPTANCE|G1 kesit kabulü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G3B-ACCEPTANCE|G3-B bend kabulü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/STATUS|P6 durum]]
- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Proje merkezi]]
