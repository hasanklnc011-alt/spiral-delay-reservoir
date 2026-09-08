# Güncel Model ve Kabul Protokolü

## İddia kapsamı

Yeni araştırma hattı, fiziksel olarak uygulanabilir on-chip optik çekirdek ve açıkça
etiketlenmiş readout ile NARMA-10 hedefler. Eski üç-ring SiN/Kerr TCMT modeli güncel
aday değildir; yalnız `legacy-three-ring/` altında tarihsel referanstır.

## P0 veri ve seçim kuralı

- Kanonik yayın sözleşmesi: `configs/p0_narma10_protocol_v2.json`. V1 kör test açılmadan emekliye ayrıldı.
- Model seçimi yalnız development train/validation üzerinde yapılır.
- Development geçiş hedefi: 10 seed medyan validation NMSE `≤0.04`.
- Kör test sonucu hiçbir hiperparametre veya mimari kararına geri beslenmez.

## Kör yayın kapıları

- Medyan test NMSE `<0.05`.
- En az `8/10` seed için NMSE `<0.05`.
- `delayed_input`, aynı-delay dijital ve fotonik çekirdeksiz kontrollerin her birine
  karşı en az `%10` göreli kazanç.
- Eşleştirilmiş `%95` bootstrap farkının üst sınırı `<0`.
- Bütün input, target, feature, prediction ve metrikler sonlu.

## Fiziksel kabul

- Field/power encoding açıkça tanımlanır; square-law çapraz terimlerinin kaynağı gösterilir.
- Port, tap, delay, ağırlık, kayıp, faz hatası, gürültü ve alan bütçesi raporlanır.
- İdeal kanal sayısı fiziksel port veya zaman-multiplex ölçümüne eşlenmeden fiziksel
  sistem sonucu diye sunulmaz.
- Fotonik katkı aynı delay/feature bütçeli dijital ve no-PIC kontrollerle ayrıştırılır.
- FDTD yalnız seçilmiş bileşen/model için, P5 başarı kapısından sonra kullanılır.

## P1 ideal üst sınır kanıtı

10 development seed üzerinde full-quadratic oracle `0.022164`, ideal coherent
field-u square-law basis `0.022534` medyan validation NMSE verdi. Sonuç 230 ideal
intensity kanalı içerdiğinden fiziksel PIC performansı değildir.

## P2 mimari kararı

Train-only sparse kanal sıralaması, 230 ideal kanalı tek photodiode üzerinde 20
zaman-multiplex ölçüme indirdi. Bu minimum aday `0.039716` medyan ve 8/10 seed başarıyla
P2 kapısını geçti. 30-slot aday `0.026459` medyan ve 9/10 seed başarı sağladığından,
P3'te kayıp/gürültü/tolerans için ana adaydır; 20-slot minimum ablation olarak korunur.

P2 hâlâ ideal/kayıpsız modeldir. P3; splitter ve combiner kaybı, finite extinction,
faz ve LO drift'i, shot/thermal noise, detector bant genişliği, ölçüm-slot zamanlaması
ve toplam optik güç bütçesini açıkça modellemeden fiziksel uygulanabilirlik iddiası yapmaz.

## P3 gerçekçi sistem sonucu

Nominal fizik profili altında 30 özellikli 10-PD × 3-slot hibrit mimari P3 kapısını
geçti: medyan validation NMSE `0.038246`, 9/10 seed `≤0.05`. Tek-PD 30-slot düzen
10 GBd gerçek-zaman timing/bandwidth kapısını geçmedi. 20 özellikli aday nominal
bozulmalar altında elendi. Stres profilinin başarısız olması nedeniyle P4; optik güç,
receiver noise, port/slot ve gerekirse kanal bütçesini validation-only optimize edecektir.

## P4 robust optimizasyon kararı

30 kanal, 10-PD × 3-slot ve kol başına 5 mW sinyal + 5 mW LO ölçeği seçildi.
Beş hardware realization × 10 development seed üzerinde nominal medyan `0.027499`,
stres medyan `0.033723`; her iki profilde koşuların 45/50'si ve data seed'lerin 9/10'u
`≤0.05` verdi. Aynı maliyette 40 kanalın kazancı yalnız `0.00030` olduğu için 30 kanal
Pareto adayıdır. Kör test hâlâ kapalıdır.

## P5 kör yayın sonucu

Kilitli aday tek kör v2 koşusunda `0.038705` medyan test NMSE ve 8/10 seed `<0.05`
ile yayın kapısını geçti. Delayed-input'a karşı göreli kazanç `%74.7`, no-PIC'e karşı
`%94.9`; iki bootstrap CI üst sınırı da sıfırın altındadır. Kayıpsız aynı-delay dijital
ikiz `0.032471` ile daha iyidir; fotonik uygulama cezası `%19.2` olarak raporlanır.
Kör sonuç artık optimizasyona geri beslenemez.

## Durma koşulları

- Non-finite veri/koşu: hemen reddedilir; clipping yapılmaz.
- P4 stres toleransı veya nominal tekrarlanabilirlik kapısını geçmezse mimari yeniden
  açılır; kör test çalıştırılmaz.
- Aday kilidi yok: kör test çalışmaz.
- İlk kör test başarısız: protokol v1 kapanır; aynı suite üzerinde tuning yapılmaz.

## Araştırma hattı bağlantıları

- [Photonic Reservoir proje merkezi](docs/_source_records/project-hub-note.md)
- [P0 benchmark ve kör test protokolü](P0-BENCHMARK-AND-BLIND-PROTOCOL.md)
- [P1 sonuçları](p1-coherent-delay/RESULTS.md)
- [P2 sonuçları](p2-architecture/RESULTS.md)
- [P3 sonuçları](p3-realistic/RESULTS.md)
- [P4 sonuçları](p4-optimization/RESULTS.md)
- [P5 sonuçları](p5-publication/RESULTS.md)
- [Güncel handoff](docs/_source_records/HANDOFF.md)
- Fotonik araştırma hatları sentezi (MayOS vault note, outside this repository)
