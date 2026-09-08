# P3 — Gerçekçi Kayıp, Gürültü ve Tolerans

## Amaç

P2'nin 30-slot headroom adayı ile 20-slot minimum kontrolünü sistem-seviyesi fiziksel
bozulmalar altında yalnız P0 development validation üzerinde sınamak.

## V1 modeli

- Gecikmeye bağlı waveguide kaybı ve toplam fiziksel delay uzunluğu.
- Switch ve combiner insertion loss.
- Finite extinction kaynaklı inactive-tap leakage.
- Statik ve dinamik faz hatası, LO amplitude drift'i.
- Photodiode responsivity, shot noise ve input-referred thermal noise.
- Tek/çok-port multiplex zamanlaması, detector low-pass cevabı ve bandwidth kapısı.
- 10 GBd gerçek-zaman hedefinde delay uzunluğu, detector bandwidth ve switch-rate kapıları.

## Başarı ve durma koşulu

Nominal profilde medyan validation NMSE `≤0.04`, en az 8/10 seed `≤0.05` ve bütün
fiziksel zaman/uzunluk kapıları birlikte geçmelidir. Hiçbir nominal aday geçmezse
mimari yeniden açılır; kör test çalıştırılmaz. P3 v1 bir sistem modelidir, bileşen/FDTD
doğrulaması değildir.

## Sonuç

V1, alıcının tüm 50 GHz donanım bant genişliğini gürültü bant genişliği saydığı için
nominal profilde `0.0515` ile başarısız oldu ve korundu. Düzeltilmiş V2, gürültü bant
genişliğini gerçek slot hızına eşledi. En küçük geçen nominal mimari 30 özellik için
10 parallel photodiode × 3 time slot oldu: medyan `0.038246`, 9/10 seed `≤0.05`.
Tek-PD 30-slot düzen gerçek-zaman bandwidth/switch kapılarını geçmedi.

Ayrıntılar: [P3 sonuçları](RESULTS.md).

## Devamlılık checkpoint'i

Kanonik config `configs/screen-v1.json`, koşu girişi `scripts/run_p3_screen.py` ve testler
`tests/test_p3_realistic.py` içindedir. Kesinti olursa önce bu not ve proje `HANDOFF.md`
okunur; var olan run dosyası üzerine yazılmaz.

## Araştırma hattı bağlantıları

- [Photonic Reservoir proje merkezi](../docs/_source_records/project-hub-note.md)
- [P2 mimari sonuçları](../p2-architecture/RESULTS.md)
- [Kabul protokolü](../MODEL-AND-ACCEPTANCE.md)
- [Güncel handoff](../docs/_source_records/HANDOFF.md)
