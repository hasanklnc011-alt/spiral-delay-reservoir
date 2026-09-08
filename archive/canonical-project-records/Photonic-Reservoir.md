---
title: Photonic Reservoir — NMSE < 0.05
type: project
status: active
updated: 2026-09-03
---

# Photonic Reservoir — NMSE < 0.05

## Amaç

Fiziksel olarak uygulanabilir on-chip optik çekirdekle NARMA-10 kör medyan NMSE
`<0.05` elde etmek. Üç-ring topolojisi zorunlu değildir; fiziksel katkı zorunludur.

## Güncel durum

- [x] P0 benchmark ve kör test protokolü kuruldu.
- [x] Eski üç-ring çıktıları yeni hattan fiziksel olarak ayrıldı.
- [x] P1 ideal quadratic/coherent hipotez doğrulaması: medyan `0.022534`, test açılmadı.
- [x] P2 mimari seçimi: minimum 20-slot tek-PD time-multiplex; P3 başlangıcı 30 slot.
- [x] P3 nominal fizik modeli: 10 PD × 3 slot, medyan `0.038246`, 9/10 seed.
- [x] P4 robust optimizasyon: nominal `0.027499`, stres `0.033723`, her ikisi 45/50 koşu başarılı.
- [x] P5 aday kilidi ve tek kör test: medyan `0.038705`, 8/10 seed; yayın kapısı geçti.
- [ ] P6 seçilmiş bileşen/FDTD doğrulaması.

## Güncel kanonik dosyalar

- [[🏰 300-Projects/Photonic-Reservoir/P0-BENCHMARK-AND-BLIND-PROTOCOL|P0 benchmark ve kör test protokolü]]
- [[🏰 300-Projects/Photonic-Reservoir/MODEL-AND-ACCEPTANCE|Model ve kabul protokolü]]
- [[🏰 300-Projects/Photonic-Reservoir/HANDOFF|Güncel handoff]]
- [[🏰 300-Projects/Photonic-Reservoir/p1-coherent-delay/RESULTS|P1 ideal-v1 sonuçları]]
- [[🏰 300-Projects/Photonic-Reservoir/p2-architecture/RESULTS|P2 mimari sonuçları]]
- [[🏰 300-Projects/Photonic-Reservoir/p3-realistic/RESULTS|P3 gerçekçi sistem sonuçları]]
- [[🏰 300-Projects/Photonic-Reservoir/p4-optimization/RESULTS|P4 robust optimizasyon sonuçları]]
- [[🏰 300-Projects/Photonic-Reservoir/p5-publication/RESULTS|P5 tek kör test sonuçları]]

## Legacy sınırı

`legacy-three-ring/` içindeki sonuçlar tarihsel kanıttır. Yeni aday seçimi, başarı
iddiası veya başlangıç parametresi olarak kullanılmaz. Gerektiğinde yalnız başarısızlık
modu ve kontrol tasarımı öğrenmek için okunur.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/MRR-RNN-Literatur-Taramasi|MRR/RNN literatür taraması]]
- [[🏰 300-Projects/Photonic-Reservoir/P0-BENCHMARK-AND-BLIND-PROTOCOL|P0 benchmark protokolü]]
- [[🧠 500-Knowledge/concepts/Photonic-Research-Lines-Synthesis|Fotonik araştırma hatları sentezi]]
