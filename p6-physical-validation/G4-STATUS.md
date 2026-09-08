# G4 Faz, PD ve Termal Compact-Model Durumu

## Karar

10 PD × 3 slot routing ve kontrol katmanlarının fiziksel semantiği geçti:
`30 GHz` slot seçimi hızlı EO/switch katmanına aittir; `10 kHz` varsayılan
thermo-optic kontrol yalnızca statik trim, drift ve fabrication offset içindir.
Thermal bant/slot oranı `3.33e-7` olduğundan heater'ı slot anahtarı gibi
kullanmak yasaktır.

Fiziksel G4 kabulü henüz verilmedi (`g4_physical_accepted=false`):

- Maksimum koherent diferansiyel gecikme `1.4 ns`; `2° RMS` bütçenin tamamı
  lazere ayrılsa linewidth üst zarfı `138.5 kHz`. Pilot/feedback ve termal gürültü
  payları henüz ayrılmadı.
- P5 uyumlu receiver kapısı `50 GHz`, `0.8 A/W`, `20 pA/√Hz`. İdeal
  combiner'da `5 mW` LO ve `1.25 mW` tepe sinyal için gereken lineer tepe
  photocurrent en az `4.5 mA`; PD/TIA saturation ve swing PDK/ölçüm bekliyor.
- 30 trim, `20 mW` varsayımsal `Pπ`, `%25` crosstalk marjı ve `20 mW`
  global stabilizasyon ile ortalama `395 mW`, maksimum `770 mW` elde edildi.
  `800 mW` zarfında yalnızca `30 mW` varsayımsal pay kalıyor; bu kabul kanıtı
  değil, thermal solve/measurement gerektiriyor.

Açık fiziksel girdiler: hızlı switch S-parametresi/bandwidth, phase-shifter
`PπL` ve optik kayıp, thermal time constant/crosstalk matrisi, laser shared-noise
bütçesi ve 50 GHz PD/TIA lineerlik verisi.

Birincil foundry kaynak taraması `PDK-SELECTION.md` içinde fail-closed kaydedildi.
İşlevsel olarak uygun 50G sınıfı hazır platformların yayımlanmış katmanları
`220 nm` Si kullanıyor ve G1'in `180±5 nm` koşulunu karşılamıyor. AIM'in nicel
katman/aygıt verileri ise lisanslı PDK erişimi gerektiriyor. Bu nedenle G4,
platform seçimi yapılmadan kamuya açık metriklerle kapatılmayacak.

Hasan custom-process yolunu seçti; `343×180 nm` kesit korunacak. G4 bundan sonra
hazır 220 nm PDK hücreleriyle değil, `CUSTOM-PROCESS-VALIDATION.md` içindeki
30 GHz switch, birlikte ölçülmüş 50 GHz PD/TIA ve 30-heater thermal test
sözleşmesiyle kapanabilir. Bu seçim mevcut `g4_physical_accepted=false` hükmünü
değiştirmez.

P5 kör sonucu yeniden çalıştırılmadı ve bu bütçelerin hiçbirinde tuning
hedefi olarak kullanılmadı.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/P6-PROTOCOL|P6 protokolü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/COMPONENT-MODEL|Bileşen modeli]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G3C-STATUS|G3-C splitter durumu]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/PDK-SELECTION|PDK seçim kapısı]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/CUSTOM-PROCESS-VALIDATION|Custom-process doğrulama planı]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/STATUS|P6 durum]]
- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Proje merkezi]]
