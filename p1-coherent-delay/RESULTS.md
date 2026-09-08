---
title: P1 Coherent Delay — ideal-v1 Sonuçları
type: project-note
status: complete
created: 2026-09-03
---

# P1 Coherent Delay — ideal-v1 Sonuçları

## Sonuç

Önceden tanımlanan P1 kapısı geçti: 10 development seed üzerinde ideal coherent
field-u square-law modelinin medyan validation NMSE değeri `0.022534 ≤ 0.04`.
Kör yayın verisi açılmadı ve test değerlendirmesi yapılmadı.

| Varyant | Özellik/kanal | Medyan validation NMSE | `≤0.04` seed |
|---|---:|---:|---:|
| Full-quadratic dijital oracle | 230 | 0.022164 | 9/10 |
| Coherent field-u + PD square-law | 230 | 0.022534 | 9/10 |
| Coherent sqrt-power + PD square-law | 230 | 0.022450 | 9/10 |
| Coherent field-u, LO yok | 210 | 0.025093 | 9/10 |
| Lineer 20-lag | 20 | 0.154694 | 0/10 |

## Doğrulanan hipotez

`E_i = u[t-i]` alan encoding'i için `|E_i|²`, `|LO+E_i|²` ve
`|E_i+E_j|²` intensity kanalları, lineer readout altında tüm lineer lag ve
çapraz `u_i u_j` terimlerini span eder. Testte bu basis ile dijital oracle arasındaki
en büyük seed-bazlı NMSE farkı `3.75×10⁻⁴` oldu.

## Sınırlar

- Bu bir ideal özellik-uzayı üst sınırıdır; 230 bağımsız intensity kanalı fiziksel
  port, tap veya zaman-multiplex mimarisine henüz eşlenmedi.
- Kayıp, faz hatası, coherence drift, detector noise, splitter bütçesi ve alan yoktur.
- Seed 23 her quadratic varyantta zordur: coherent field-u NMSE `0.073943`.
  Medyan kapısı geçmiştir fakat bütün seed'ler `<0.04` değildir.
- `sqrt(power)` encoding'in benzer sonucu, fiziksel eşdeğerlik kanıtı değildir; geniş
  230-kanal basis'in güçlü bir yaklaşım uzayı sunduğunu gösterir.

## Kanıt dosyaları

- Config: `configs/ideal-v1.json`.
- Sonuç: `runs/ideal-v1.json`.
- Sonuç SHA-256: `450aea478c75bdf0dc7d7efd0d4134336d49e1e4b5846b6e0b8069b1e6afd510`.
- Koşu: development-only, `test_evaluations=0`.
- Regresyon: 35/35 test.

## Karar

P1 tamamlandı. P2, 230 ideal kanalı fiziksel olarak uygulanabilir sınırlı-port veya
time-multiplex mimariye indirgerken validation medyanını `≤0.04` tutmaya çalışacak.

## Araştırma hattı bağlantıları

- [Photonic Reservoir proje merkezi](../docs/_source_records/project-hub-note.md)
- [P0 benchmark protokolü](../P0-BENCHMARK-AND-BLIND-PROTOCOL.md)
- [Güncel kabul protokolü](../MODEL-AND-ACCEPTANCE.md)
- [P1 çalışma alanı](README.md)
