---
title: Photonic Reservoir Çalışması
type: project
status: active
created: 2026-08-26
---

# Photonic Reservoir Çalışması

## Amaç

Ring tabanlı fotonik reservoir modelini, memory capacity ve NARMA görevleriyle
incelemek; lineer ve doğrusal olmayan modelleri karşılaştırmak.

## Orijinal çalışma konumu

`C:\Users\hasan\OneDrive\Desktop\eski dosyalarım\photonic_reservoir`

Orijinal kod ve Tidy3D verileri salt-okunur kanıt kaynağıdır. Yeni kanonik,
Git-izlenebilir TCMT paketi bu proje klasöründedir.

## 2026-08-28 kanonik uygulama

- `src/photonic_reservoir/` — enerji-normalize üç-ring TCMT, fiziksel Kerr,
  explicit kompleks delay-feedback, ridge/ESN baselineları ve validation-only arama.
- `configs/` — smoke, NARMA-10 tarama, seçilmiş üç-ring ve seçilmiş delay adayları.
- `runs/` — üzerine yazılmayan config/commit/claim-level manifestleri ve metrikler.
- `evidence/` — eski Tidy3D dosya hash'leri ve sıkı FDTD kanıt denetimi.
- [[🏰 300-Projects/Photonic-Reservoir/MODEL-AND-ACCEPTANCE|Model ve kabul protokolü]].
- [[🏰 300-Projects/Photonic-Reservoir/P0-BENCHMARK-AND-BLIND-PROTOCOL|P0 benchmark ve kör test protokolü]].

## Doğrulanmış yeni sonuçlar

- 17 deterministik test geçiyor; analitik steady-state ve zaman-adımı yakınsaması dahil.
- NARMA-3 smoke: üç-ring `NMSE ≈ 0.0687`, delayed-input `≈ 0.2032`, ESN `≈ 0.1040`.
- Validation-only NARMA-10 seçimi: `Nv=20`, `T_sym=0.2 ps`, detuning
  `[-0.5, 0, +0.5]` linewidth, coupling `0.45` linewidth.
- Seçilmiş üç-ring NARMA-10: `NMSE ≈ 0.4281`; delayed-input `≈ 0.3609`, ESN `≈ 0.2759`.
- Delay pivotu (`τd=1 sembol`, `η=0.8`, `φ=0`) ile `NMSE ≈ 0.3502`; ancak güven
  aralığı sıfırı kesiyor ve uncoupled/single-ring feedback `≈ 0.3492` ile daha iyi.
- Fiziksel SiN Kerr etkisi bütün taramalarda ihmal edilebilir düzeyde; Kerr avantajı yok.
- Eski üç-ring FDTD statik spektrumu güçte iyi görünse de kompleks NMSE `≈ 1.18`;
  dinamik üç-ring FDTD doğrulaması yoktur. Yeni cloud koşusu yetkilendirilmedi.

## Dosya haritası

- `ring_model.py` — ring modeli
- `reservoir.py` — reservoir yapısı
- `analysis.py` — analizler
- `params.py` — parametreler
- `main.py` — ana çalıştırma akışı
- `fig_memory_capacity.png` — memory capacity sonucu
- `fig_narma3_results.png` — NARMA-3 sonucu
- `fig_narma10_results.png` — NARMA-10 sonucu

## Sonraki işler

- [x] P0: NARMA-10 dataset/split/hash sözleşmesini ve kör-test aday kilidini kur.
- [ ] P1: full-quadratic oracle ile coherent square-law hipotezini development validation üzerinde yeniden üret.
- [x] Sonuçları, parametreleri, seed/split ve kanıt seviyelerini manifestlerle ayır.
- [x] Input-only, delayed-input, ESN, Kerr-off, coupling-off ve memory-reset kontrollerini kur.
- [x] Statik FDTD spektrumunun dinamik benchmark olmadığını denetle ve belgeleyerek düzelt.
- [ ] Ren et al. tam metnini edinip high-Q lineer MRR memory-array modelini çıkar.
- [ ] Belleğin halkalardan geldiğini gösterecek high-Q/on-chip multi-delay mimari tasarla.
- [ ] Yeni aday NARMA-10 yayın kapısını geçmeden Tidy3D cloud koşusu başlatma.

## Literatür taraması

- [[🏰 300-Projects/Photonic-Reservoir/MRR-RNN-Literatur-Taramasi|MRR RNN - Literatür Taraması]]

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/3 halkalı Ring/Tidy3D-Small-Ring|Tidy3D Small-Ring FDTD]]
- [[🏰 300-Projects/2D FDFD tabanlı, fixed-point ve truncated RNN/2D FDFD tabanlı, fixed-point ve truncated RNN|FDFD Kerr Photonic RNN]]
- [[🧠 500-Knowledge/concepts/Photonic-Research-Lines-Synthesis|Fotonik araştırma hatları sentezi]]
