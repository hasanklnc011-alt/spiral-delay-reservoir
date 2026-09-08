# P6 G6 Fiziksel Kabul Denetimi

## Hüküm

`NOT_PHYSICALLY_ACCEPTED` — P6 kanıt zinciri fail-closed denetlendi. 11 kapının
5'i geçti; 2'si yeniden tasarım gerektiren fiziksel FAIL, 4'ü harici aygıt/PDK
kanıtı bekleyen OPEN durumunda. P5 kör sonucu yeniden çalıştırılmadı.

| Kapı | Durum | Ana kanıt |
|---|---|---|
| G0 provenance | PASS | Blind/candidate hash kilidi |
| G1 kesit/delay | PASS | 343×180 nm, `n_g=4.01297` |
| G2 layout | PASS | 14.240061 cm exact GDS route |
| G3-A straight | PASS | m20/m25 lossless de-embedding |
| G3-B bend/crosstalk | PASS | R10 ve pitch 5 µm |
| G3-C tap/splitter | FAIL/REDESIGN | DC, Y, iki MMI serisi, slot-opening ve width-doubling-free union-Y kapıları geçmedi |
| G3-D combiner | FAIL/REDESIGN | İki kaynaklı FDTD pilotu ve EME uzunluk ekranı imbalance/excess/reflection/faz kapılarını birlikte geçmedi |
| G4 fast switch/faz | OPEN | 30 GHz aygıt S-parametresi yok |
| G4 PD/TIA | OPEN | 50 GHz saturation/noise/lineerlik kanıtı yok |
| G4 thermal | OPEN | `PπL`, time constant ve crosstalk solve yok |
| G5 composition | OPEN | Eksik aygıt kayıpları compose edilemiyor |

## Fiziksel olarak ayakta kalanlar

- Delay kesiti, exact spiral route, R10 bend ve adjacent-turn crosstalk kanıtları
  P6 component-validation kapsamında geçerli.
- `0.8 dB/cm` assumption-only propagation ile delay+bend `0.8974 dB/cm`; stress
  zarfı içinde, ancak PDK/cutback olmadan fiziksel kayıp kabulü değil.
- 10 PD × 3 slot routing semantiği geçerli; thermal yalnız statik trim, slot
  seçimi hızlı EO/switch katmanıdır.

## Devam için zorunlu kanıt

1. Foundry-qualified tap/splitter kompleks S-matrisi veya ayrı EME/inverse-design ile optimize edilmiş hücre.
2. Foundry-qualified veya yeniden tasarlanmış reciprocal 2×2 combiner kompleks S-matrisi ve passivity/coherent-transfer testi.
3. Seçilmiş custom process için fabricated cutback, 30 GHz switch, birlikte
   ölçülmüş 50 GHz PD/TIA ve `30×30` thermal test matrisi.
4. Bu girdiler geldikten sonra G5 yeniden compose edilir; kör P5 skoru koşulmaz.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/P6-PROTOCOL|P6 protokolü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G3C-STATUS|G3-C durumu]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G3D-STATUS|G3-D durumu]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G4-STATUS|G4 durumu]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G5-STATUS|G5 durumu]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/CUSTOM-PROCESS-VALIDATION|Custom-process doğrulama planı]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/STATUS|P6 durum]]
- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Proje merkezi]]
