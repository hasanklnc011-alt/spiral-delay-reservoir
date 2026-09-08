# P5 — Aday Kilidi ve Tek Kör Test

P5 önce yalnız development verisinde yayın kontrollerini çalıştırır. Adayın doğruluk,
üç kontrol karşısında `%10` göreli kazanım ve eşleştirilmiş bootstrap CI üst sınırı
kapılarının tamamı geçmeden candidate lock üretilemez ve kör suite açılamaz.

`same_delay_digital`, seçilmiş aynı 30 quadratic özelliğin kayıpsız/gürültüsüz dijital
ikizidir. Bu kontrol fiziksel fotonik katkı iddiasını en sert biçimde sınar; sonucuna
göre protokolün mantıksal uygulanabilirliği ayrıca değerlendirilecektir.

## Sonuç

V1 preflight, fiziksel adayın kendi kayıpsız dijital ikizini `%10` yenmesini istediği
için mantıksal olarak geçersiz bulundu; kör test açılmadan emekliye ayrıldı. V2'de
dijital ikiz raporlanan üst sınır, delayed-input ve no-PIC ise üstünlük kontrolleridir.

V2 aday kilidi sonrası yapılan tek kör koşu geçti: medyan test NMSE `0.038705`, 8/10
seed `<0.05`; delayed-input'a karşı `%74.7`, no-PIC'e karşı `%94.9` kazanç. Dijital
ikize göre fiziksel ceza `%19.2`. Ayrıntılar:
[[🏰 300-Projects/Photonic-Reservoir/p5-publication/RESULTS|P5 kör test sonuçları]].

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Photonic Reservoir proje merkezi]]
- [[🏰 300-Projects/Photonic-Reservoir/p4-optimization/RESULTS|P4 seçilen aday]]
- [[🏰 300-Projects/Photonic-Reservoir/P0-BENCHMARK-AND-BLIND-PROTOCOL|P0 kör test protokolü]]
- [[🏰 300-Projects/Photonic-Reservoir/MODEL-AND-ACCEPTANCE|Kabul kapıları]]
