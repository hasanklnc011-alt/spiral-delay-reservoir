# P6 Physical Validation Handoff

Güncelleme: 2026-09-05

## Değişmezler

- P5 blind yeniden çalıştırılmaz ve hiçbir P6 tuning kararına geri beslenmez.
- Blind hash: `b263292fd0226c10cc3b0096350176cb14771e258f2eacd89c2952ace9219028`.
- Candidate-lock hash: `664904b350efaa84a65e5f57a5119042f196753ccd4e7e6d11e851395e5c247d`.
- Kesit `343×180 nm` custom-process olarak korunur; hazır 220 nm PDK göçü yok.
- Legacy üç-ring ve eski `tidy3d_small_ring` çıktıları salt-okunur.

## Güncel fiziksel hüküm

- G1, G2, G3-A, G3-B ve model/provenance kapıları: `5/11 PASS`.
- G3-C ve G3-D: `FAIL/REDESIGN`.
- Propagation cutback, switch, PD/TIA ve thermal: dört `OPEN`.
- G5/G6: `NOT_PHYSICALLY_ACCEPTED`.

## Son tamamlanan iş

- Custom-process inverse-design ID0–ID2 tamamlandı.
- ID1 splitter/combiner üçer kaydedilmiş coarse-3D Adam adımıyla seed üretti.
- Binary ID2 üç broadband FDTD solve'u toplam `0.16920 FC` tahminle tamamlandı.
- Splitter worst excess/reflection: `3.494 dB / -16.22 dB`.
- Combiner worst excess/imbalance/quadrature/reflection:
  `5.466 dB / 5.160 dB / 15.62° / -15.42 dB`.
- İki aday ID2'yi geçmedi; ID3 convergence/corners çalıştırılmadı.
- Kanıt: `runs/inverse-design-id2-binary-fdtd-v1.json` ve üç HDF5.
- Testler: `112/112 PASS`; JSON parse ve `git diff --check` temiz.

## Dönüşte tek teknik karar

Yeni ücretli solve başlatmadan önce iki yoldan biri seçilmeli:

1. Effective-index/2D continuation ile çok daha uzun, beta-ramped ve
   üretilebilirlik-kısıtlı yeni seed hattı kurmak; ardından yeni binary ID2/ID3.
2. Custom foundry'den CP0 kuralları ve qualified splitter/combiner kompleks
   S-parametrelerini edinmek.

CP0 olmadan minimum feature/gap proxy kabul değildir. CP1–CP5 ölçümleri gelmeden
G4/G5 kapatılmaz. Tamamlanmış task'lar tekrar çalıştırılmaz.

## Araştırma hattı bağlantıları

- [P6 durum](STATUS.md)
- Inverse-design protokolü
- [Custom-process doğrulama](CUSTOM-PROCESS-VALIDATION.md)
- [Proje merkezi](../docs/_source_records/project-hub-note.md)
