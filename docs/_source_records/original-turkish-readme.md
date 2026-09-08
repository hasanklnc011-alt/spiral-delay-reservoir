> **The project's original README (Turkish), kept verbatim.** The current English README is at
> the repository root. Obsidian links have been converted to plain text / relative links.

# Photonic Reservoir — NMSE < 0.05 Araştırma Hattı

Bu depo artık yeni NARMA-10 araştırma hattını ve eski üç-ring çalışmasını fiziksel
olarak ayırır. Güncel çalışma yalnız P0 protokolü ile `p1-coherent-delay/` alanını
kullanır. Eski sonuçlar silinmemiştir; `legacy-three-ring/` altında salt-okunur
referans olarak korunur.

## Güncel başlangıç sırası

1. `P0-BENCHMARK-AND-BLIND-PROTOCOL.md`
2. `configs/p0_narma10_protocol.json`
3. `HANDOFF.md`
4. `p1-coherent-delay/README.md`

P1 sırasında yalnız development train/validation kullanılır. Kör yayın suite'i
aday config ve kaynak kod kilitlenene kadar çalıştırılamaz.

## Dizinler

- `src/photonic_reservoir/protocol.py` — ortak P0 bütünlük ve kör-test kapısı.
- `src/photonic_reservoir/p1_coherent_delay/` — yeni model kodunun tek hedefi.
- `p1-coherent-delay/configs/` — yalnız P1 config'leri.
- `p1-coherent-delay/runs/` — yalnız P1 development çıktıları.
- `legacy-three-ring/` — eski config, run, FDTD kanıtı ve belgeler.

Eski `model.py`, `search.py`, `delay_search.py` ve ilişkili testler geçmiş sonuçların
yeniden üretilebilirliği için pakette geçici olarak korunur. Yeni P1 kodu bunları
import etmez.

## Doğrulama

```powershell
$env:PYTHONPATH = "$PWD\src"
python scripts/verify_p0_protocol.py
python -m unittest discover -s tests -v
```

P0 aşamasında doğru sonuç `blind_test_authorized: false` değeridir.

## Araştırma hattı bağlantıları

- [Photonic Reservoir proje merkezi](project-hub-note.md)
- [P0 benchmark ve kör test protokolü](../../P0-BENCHMARK-AND-BLIND-PROTOCOL.md)
- [MRR/RNN literatür taraması](../references/literature_review.md)
- Fotonik araştırma hatları sentezi (MayOS vault note, outside this repository)
