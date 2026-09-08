# G1 Kesit Kabulü

## Karar

G1, **343×180 nm silicon strip / SiO₂** kesit için koşullu olarak geçti. Bu karar
yalnız P6 bileşen doğrulamasına ilerleme yetkisidir; foundry-qualified PDK veya
tape-out kabulü değildir.

- Fine mesh, 1550 nm: `n_eff=1.871075`, `n_g=4.012965`, TE fraction `0.94596`.
- 14.240141755 cm gecikme: `1.90616 ns = 19.0616` sembol; hata `%0.324`.
- Medium→fine: `Δn_g/n_g=%0.177`, `|Δn_eff|=4.90e-5`; yakınsama geçti.
- Tek guided TE-like mod; ikinci guided çözüm TM-like'dır.
- Genişlik `343±10 nm` ve kalınlık `180±5 nm` köşeleri 1550 nm'de geçti.
- Kalınlık `180±10 nm` **geçmedi** ve kabul edilen proses penceresi değildir.
- Nominal 5-nm örneklemde `n_g=4±%2` penceresi `1530–1575 nm`; sistem taşıyıcısı
  1550 nm'de kalır.

Toplam remote G1 harcaması: ilk seed `0.0107155 FC`, dört aday `0.0170092 FC`,
seçilmiş convergence/corner suite `0.0737444 FC`, kalınlık refinement
`0.0208476 FC`; toplam `0.1223167 FC`.

## Durma ve ilerleme kuralı

G3 bileşen modelleri yalnız `configs/g1-accepted-v1.json` kesitini kullanır.
Bir foundry/PDK seçimi `180±5 nm` kalınlık şartını karşılamazsa G1 yeniden açılır;
P5 kör sonucu hiçbir durumda yeniden çalıştırılmaz veya tuning hedefi yapılmaz.

## Araştırma hattı bağlantıları

- [P6 protokolü](P6-PROTOCOL.md)
- [EM/FDTD planı](EM-FDTD-PLAN.md)
- [P6 durum](STATUS.md)
- [Proje merkezi](../docs/_source_records/project-hub-note.md)
