---
title: MRR RNN - Literatür Taraması
type: literature-review
status: active
created: 2026-08-28
tags: [microring, reservoir-computing, rnn, photonics]
---
# MRR RNN - Literatür Taraması

Bu not, micro-ring rezonatörlerle recurrent computation için çekirdek literatürün
fiziksel model, bellek, eğitim ve benchmark açısından karşılaştırmasıdır.

## Ana ayrım

Si mikro-ring çalışmalarındaki TPA, free-carrier ve thermo-optik etkiler SiN/Kerr'e
doğrudan taşınmaz. Bizim SiN hattına aktarılacak olanlar mimari, benchmark ve
modelleme yöntemidir; bellek mekanizması ayrıca tasarlanmalıdır.

## 1. Donati et al. (2024) - fiber feedback ile time-delay RC

Kaynak: [10.1364/OE.514617](https://doi.org/10.1364/OE.514617)

- Add-drop Si MRR, through porttan fiber döngüyle add porta bağlanır.
- Bellek, free-carrier/termal atalet ile 88 ns fiber echo memory'nin birleşimidir.
- Maskeli giriş zaman örnekleri virtual node'lara ayrılır; yalnız lineer readout eğitilir.
- Gecikmeli Boolean görevlerde üç bitlik bellek için feedback gereklidir; Santa Fe ve
  Mackey-Glass'ta MRR nonlinearity kullanılır.
- SiN/Kerr için anlamı: delay-loop, faz kararlılığı ve readout protokolü doğrudan
  kullanılabilir; Si taşıyıcı/termal belleği kullanılamaz.

## 2. Bazzanella et al. (2022) - tek MRR'nin intrinsic memory sınırı

Kaynak: [10.1109/JLT.2022.3183694](https://doi.org/10.1109/JLT.2022.3183694)

- Feedbacksiz tek Si MRR ve time-multiplexed virtual node yaklaşımı kullanılır.
- TPA'nın ürettiği free-carrier dispersion ve thermo-optik etki fading memory ile
  nonlinear dönüşüm sağlar.
- Offline ridge regression uygulanır; AND/OR bellek, XOR ise bellek + nonlinearity
  gereksinimini ayrıştırır.
- Tek ring lineer görevlerde en fazla iki geçmiş bitlik intrinsic memory göstermiştir.
- Zorunlu metodolojik ders: aynı readout giriş sinyaline de uygulanmalıdır; aksi halde
  modülatör/algılayıcı kaynaklı artefaktlar reservoir başarısı gibi görünebilir.

## 3. Giron Castro et al. (2024) - TCMT parametre haritası

Kaynak: [10.1364/OE.509437](https://doi.org/10.1364/OE.509437)

- Maskeli 1-GBd giriş, feedback waveguide ve 50 virtual node içeren Si-MRR TDRC modeli.
- TCMT, cavity alanı `a(t)`, carrier yoğunluğu `ΔN(t)` ve sıcaklık `ΔT(t)` için bağlı
  denklemlerle kurulmuş; 4. derece Runge-Kutta kullanılmıştır.
- NARMA-10'da yalnız ridge-regression readout eğitilir.
- Güç-detuning düzleminde üç bölge bulunur: lineer/yetersiz (A), orta nonlinear ve
  tutarlı iyi çalışma bölgesi (B), self-pulsing/tutarsız bölge (C).
- SiN/Kerr için başlangıç: TCMT + RK4 iskeletini koru; carrier/thermal denklemler yerine
  Kerr detuning'i ekle ve explicit bellek döngüsü tanımla.

## 4. Tait et al. (2017) - gerçek continuous-time RNN

Kaynak: [10.1038/s41598-017-07754-z](https://doi.org/10.1038/s41598-017-07754-z)

- WDM çıkışlar, programlanabilir MRR weight bank'ler, balanced photodetector ve MZM
  nöronlarından oluşan broadcast-and-weight mimarisi kullanılır.
- Model: `ds/dt = (W y - s)/τ + W_in u`, `y = σ(s)`.
- MRR burada nonlinear reservoir düğümü değil, ağırlık matrisi için ayarlanabilir filtredir.
- Cusp ve Hopf bifurcation ile fiziksel devrenin continuous-time RNN'e dinamik
  izomorfizmi gösterilir.
- Bu, ileri aşamada gerçek eğitilebilir RNN yoludur; mevcut Kerr-reservoir baseline'ının
  doğrudan devamı değildir.

## 5. Dong et al. (2026) - üç MRR deep reservoir

Kaynak: [10.1016/j.optlastec.2025.114614](https://doi.org/10.1016/j.optlastec.2025.114614)

- Seri bağlı üç add-drop Si MRR katmanı, gecikmeli waveguide ve katmanlar arası feedback.
- TCMT + TPA/FCA/FCD/TO denklemleri 4. derece Runge-Kutta ile çözülür; tüm drop-port
  durumları tek lineer readout'ta birleşir.
- NARMA-10: single MRR 0.455, iki MRR 0.103, üç MRR 0.071 NMSE.
- Mackey-Glass'ta en iyi sonuç iki MRR ile 0.0011 NMSE; katman sayısı görev bağımlıdır.
- Mevcut üç-ring NARMA-3 sonucumuz için en yakın mimari referanstır.

## 6. Ren et al. (2024) - nonlinear MRR + lineer MRR array

Kaynak: [10.1364/OE.518063](https://doi.org/10.1364/OE.518063)

- Bir nonlinear Si MRR, yüksek-Q lineer MRR dizisiyle birleştirilerek uzun fiber delay
  olmadan bellek kapasitesi artırılır.
- NARMA-10, Mackey-Glass ve Santa Fe üzerinde değerlendirilmiştir; NARMA-10 için
  fiber-feedback'e benzer başarıyı en az 350× daha küçük boyutta raporlar.
- Tam PDF henüz elimizde olmadığı için denklem ve parametre kartı sonraki okumada tamamlanacak.

## Proje kararı

İlk model: **SiN/Kerr TCMT + explicit delay-feedback veya üç-ring bellek + ridge readout**.
NARMA-10 için input-only, delayed-input ve dijital ESN baseline'ları birlikte raporlanacak.
Tait tipi weight-bank CTRNN ikinci aşama mimari seçeneğidir.

## İlişkili notlar

- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Photonic Reservoir çalışması]]
- [[🏰 300-Projects/3 halkalı Ring/Tidy3D-Small-Ring|Tidy3D Small-Ring FDTD]]
- [[🏰 300-Projects/2D FDFD tabanlı, fixed-point ve truncated RNN/2D FDFD tabanlı, fixed-point ve truncated RNN|FDFD Kerr Photonic RNN]]
