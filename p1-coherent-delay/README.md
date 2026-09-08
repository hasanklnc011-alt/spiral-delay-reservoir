# P1 — Coherent Delay İdeal Hipotez Doğrulaması

Bu alan yalnız yeni P1 deneyleri içindir. Eski üç-ring config veya run dosyaları
buraya kopyalanmaz.

## Girdi

- `../configs/p0_narma10_protocol.json` içindeki development suite.
- Ortak leakage-safe ridge ve NMSE tanımı.

## İlk deneyler

1. Full-quadratic dijital oracle.
2. Field `∝ u` ve field `∝ sqrt(P)` encoding ayrımı.
3. Coherent delayed-field toplamı + photodiode square-law.
4. Aynı delay ve feature bütçeli lineer/dijital kontroller.

## Geçiş kapısı

10 development seed üzerinde medyan validation NMSE `≤0.04`. Test slice yoktur.

## Sonuç — ideal-v1

P1 geçiş kapısı geçti. Kanonik sonuç:
[[🏰 300-Projects/Photonic-Reservoir/p1-coherent-delay/RESULTS|P1 ideal-v1 sonuçları]].

- Full-quadratic oracle: `0.022164` medyan validation NMSE.
- Coherent field-u square-law: `0.022534`.
- Lineer 20-lag kontrolü: `0.154694`.
- Kör/test değerlendirmesi: `0`.

Bu sonuç 230 ideal intensity kanallı bir üst sınırdır; fiziksel PIC sonucu değildir.

## Dizinler

- `configs/` — P1 development config'leri.
- `runs/` — P1 validation-only çıktıları.
- Kod: `src/photonic_reservoir/p1_coherent_delay/`.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Photonic Reservoir proje merkezi]]
- [[🏰 300-Projects/Photonic-Reservoir/P0-BENCHMARK-AND-BLIND-PROTOCOL|P0 benchmark protokolü]]
- [[🏰 300-Projects/Photonic-Reservoir/MODEL-AND-ACCEPTANCE|Güncel kabul protokolü]]
