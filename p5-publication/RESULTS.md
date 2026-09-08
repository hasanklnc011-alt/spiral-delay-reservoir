# P5 Tek Kör Test Sonuçları

## Nihai sonuç

P5 yayın kapısı geçti.

- Kör medyan test NMSE: `0.0387049671` (`<0.05`).
- `<0.05` seed sayısı: `8/10`.
- Delayed-input medyanı: `0.1530487464`; göreli kazanım `%74.71`.
- No-PIC medyanı: `0.7606056879`; göreli kazanım `%94.91`.
- Her iki eşleştirilmiş bootstrap farkının `%95` üst sınırı `<0`.
- Kayıpsız aynı-delay dijital ikiz: `0.0324712617`; fiziksel adayın cezası `%19.20`.

Seed 227 `0.06360`, seed 229 `0.12033` ile eşik üstündedir. Bunlar sonuçtan çıkarılmadı.

## Kör seed sonuçları

| Seed | Test NMSE | Durum |
|---:|---:|:---:|
| 179 | 0.03560 | Geçti |
| 181 | 0.04108 | Geçti |
| 191 | 0.03266 | Geçti |
| 193 | 0.03072 | Geçti |
| 197 | 0.03942 | Geçti |
| 199 | 0.04247 | Geçti |
| 211 | 0.03753 | Geçti |
| 223 | 0.03799 | Geçti |
| 227 | 0.06360 | Kaldı |
| 229 | 0.12033 | Kaldı |

## Protokol düzeltmesi

V1 development preflight'ta fotonik aday `0.03330`, kayıpsız aynı-feature dijital
ikiz `0.02646` verdi. Gürültülü fiziksel uygulamanın kendi kayıpsız matematiksel ikizini
`%10` yenmesini istemek mantıksal olarak imkânsızdı. V1, kör değerlendirme sayısı `0`
iken emekliye ayrıldı.

V2 yeni ve ayrık bir kör suite kullandı. Dijital ikiz, üstünlük hedefi değil fiziksel
uygulama cezasını raporlayan üst sınır yapıldı. Fotonik katkı, aynı delay belleğine
sahip lineer kontrol ve belleksiz no-PIC kontrolüne karşı ölçüldü.

## Aday kilidi ve yeniden üretilebilirlik

- Protokol: `configs/p0_narma10_protocol_v2.json`.
- Protokol SHA-256: `e6cbd95e7aa6b5b3aae9f73172099e4c591db334b2a7f0497768f999c70073f8`.
- Candidate config SHA-256: `c7c36b289bf1bdc0689f45b280f807ceaed3c470690cfe36cfd21be023baaa3c`.
- Kilitli source SHA-256: `a0e6561a726a6d17a31dd1bde37257435f857549cb726d711bea6e5c4a17a080`.
- Candidate lock SHA-256: `664904b350efaa84a65e5f57a5119042f196753ccd4e7e6d11e851395e5c247d`.
- Kör sonuç SHA-256: `b263292fd0226c10cc3b0096350176cb14771e258f2eacd89c2952ace9219028`.
- Kör dataset: `10`; toplam candidate/control test değerlendirmesi: `40`.
- Yetkili çıktı `runs/blind-v2.json` oluştuğu için aynı koşu yeniden çalıştırılamaz.

## İddia sınırı

Başarı, fiziksel-parametreli sistem simülasyonu içindir. Gerçek PIC, layout, bileşen
ölçümü veya FDTD kanıtı değildir. Optik mimari dijital ikizden daha doğru değildir;
değeri, quadratic temporal özellikleri fiziksel koherent girişim ve photodetection ile
üretirken kör NARMA-10 hedefini geçmesidir.

## Araştırma hattı bağlantıları

- [Photonic Reservoir proje merkezi](../docs/_source_records/project-hub-note.md)
- [P4 seçilen aday](../p4-optimization/RESULTS.md)
- [P0 protokol geçmişi](../P0-BENCHMARK-AND-BLIND-PROTOCOL.md)
- [Kabul protokolü](../MODEL-AND-ACCEPTANCE.md)
- [Güncel handoff](../docs/_source_records/HANDOFF.md)
