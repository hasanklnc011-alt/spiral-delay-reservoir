# P6 Bileşen Modeli

## 1. Delay ve grup indisi

Maksimum bellek gecikmesi

`T_delay = (N_lag - 1) / R_sym = 19 / 10 GHz = 1.9 ns`

ve gerekli fiziksel uzunluk

`L = c T_delay / n_g`.

P5'in `n_g=4` varsayımı `L=14.240141755 cm` verir. Eski 800×400 nm SiN
referansındaki `n_g=2.1073186`, aynı gecikme için yaklaşık 27 cm ister. Bu
nedenle `n_g` bir config etiketi değil ilk EM kabul kapısıdır.

## 2. Double-spiral floorplan zarfı

Model, iki iç içe Archimedean kol ve merkez turnaround için sayısal centerline
uzunluğu kullanır. Pitch ve minimum yarıçap DRC/foundry değeri gelene kadar
yalnızca floorplan tahminidir. Raporlananlar:

- dış yarıçap ve kare keepout alanı,
- kol başına tur sayısı,
- toplam bend açısı ve eşdeğer 90° bend sayısı,
- bend loss varsayımının toplam katkısı.

Bu analitik zarf GDS route-length/DRC kapısının yerine geçmez.

Baseline network tek seri progressive-tap bus'tır. Lossless eş-tap gücü için
`k` sıfırdan başlarken `κ_k=1/(20-k)` kullanılır; gerçek propagation ve coupler
excess loss ile bu oranlar fiziksel power-balance solve'da güncellenir. `1×20` fanout
sonrası bağımsız gecikme kolları baseline değildir; toplam waveguide'i yaklaşık
`1.424 m` yapar.

## 3. Optik kayıp

Bir sinyal yolunun güç kaybı ayrı terimlerle yazılır:

`IL_path = α_prop L + IL_bend + IL_switch + IL_combiner + IL_splitter,excess + IL_misc`.

`10 log10(N)` ideal fanout/bölünme terimi excess loss değildir ve ayrı raporlanır.
P3/P5, propagation, switch ve combiner terimlerini içerdi; bend ve splitter/tap
dağıtımını ayrı bileşen olarak içermedi. P6 bunları geriye dönük olarak P5
kaybına gömmez.

Propagation loss, ideal lossless FDTD'den çıkarılamaz. FDTD bend radiation,
transition, splitter ve combiner excess loss'u verir; uzun-düz waveguide `α_prop`
için PDK veya cut-back ölçümü gerekir.

## 4. 10 coherent combiner / PD kolu

30 kanal, sıradaki her 10 etiket bir slot olacak şekilde dondurulur. Her kanal
`self:i`, `lo:i` veya `pair:i,j`'dir:

- `self:i`: tek sinyal kolu, ikinci giriş karanlık.
- `lo:i`: `E_i + E_LO exp(jφ)`.
- `pair:i,j`: `E_i + E_j exp(jφ)`.

Kilitli fiziksel routing:

| PD | Slot 0 | Slot 1 | Slot 2 |
|---:|---|---|---|
| 0 | `pair:0,9` | `lo:10` | `pair:8,17` |
| 1 | `pair:1,10` | `self:2` | `pair:9,18` |
| 2 | `self:9` | `self:12` | `self:14` |
| 3 | `self:0` | `lo:11` | `self:3` |
| 4 | `pair:2,11` | `pair:10,19` | `lo:13` |
| 5 | `self:10` | `pair:5,14` | `self:15` |
| 6 | `self:1` | `lo:12` | `self:17` |
| 7 | `pair:3,12` | `pair:6,15` | `self:16` |
| 8 | `self:11` | `self:13` | `lo:14` |
| 9 | `pair:4,13` | `pair:7,16` | `self:18` |

Enerji-korunumlu ideal 3-dB combiner tek çıkışı
`E_out=(E_1+exp(jφ)E_2)/√2`'dir. Genel S-matris için `S†S≤I` ve
`P_out,total≤P_in,total` zorunludur. P3'teki doğrudan alan toplamında bu
`1/√2` normalizasyonu açık değildir; P6 bunu geriye dönük gizlice düzeltmez,
model-kapsam açığı olarak kapatır.

PD akımı `I = R |E_out|²` ve receiver modeli sistem için `BW ≥ 15 GHz`,
P5'in 50 GHz detector varsayımını birebir eşlemek için `BW ≥ 50 GHz`,
`R ≥ 0.8 A/W`, `i_n ≤ 20 pA/√Hz` kapılarını taşır.
Saturation/dark-current/capacitance P5'te yoktur ve P6'da açık alan olarak kalır.
5 mW LO, combiner öncesi `4 mA`; ideal 3-dB tek çıkışta yaklaşık `2 mA`
DC photocurrent demektir. TIA dinamik aralığı bu nedenle hard gate'tir.

## 5. Optik güç semantiği

P5 `signal_power_mw=5` değerini `u=1` alanı için kol ölçeği olarak kullanır;
NARMA girdisi `u∈[0,0.5]` olduğundan tek sinyal kolunun tepe gücü `1.25 mW`'tır.
LO kolu `5 mW`'tır. Model hem `u=1` normalize bütçeyi hem gerçek input-bound
bütçeyi slot bazında sayar.

Tek bir lazer ve fanout ağacı kullanılacaksa, gerekli launch power ideal bölünme,
excess loss, her delay yolu ve slot fanout çakışmalarıyla yeniden kurulmalıdır.
Bu eşleme kapanmadan `100 mW` lazer ihtiyacı diye yorumlanamaz.

Aynı slotta bazı tap'ler iki PD'ye gider; maksimum multicast fanout `2`'dir.
Bu ya ideal `3.0103 dB` bölünme ve excess loss ya da iki kat tap gücü gerektirir.

## 6. Faz ve termal bütçe

Slot hızı `30 GHz`'dir. Thermo-optic heater'lar bu hızda kanal fazı
değiştiremez. Seçilen fiziksel yorum:

- 30 kanal yolunda yavaş/statik trim (bir preset/channel),
- 10 receiver'da 3-slot seçimi için ayrı hızlı EO/switch katmanı,
- heater'ların yalnızca drift ve fabrication offset düzeltmesi.

Kilitli channel setinde en büyük koherent diferansiyel gecikme `lo:14` için
`1.4 ns`'dir. Lorentzian laser modeli `Var(Δφ)=2πΔνΔτ` ile, `2° RMS`
bütçenin tamamı lazere ayrılırsa yaklaşık `138 kHz` linewidth sınırı verir.
Bu bir ilk zarf hesabıdır; pilot/feedback ve thermal noise payları eklenince sıkılaşır.

Ortalama heater bütçesi

`P_avg = N_trim P_pi f_phase margin + P_global`

ile raporlanır. Baseline'daki `P_pi`, `f_phase` ve crosstalk margin yalnızca
tasarım zarfıdır; PDK/thermal solve/measurement ile değiştirilmelidir. Kontrol
elektroniği ve TEC ayrı kalemdir.

## Araştırma hattı bağlantıları

- [P6 protokolü](P6-PROTOCOL.md)
- [P5 dondurulmuş sonuç](../p5-publication/RESULTS.md)
- [P4 adayı](../p4-optimization/RESULTS.md)
- [Proje merkezi](../docs/_source_records/project-hub-note.md)
