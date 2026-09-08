---
title: MRR RNN Araştırması - Oturum Devri
type: handoff
status: active
created: 2026-08-28
updated: 2026-09-03
---

# MRR RNN Araştırması — Handoff

## Oturum durumu

2026-08-28 oturumu Hasan'ın isteğiyle kapatıldı. Proje aktif fakat beklemededir.
Geri dönüşte bu dosya kanonik başlangıç noktasıdır.

## Amaç ve kapsam

SiN mikro-ringlerle fiziksel olarak savunulabilir recurrent/reservoir computation
geliştirmek. İlk yayın hedefi NARMA-10'dur. Si taşıyıcı/termal fiziği, FDFD solver
iterasyonu ve Tait weight-bank CTRNN bu modelle karıştırılmaz.

## Tamamlananlar

- Enerji-normalize üç-ring TCMT, fiziksel Kerr, direct/coherent readout ve kompleks
  interpolasyonlu delay-feedback tek pakette kuruldu.
- NARMA, leakage-safe ridge, input-only/delayed-input, eşit durumlu ESN, coupling-off,
  memory-reset, single-ring ve Kerr ablationları uygulandı.
- Validation-only iki aşamalı üç-ring ve delay aramaları tamamlandı; test seti yalnız
  aday kilitlendikten sonra değerlendirildi.
- 17 test geçiyor: analitik steady-state, zaman-adımı yakınsaması, determinism,
  delay, NARMA hizası, split ve cloud-gate güvenliği dahil.
- Eski Tidy3D kanıtları SHA-256 manifestine alındı; orijinal dosyalara dokunulmadı.

## Doğrulanmış sonuçlar

- NARMA-3: üç-ring `0.0687`, delayed-input `0.2032`, ESN `0.1040` medyan NMSE.
- NARMA-10 seçilmiş üç-ring-only: `0.4281`; delayed-input `0.3609`, ESN `0.2759`.
- Seçilmiş delay (`1 sembol`, `η=0.8`, `φ=0`) + üç-ring: `0.3502`.
- Aynı delay ile uncoupled/single-ring: `0.3492`. Delay **açıkken** kazanç üç-ring
  coupling'den değil feedback memory'den geliyor. Bu cümle rejime bağlıdır: delay
  **kapalıyken** coupling ciddi katkı veriyor (NARMA-10 `0.4281` vs uncoupled
  `0.5684`; NARMA-3 `0.0687` vs `0.2324`). Coupling ölü değil, güçlü task-aligned
  feedback geldiğinde sağladığı bellek tabanı gereksizleşiyor.
- `three_ring_uncoupled` ile `single_ring` beş koşunun hepsinde dört ondalıkta aynı.
  Bu fiziksel bir bulgu değil, kodun zorunlu sonucu: coupling sıfırken ring 2 ve 3
  ne sürülüyor (`model.py` yalnız `a[0]`'ı sürer) ne de okunuyor (`through_field`
  yalnız `a[0]`'ı görür). Bu ablation "halkalar birbirinin kopyası" iddiasını
  taşıyamaz.
- Delay adayının delayed-input'a medyan üstünlüğü yalnız `%3`; eşleştirilmiş `%95`
  CI `[-0.0475, 0.0207]`, yani yayın kapısı geçilmedi.
- Fiziksel Kerr açık/kapalı farkı yaklaşık `10⁻⁶` göreli seviyede ve avantaj değil.
- Eski üç-ring statik FDTD: power NMSE `0.154`, power corr `0.980`, fakat global
  kompleks gain sonrası kompleks NMSE `1.180`; sıkı fiziksel kapı başarısız.
- Eski tek-ring transient: corr `0.971`, NMSE `0.202`; `<0.2` kapısını az farkla geçemedi.
- Dinamik üç-ring FDTD benchmarkı yoktur; cloud kapısı kapalıdır.

## Kanonik dosyalar

- [Proje merkezi](../../docs/_source_records/project-hub-note.md)
- [Model ve kabul protokolü](../../MODEL-AND-ACCEPTANCE.md)
- `src/photonic_reservoir/`, `configs/`, `runs/`, `evidence/`, `tests/`

## Kararlar

- “FDTD-fitted TCMT” hiçbir yerde doğrudan “FDTD benchmarkı” diye adlandırılmayacak.
- Kerr yalnız fiziksel `n₂` ile istatistiksel avantaj verirse katkı olarak sunulacak.
- Mevcut düşük-Q üç-ring-only ve tek-delay hibrit aday için yeni cloud kredisi harcanmayacak.
- NARMA-3 kontrol görevidir; yayın ve FDTD kapısını yalnız tam 10-seed NARMA-10 açabilir.

## Açık riskler

- Mevcut Q/lifetime NARMA-10 belleği için kısa.
- Delay-loop sonucu coupling ablation'ında korunuyor; mevcut halkalar hesaplamaya anlamlı
  ek durum sağlamıyor.
- Fiziksel SiN Kerr kayması mevcut güç/Q aralığında çözünür değil.
- Ren et al. high-Q lineer MRR array makalesinin tam parametre kartı hâlâ eksik.

## 2026-09-03 P0 güncellemesi

`NMSE < 0.05` yeni hedefi için P0 benchmark ve kör test sözleşmesi kuruldu.
`configs/p0_narma10_protocol.json` geliştirme ile kör yayın suite'ini ayırır; exact
dataset hash'lerini ve aday-kilidi zorunluluğunu taşır. Eski yayın config'indeki
seed 83 tam uzunlukta patladığı için geçersizdir; clipping yapılmaz. Eski test
seed'leri geliştirme verisi sayılır.

Sıradaki tek adım **P1 ideal hipotez doğrulamasıdır**: full-quadratic dijital oracle
ile doğru field encoding kullanan coherent square-law model, yalnız development
train/validation üzerinde ortak split'le yeniden üretilecek. Medyan validation
NMSE `≤0.04` olmazsa bu dal fiziksel ayrıntıya geçmeden durur. Kör test kapalıdır.

## Önceki yön notu — P0 kararıyla ertelendi

**State observability** (2026-09-02'de öne alındı). Hasan ring 2 ve 3'ten fiziksel
drop/tap output alınabileceğini doğruladı, bu yüzden bu yön Ren et al. high-Q
yönünün önüne geçti.

Gerekçe: issue-01 doğrulaması, seçilmiş reservoir'un erişilebilir state boyutunun
çöktüğünü gösterdi — participation rank `1.03` (delay yok) / `1.35` (delay var),
varyansın %98.7'si tek yönde. Üç halkanın state'i var ama tek through-port'tan
okunuyor. Q'yu artırmadan önce mevcut state'in okunabilir olup olmadığını çözmek
gerekiyor; aksi hâlde yüksek-Q bir array de aynı tek kanaldan gözlenecek.

Kur: `through_field` yerine fiziksel port matrisi, `s_out = C·s_in + D·a`. Ring 2/3
çıkışını doğrudan ridge'e verip "physical readout" deme — okuyacak tap/drop
coupling'i TCMT'de modellenmeli. Ablation: mevcut tek through-port / fiziksel
multi-port, aynı toplam readout feature bütçesiyle, coupling açık/kapalı.

B4 (fiziksel geçerlilik kapısı) **çözüldü** ve bu yönü zorunlu kılıyor. Kalibre
edilen pencere kanıt dosyalarından ölçüldü: `193.623–196.023 THz`, 2.400 THz,
merkez `194.823 THz = 1538.79 nm`. Sonuç sert — mevcut arama ızgarasının altı
noktasının altısı da bandın dışında (en yavaşı bile 4.2 katı, seçilmiş aday
41.7 katı). Bandın içinde kalmak `n_virtual=20` için `T_sym ≥ 8.33 ps` demek, o
da `τ_f ≥ 1 sembol` için `Q ≳ 5100` demek; mevcut halkalar `462–1081`.

Yani geçerli rejim ile yararlı rejim bu Q'larda örtüşmüyor. Yeni aday üretmeden
önce `physical_validity()` çıktısına bak; artık her run manifest'inde.

Not: ring config'leri `1.55 µm` kullanıyor ama kalibrasyon `1538.79 nm` merkezli
— `-0.62 FSR` kayma. `FDTD-calibrated TCMT` etiketi bu kayma belirtilmeden
kullanılmaz.

Ren et al. tam metni sonra: high-Q lineer MRR memory-array/on-chip multi-delay
mimarisini aynı TCMT arayüzünde kur. Yeni aday önce validation-only NARMA-10 kapısını
geçmeli; geçmeden tam yayın koşusu veya Tidy3D cloud doğrulaması başlatma.

## Yeni sohbete başlangıç

> `Photonic-Reservoir/HANDOFF.md`, `Photonic-Reservoir.md`,
> `MODEL-AND-ACCEPTANCE.md` ve `runs/search_delay_narma10.json` dosyalarını oku.
> Mevcut üç-ring ve tek-delay adaylarını yeniden tarama. Sıradaki tek adımı uygula:
> high-Q MRR memory-array/on-chip multi-delay modelini kaynak denklemlerle kur ve
> validation-only NARMA-10 karşılaştırmasını yap.
