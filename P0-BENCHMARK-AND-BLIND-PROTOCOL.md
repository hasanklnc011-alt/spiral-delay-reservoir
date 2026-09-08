---
title: P0 — NARMA-10 Benchmark ve Kör Test Protokolü
type: project-note
status: active
created: 2026-09-03
---

# P0 — NARMA-10 Benchmark ve Kör Test Protokolü

> Güncel yayın protokolü v2'dir: `configs/p0_narma10_protocol_v2.json`. V1'in
> aynı-feature kayıpsız dijital ikizi `%10` yenme şartı development preflight'ta
> mantıksal olarak geçersiz bulundu; v1 kör suite hiç çalıştırılmadan emekliye ayrıldı.

## Amaç

Fotonik mimari aramasından önce NARMA-10 veri üretimini, split'leri, NMSE hedefini
ve kör yayın testini değişmez bir sözleşmeye bağlamak. Nihai hedef fiziksel olarak
uygulanabilir adayda kör 10-seed medyan test NMSE `<0.05`.

## Kapsam

- NARMA-10 üretiminin deterministik ve sonlu olduğunu doğrulamak.
- Geliştirme ile kör yayın seed'lerini ayırmak ve exact dataset hash'lerini sabitlemek.
- Aday config ve kaynak kod kilitlenmeden kör testi reddetmek.
- Eski seed-83 benchmarkını geçersiz yayın protokolü olarak işaretlemek.

Kapsam dışı: fotonik topoloji seçimi, hiperparametre taraması, fizik modeli ve kör
test skorunun çalıştırılması. Bunlar P1 ve sonrasındadır.

## Kanonik context ve çıktılar

- `configs/p0_narma10_protocol.json` — frozen split, seed, hash ve kapılar.
- `src/photonic_reservoir/protocol.py` — bütünlük ve aday-kilidi doğrulayıcısı.
- `scripts/verify_p0_protocol.py` — yeniden üretilebilir P0 kontrolü.
- `tests/test_protocol.py` ve `tests/test_benchmark.py` — regresyon kanıtı.
- [[🏰 300-Projects/Photonic-Reservoir/MODEL-AND-ACCEPTANCE|Model ve kabul protokolü]].

## Başarı ve kalite eşikleri

- Geliştirme: 10 seed üzerinde medyan validation NMSE `≤0.04`.
- Kör yayın: medyan test NMSE `<0.05` ve seed'lerin en az `8/10`'unda `<0.05`.
- `delayed_input`, aynı-delay dijital ve fotonik çekirdeksiz kontrollere karşı ayrı
  ayrı en az `%10` göreli kazanç.
- Eşleştirilmiş `%95` bootstrap farkının üst sınırı `<0`.
- Input, target, feature, prediction ve metriklerin tamamı sonlu.

## Varsayımlar ve riskler

- Seed numaralarının görünür olması körlüğü bozmaz; seçim sırasında test skoruna
  erişmek bozar. Kod kapısı kazara erişimi engeller, kötü niyetli dosya okumasını değil.
- NARMA rekürsiyonu bazı seed/uzunluklarda patlayabilir. Seed 83 tam yayın
  uzunluğunda bu nedenle reddedildi; clipping ve NaN→sayı dönüşümü yasaktır.
- Daha önce test skoru görülen eski seed'ler yalnız geliştirme verisidir.
- Kör test başarısız olursa aynı suite üzerinde tuning yapılmaz; yeni hipotez yeni
  protokol sürümü ve yeni kör suite gerektirir.

## Bağımlılık grafiği

`P0 benchmark kilidi → P1 ideal hipotez → P2 fiziksel multiplex mimarisi → P3 kayıp/gürültü/tolerans → P4 validation-only optimizasyon → aday kilidi → P5 tek kör test → P6 bileşen/FDTD doğrulaması`

## Üretici ve doğrulayıcı ayrımı

- Üretici P1–P4 sırasında yalnız development train/validation kullanır.
- Doğrulayıcı dataset hash'lerini, aday config/source hash'lerini ve kör-test
  yetkisini kontrol eder.
- Nihai sonuç tek merkezî raporda sentezlenir; test sonucu adaya geri beslenmez.

## Durma koşulları

- Sonlu olmayan herhangi bir değer: ilgili dataset/koşu derhal durur.
- Aday kilidi yoksa: kör değerlendirme çalışmaz.
- İlk kör değerlendirme kapıyı geçmezse: v1 kapanır; aynı kör veride yeniden seçim yoktur.

## P0 doğrulama komutu

`python scripts/verify_p0_protocol.py`

Başarılı çıktı 20 dataset commitment'ının doğrulandığını ve
`blind_test_authorized: false` olduğunu göstermelidir. Bu aşamada `false` doğru sonuçtur.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Photonic Reservoir çalışma merkezi]]
- [[🏰 300-Projects/Photonic-Reservoir/MODEL-AND-ACCEPTANCE|Model ve kabul protokolü]]
- [[🧠 500-Knowledge/concepts/AI-Proje-Baslatma-Protokolu|AI Proje Başlatma Protokolü]]
- [[🧠 500-Knowledge/concepts/Photonic-Research-Lines-Synthesis|Fotonik araştırma hatları sentezi]]
