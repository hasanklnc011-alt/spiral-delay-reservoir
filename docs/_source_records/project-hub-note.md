> **Source record (Turkish), kept verbatim.** See [`docs/PROJECT_OVERVIEW.md`](../PROJECT_OVERVIEW.md).

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

- [P0 benchmark ve kör test protokolü](../../P0-BENCHMARK-AND-BLIND-PROTOCOL.md)
- [Model ve kabul protokolü](../../MODEL-AND-ACCEPTANCE.md)
- [Güncel handoff](HANDOFF.md)
- [P1 ideal-v1 sonuçları](../../p1-coherent-delay/RESULTS.md)
- [P2 mimari sonuçları](../../p2-architecture/RESULTS.md)
- [P3 gerçekçi sistem sonuçları](../../p3-realistic/RESULTS.md)
- [P4 robust optimizasyon sonuçları](../../p4-optimization/RESULTS.md)
- [P5 tek kör test sonuçları](../../p5-publication/RESULTS.md)

## Legacy sınırı

`legacy-three-ring/` içindeki sonuçlar tarihsel kanıttır. Yeni aday seçimi, başarı
iddiası veya başlangıç parametresi olarak kullanılmaz. Gerektiğinde yalnız başarısızlık
modu ve kontrol tasarımı öğrenmek için okunur.

## Araştırma hattı bağlantıları

- [MRR/RNN literatür taraması](../references/literature_review.md)
- [P0 benchmark protokolü](../../P0-BENCHMARK-AND-BLIND-PROTOCOL.md)
- Fotonik araştırma hatları sentezi (MayOS vault note, outside this repository)
