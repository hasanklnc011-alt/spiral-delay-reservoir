---
title: Photonic Reservoir NMSE < 0.05 — Handoff
type: handoff
status: active
updated: 2026-09-03
---

# Photonic Reservoir NMSE < 0.05 — Handoff

## Güncel amaç

Fiziksel olarak uygulanabilir, on-chip optik çekirdeğe sahip bir sistemde kör 10-seed
NARMA-10 medyan test NMSE `<0.05` elde etmek ve kazanımın fiziksel kaynağını kontrollerle göstermek.

## Tamamlanan

- P0 development ve blind suite'leri exact dataset SHA-256 ile ayırdı; kör kapı kapalı.
- Eski üç-ring hattı `legacy-three-ring/` altına ayrıldı.
- P1 ideal coherent square-law üst sınırı `0.022534` medyan validation NMSE verdi.
- P2, 230 ideal kanalı tek photodiode ve 20 time-multiplex slota indirdi.
- 20-slot minimum aday: medyan `0.039716`, 8/10 seed `≤0.05`.
- 30-slot headroom adayı: medyan `0.026459`, 9/10 seed `≤0.05`.
- Rastgele MZI maskeleri ancak yaklaşık 230 ölçümde kapıyı geçti; sparse görev-odaklı aile seçildi.
- P3 nominal sistem modeli geçti: 30 özellik, 10 photodiode × 3 slot, medyan
  `0.038246`, 9/10 seed `≤0.05`.
- Tek-PD 30-slot gerçek-zaman bandwidth kapısında, 20 özellikli aday nominal doğruluk
  kapısında elendi. Stres profili henüz geçmedi.
- P4 robust optimizasyon geçti: 30 kanal, 10 PD × 3 slot, kol başına 5 mW sinyal ve
  5 mW LO; nominal medyan `0.027499`, stres medyan `0.033723`.
- Her profil 5 hardware × 10 data koşusunda 45/50 başarı verdi. Seed 23 bütün hardware
  realizasyonlarında sistematik outlier kaldı.
- P5 v1 preflight, kayıpsız dijital ikizi yenme şartının mantıksal olarak imkânsız
  olduğunu gösterdi; v1 kör test `0` iken emekliye ayrıldı.
- V2 protokol, yeni ayrık kör suite ve kilitli adayla tek kez çalıştı. Kör medyan test
  NMSE `0.038705`, 8/10 seed `<0.05`; yayın kapısı geçti.
- Delayed-input'a karşı `%74.7`, no-PIC'e karşı `%94.9` kazanç sağlandı; dijital ikize
  göre fiziksel ceza `%19.2` olarak açıkça raporlandı.

## Kanıt

- Kanonik P2 koşusu: `p2-architecture/runs/screen-v4-pareto.json`.
- P2 sonuç SHA-256: `9207253bd00634da699c6d13c82a8025977cef20d6e4bb530d0d165d6e87405d`.
- Kayıt sırasında kör/test değerlendirmesi: `0`.
- P3 V2 sonuç SHA-256: `0f08e6291bde6ed26144a14e8ea7481f9e1e65939697d87a1db51eeb3095129f`.
- P4 stres confirmation SHA-256: `44fa69e447ac10b1fd6564185eb30db7c9f8759b9b7758025d7c4a4a9a719a17`.
- P4 nominal confirmation SHA-256: `9de948e459f3f8f833a3da4a14d00fc0c09aea3e991823244468b0ba556e9416`.
- P5 v2 protokol SHA-256: `e6cbd95e7aa6b5b3aae9f73172099e4c591db334b2a7f0497768f999c70073f8`.
- P5 kör sonuç SHA-256: `b263292fd0226c10cc3b0096350176cb14771e258f2eacd89c2952ace9219028`.
- Son regresyon: 50/50 test.

## Sıradaki tek adım — P6

Kör sonuca göre tuning yapmadan seçilmiş mimarinin fiziksel uygulanabilirliğini yükselt:
14.24 cm delay routing/spiral alanı, bend ve splitter loss, 10 coherent combiner/PD kolu,
faz kontrolü ve termal güç bütçesi için bileşen düzeyi model ve yalnız seçilmiş kritik
bileşenlerde EM/FDTD doğrulama planı kur. P5 kör sonucu değişmez yayın kanıtı olarak kalır.

## Kullanılmayacak kaynaklar

- `legacy-three-ring/runs/` skorları aday seçimi için kullanılmaz.
- P3 sistem modeli bileşen ölçümü veya FDTD doğrulaması diye sunulmaz.
- Başarısız V1 ve stres sonucu silinmez; P4 optimizasyonuna görünür girdi kalır.
- Seed 23 outlier'ını gizlemek için development veya kör seed listesi değiştirilmez.
- Kör seed 227 ve 229 sonuçları yeni tuning için kullanılmaz; P5 v2 yeniden çalıştırılmaz.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Photonic Reservoir proje merkezi]]
- [[🏰 300-Projects/Photonic-Reservoir/P0-BENCHMARK-AND-BLIND-PROTOCOL|P0 benchmark protokolü]]
- [[🏰 300-Projects/Photonic-Reservoir/MODEL-AND-ACCEPTANCE|Güncel model ve kabul protokolü]]
- [[🏰 300-Projects/Photonic-Reservoir/p2-architecture/RESULTS|P2 mimari sonuçları]]
- [[🏰 300-Projects/Photonic-Reservoir/p3-realistic/RESULTS|P3 gerçekçi sistem sonuçları]]
- [[🏰 300-Projects/Photonic-Reservoir/p4-optimization/RESULTS|P4 robust optimizasyon sonuçları]]
- [[🏰 300-Projects/Photonic-Reservoir/p5-publication/RESULTS|P5 tek kör test sonuçları]]
- [[🏰 300-Projects/Photonic-Reservoir/MRR-RNN-Literatur-Taramasi|MRR/RNN literatür taraması]]
