# G3-D Coherent 2×2 Combiner Durumu

## Karar

G3-D henüz fiziksel kabul almadı; güncel durum `FAIL/REDESIGN`.
P5 kör sonucu yeniden çalıştırılmadı ve hiçbir geometri kararı kör skora göre
verilmedi.

## Mevcut kuplörün yeniden kullanım tanısı

G3-C için daha önce reddedilen yönlü-kuplör HDF5'i, coherent `0/90/180/270°`
compose ve pasiflik kod yolunu sınamak amacıyla yalnız yerel olarak işlendi.
İkinci excitation simetriyle türetildiği ve kaynak solve yakınsamadığı için bu
kayıt `DIAGNOSTIC_ONLY` sınıfındadır; G3-D kanıtı değildir.

## İki bağımsız kaynaklı 2×2 MMI pilotu

Flexcompute'un resmi 2×2 SOI MMI tohumu, kabul edilmiş `343×180 nm` kesite
ölçeklendi. Üst ve alt girişler iki ayrı, hash-kilitli 3D FDTD task'ıyla
uyarıldı. İlk task tamamlandıktan sonra runner yalnız string-log parsing'de
durdu; solve yeniden başlatılmadan başarılı task indirildi ve draft kalan ikinci
task aynı ID ile çalıştırıldı.

- Tahmin: `0.15275 FC`; gerçek toplam: `0.09583 FC`.
- İki solve decay: `5.90e-8 / 5.89e-8` — geçti.
- Merkez imbalance: `20.73 dB` — `0.5 dB` kapısını geçmedi.
- Worst-band excess: `1.584 dB` — hard `1.5 dB` kapısını geçmedi.
- Worst reflection: `-11.61 dB` — `-30 dB` kapısını geçmedi.
- Worst quadrature error: `74.41°`; tam-S en büyük tekil değer `1.166`.

Bu geometri reddedildi; m20/m25 convergence'a taşınmadı.

## EME uzunluk ekranı

Aynı `0.8575 µm` MMI genişliği için resmi simetrik/antisimetrik port-basis
dönüşümüyle `2–14 µm`, 49 noktalı EME uzunluk ekranı koşuldu (`0.15232 FC`).
En düşük birleşik hata skoru `11.0 µm`'deydi ve imbalance `0.365 dB` oldu;
ancak excess `4.615 dB`, reflection `-11.18 dB` ve quadrature error `79.34°`
nedeniyle ekran geçmedi. Bu uzunluk FDTD'ye gönderilmeyecek.

Port modları HDF5 üzerinde denetlendi: ilk çift `n_eff=1.868604/1.868580`
ile simetrik/antisimetrik TE modlarıdır; fiziksel-basis dönüşümü yanlış mod
sırasından kaynaklanmıyor. Yerel genişlik tanısı `1.2–1.4 µm` MMI'larda daha
uygun multimode alan gösterdi. Sonraki güvenli adım, yalnız bu iki fizik-temelli
genişlik için EME width+length ekranı; seçilmiş aday çıkarsa broadband iki-kaynak
FDTD pilotudur.

## Fizik-temelli genişlik + uzunluk ekranı

Yerel mode tanısının seçtiği yalnız `1.2/1.4 µm` MMI gövdeleri, `3–24 µm`
arasında `0.25 µm` adımlı 85 noktayla iki ayrı hash-kilitli EME görevinde
tarandı. Toplam tahmin ve gerçek maliyet `0.49937 FC`; iki görev de başarıyla
tamamlandı.

- `1.2 µm`: en iyi uzunluk `14.0 µm`; excess `4.881 dB`, imbalance `0.603 dB`,
  quadrature error `35.48°`, reflection `-12.09 dB`.
- `1.4 µm`: en iyi uzunluk `23.75 µm`; excess `4.570 dB`, imbalance `0.756 dB`,
  quadrature error `17.89°`, reflection `-10.31 dB`.

İki genişlik de ekranı geçmedi. Hiçbiri broadband iki-kaynak FDTD'ye
yükseltilmeyecek. Jenerik ölçekli MMI yolu durduruldu; G3-D için bundan sonraki
geçerli girdi foundry-qualified kompleks S-matris veya ayrı inverse-design/
transition-redesign hücresidir.

## Custom-process inverse-design sonucu

`8×5×0.18 µm` ortak topology, iki bağımsız excitation ve üç wavelength ile
ID1'de optimize edildi. Kaydedilmiş üç adım sonunda post-process skoru `0.3888`,
üretim cezası `0.6765` oldu; bu aşama kabul üretmedi. Binary ID2 FDTD worst
excess `5.466 dB`, imbalance `5.160 dB`, quadrature error `15.62°` ve reflection
`-15.42 dB` verdi. Çıkış alt-matrisinin en büyük tekil değeri `0.639` ile pasiflik
sınırını aşmadı, ancak diğer dört kapı kaçtı. Aday reddedildi ve ID3'e taşınmadı;
G3-D `FAIL/REDESIGN` kalır.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/P6-PROTOCOL|P6 protokolü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/EM-FDTD-PLAN|EM/FDTD planı]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G3C-STATUS|G3-C durumu]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G6-PHYSICAL-ACCEPTANCE|G6 kabul denetimi]]
- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Proje merkezi]]
