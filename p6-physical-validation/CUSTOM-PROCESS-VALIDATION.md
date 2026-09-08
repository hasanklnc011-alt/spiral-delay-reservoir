# P6 Custom-Process Doğrulama ve Test Aracı Planı

Güncelleme: 2026-09-04

## Kapsam kararı

Hasan'ın seçimiyle `343×180 nm` Si/SiO₂ kesit korunur. Hazır 220 nm PDK'ya
geçilmez; mevcut G1–G3 kanıtları yeniden adlandırılmaz. Bu belge, simülasyon
ön-tasarımını üretilebilir bir custom process'e bağlamak için gerekli minimum
foundry stack, test araçları ve ölçüm kabul sözleşmesidir.

P5 blind yeniden çalıştırılmaz; ölçüm sonuçları P5 parametre tuning'i için değil,
P6 fiziksel iddia sınırını PASS/FAIL yapmak için kullanılır.

## CP0 — proses ve referans düzlemi dondurma

Foundry'den tek sürümlü bir process manifest gerekir:

- Si çekirdek `180±5 nm`; nominal strip genişliği `343 nm`, width corner'ları
  en az `±10 nm`;
- BOX/üst kaplama kalınlıkları ve dispersif `n,k(T,λ)` verisi;
- minimum feature/gap, sidewall angle/roughness zarfı, metal keep-out ve via/metal
  stack;
- Ge/implant/contact modülleri ve heater sheet resistance/TCR;
- GDS layer map, sign-off DRC deck sürümü ve wafer/die kimliği.

Bu manifest mevcut `configs/g1-accepted-v1.json` ile uyuşmazsa G1 otomatik açılır.

## CP1 — passive delay test aracı

Tek die üzerinde aynı coupler referanslarını paylaşan straight cutback seti:
`0.5/1/2/4 cm`, R10 bend zincirleri ve seçilmiş `5 µm` pitch parallel-run yapıları.

- Propagation loss: wavelength-resolved linear fit; coupling intercept'i eğimden
  ayrılır ve fit güven aralığı raporlanır.
- P6 bütçesi: measured propagation üst güven sınırı `≤0.9026 dB/cm`; böylece
  ölçülmüş/EM bend katkısıyla toplam `≤1.0 dB/cm` kalır.
- Bend ve adjacent-turn sonuçları straight reference'a de-embed edilir.
- Full `14.240061 cm` spiral ayrı doğrulama yapısıdır; cutback eğiminin yerine geçmez.

## CP2 — splitter/tap ve coherent combiner

Jenerik başarısız hücreler tape-out adayı değildir. Yeni foundry/inverse-design
hücreleri için iki yönlü kompleks S-parametre test kuponu gerekir.

- Progressive tap: hedef `1/20…1/2,1` oranları; hücre başına excess `≤0.2 dB`;
  wavelength/corner hatası ve accumulated through loss birlikte raporlanır.
- LO tree: her 50:50 kademede imbalance `≤0.5 dB`, excess `≤0.2 dB`, reflection
  `<-30 dB`.
- 2×2 combiner: iki bağımsız giriş; excess hedef `≤0.5 dB`, hard `≤1.5 dB`,
  imbalance `≤0.5 dB`, quadrature error `≤5°`, reflection `<-30 dB` ve
  ölçülen tam kompleks matriste `S†S≤I`.
- Ölçüm: swept coherent receiver/OVA veya faz-referanslı interferometrik düzen;
  yalnız power spectrum kompleks S-matris kabulü değildir.

## CP3 — 30 GHz hızlı slot seçimi

Thermal heater yalnız statik trim'dir. Ayrı carrier-depletion MZI/ring/switch
test yapısı için optik ve RF reference plane birlikte tanımlanır.

- Kullanılabilir update rate `≥30 GHz`, elektriksel/EO bandwidth ve eye/settling;
- insertion loss `≤3 dB`, extinction `≥20 dB` ve üç slot arasında repeatable state;
- drive voltage, capacitance, driver energy ve phase/amplitude crosstalk;
- 1520–1580 nm bandı ve proses/ısı corner'ları.

## CP4 — 10 kollu PD/TIA doğrulaması

Ge PD ve gerçek TIA birlikte test edilir; tek başına PD bandwidth yeterli değildir.

- P5 uyumu: `BW≥50 GHz`, responsivity `≥0.8 A/W`, input-referred noise
  `≤20 pA/√Hz`;
- en az `4.5 mA` peak photocurrent'ta lineerlik, saturation, dark current,
  capacitance, TIA swing ve recovery;
- 10 kol mismatch'i, common laser noise ve ADC/readout sınırı.

## CP5 — heater ve thermal matris

30 heater için tekil ve eşzamanlı test yapısı:

- measured `PπL`, insertion loss ve phase-vs-power eğrisi;
- thermal time constant ve tam `30×30` crosstalk matrisi;
- ortalama/maksimum trim, global stabilizasyon ve driver dahil/haric wall-plug;
- mevcut `395/770 mW` zarfı yalnız varsayımdır; measured maksimum `≤800 mW`
  ve residual phase `≤5°` static / `≤2° RMS` dynamic olmalıdır.

## CP6 — bileşim ve durma kuralı

CP0–CP5 ölçümleri hash'li, sürümlü ve reference-plane tanımlı olmadan G5 yeniden
compose edilmez. Herhangi bir ölçüm P5 stress zarfını aşarsa blind koşu yapılmaz;
P6 `NOT_PHYSICALLY_ACCEPTED` olarak kapanır veya geliştirme verisiyle yeni bir
sonraki-faz mimarisi açılır.

## Araştırma hattı bağlantıları

- [PDK seçim kararı](PDK-SELECTION.md)
- [P6 protokolü](P6-PROTOCOL.md)
- [G3-C durumu](G3C-STATUS.md)
- [G3-D durumu](G3D-STATUS.md)
- [G4 durumu](G4-STATUS.md)
- [Proje merkezi](../docs/_source_records/project-hub-note.md)
