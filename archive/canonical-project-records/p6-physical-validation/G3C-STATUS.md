# G3-C Tap ve LO Splitter Durumu

## Karar

`200 nm` gap uniform interaction bölümü remote/subpixel mode solver'da geçti:
m20→m25 50:50 uzunluk farkı `%0.314`, fine merkez uzunluğu `2.70022 µm`.
Bu sonuç progressive tap hedeflerini `0.775–5.400 µm` interaction uzunluklarına
eşler ve lossless uniform bölümün üniter compact S-matrisini sağlar.

Ancak S-bend transition içeren iki seçilmiş 3D FDTD hücresi **reddedildi**:

- v1: `4.38 dB` imbalance, `-10.59 dB` worst reflection.
- v2 geniş port: `7.85 dB` imbalance, 1550 nm reflection `-11.83 dB`, enerji
  artığı `%4.64`; final decay `1.35e-6` ile `1e-7` hedefini de sağlamadı.

Bu nedenle uniform coupling uzunluğunu tek başına LO splitter veya combiner
hücresi kabulü gibi kullanmak yasaktır. G3-C şu anda `FAIL/REDESIGN`; sıradaki
aday broadband MMI/Y-splitter veya foundry-qualified adiabatic coupler'dır.
P5 kör sonucu çalıştırılmadı ve bu red kararında kullanılmadı.

## Alternatif adaylar

- Simetrik adiabatik Y-splitter balance (`0.098 dB`) ve faz (`1.58°`) kapılarını
  geçti; fakat merkez yansıması `-15.00 dB`, worst yansıma `-9.27 dB` ve
  enerji artığı `%4.51` oldu. Aday reddedildi.
- `2.0 µm` genişlikli simetrik 1×2 MMI için `4/6/8/10/12 µm` uzunluklar
  remote 3D FDTD ile tarandı. Hiçbiri geçmedi. En iyi merkez iletimi `10 µm`
  adayında `0.991 dB` excess ve `-17.60 dB` reflection; worst-band reflection
  `-11.11 dB` ve maksimum enerji artığı `%24.54` oldu.
- MMI taraması `0.36051 FC` tahmine karşı kayıtlı `0.20004 FC` harcadı
  (bir işin fatura değeri sorgu anında gecikmeli/`0` görünüyordu).

Sonuç olarak jenerik SOI geometriyle daha fazla kör geometri taraması yapılmayacak.
G3-C, foundry-qualified adiabatic splitter/tap S-parametresi veya yeni, önceden
mode/EME ile optimize edilmiş bir hücre gelene kadar açık hard gate'tir.

No-cloud parity-mode ekranı bu ön-optimizasyonu uyguladı: `2.0 µm` MMI için
iki temel symmetry dalının 2π beat-length'i `18.4056 µm`, m20→m25 farkı
`%0.236`. Buna dayanarak `8.8/9.2/9.6 µm` dar FDTD penceresi koşuldu.
En iyi `9.6 µm` adayı excess'i `0.611 dB`'ye indirdi; ancak merkez/worst
reflection `-13.68/-12.39 dB` ve enerji artığı `%22.85` kaldı. Dar hedefli seri de
reddedildi. Sonraki tasarım yalnız uzunluk taraması değil, transition/topoloji
yeniden tasarımı veya foundry S-parametresi olmalıdır.

## Slot-opening transition redesign

İlk slot-opening task'ındaki `54.87 dB` asimetri ε-kesit denetiminde builder
hatasına bağlandı: üst slot sınırı rail'i siliyordu. Bu sonuç fiziksel aday
reddi sayılmadı; `evidence_valid=false` olarak korundu ve `0.25827 FC` maliyeti
gizlenmedi.

Düzeltilmiş v2 ayrı task/hash ile koşuldu. Final decay `8.01e-8`; imbalance
`0.173 dB` ve faz farkı `1.03°` geçti. Buna karşın excess `0.498 dB`, merkez/worst
reflection `-13.11/-12.27 dB`, enerji artığı `%6.68`; geçerli fiziksel kanıt
olarak reddedildi. Sonraki aday, slot-tip/interface için EME/adiabatic length
convergence veya foundry-qualified cell olmalıdır.

Slot-opening `40→80 µm` uzatılınca excess `0.498→0.294 dB`, enerji artığı
`%6.68→%2.45` iyileşti; ancak reflection `-12.84 dB`'de kaldı ve final decay
`8.7e-6` ile geçmedi. Ayrı taper-only hücrede dar giriş-port reflection'ı
`-9.58 dB` bulundu: kalıcı yansımanın ana kaynağı `w→2w` giriş transition'ıdır.
Taper-only multimode output toplamı birlikten büyük olduğu için bu tanıda
excess/energy kullanılmaz; yalnız reflection kanıtı geçerlidir. Sonraki topoloji
width-doubling taper'ını kaldırmalı veya foundry-qualified olmalıdır.

## Width-doubling içermeyen union-branch Y

İki sabit-genişlikli `w` kolun girişte union oluşturduğu, `80 µm` raised-cosine
ayrışmalı yarım-domain Y pilotu aynı kilitli draft üzerinde `0.30434 FC` ile
koşuldu. Nominal denge simetriyle korunmasına rağmen excess `0.403 dB`, merkez/
worst reflection `-12.89/-12.23 dB`, enerji artığı `%5.14` ve final decay
`4.08e-6` oldu. Dört nominal kapının tümü kaçırıldı ve aday reddedildi.

Bu sonuç, geri yansımanın yalnız `w→2w` taper kusuruna indirgenemeyeceğini;
union/bifurcation bölgesinin de hedef `-30 dB` için uygun olmadığını gösterir.
Jenerik FDTD geometri taraması burada durur. G3-C yalnız foundry-qualified
splitter/tap kompleks S-matrisi veya ayrı bir EME/inverse-design tasarım girdisi
ile yeniden açılabilir; mevcut fiziksel hüküm `FAIL/REDESIGN` kalır.

## Custom-process inverse-design sonucu

`6×4×0.18 µm` topology alanı, üç wavelength ve üretim filtresiyle ID1'de
optimize edildi. Kaydedilmiş üç adımda post-process skoru `0.0941→0.7411` oldu;
bu yalnız gri seed sonucudur. `0.5` threshold binary export'un broadband ID2
FDTD'si worst excess `3.494 dB`, imbalance `0.348 dB` ve reflection `-16.22 dB`
verdi. Excess ve reflection kapıları kaçtığı için aday reddedildi; ID3
convergence/corner çalıştırılmadı. G3-C `FAIL/REDESIGN` kalır.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/P6-PROTOCOL|P6 protokolü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G2-LAYOUT-ACCEPTANCE|G2 layout kabulü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G3B-ACCEPTANCE|G3-B bend kabulü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/STATUS|P6 durum]]
- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Proje merkezi]]
