# G5 Tam-Link Bileşim Durumu

## Karar

Kabul edilmiş G1/G2/G3-A/G3-B kanıtları tek fail-closed bileşim kaydına
bağlandı. Exact `14.240061 cm` GDS rotası `372.91` eşdeğer 90° bend taşıyor.
Fine FDTD `0.003718 dB/90°` değeriyle compose edilen bend kaybı `1.386 dB`.

Varsayımsal `0.8 dB/cm` propagation girdisi eklenince delay hattı `12.778 dB`,
yani `0.8974 dB/cm`; P5'in `1 dB/cm` stress zarfı içinde. Ancak propagation
değeri PDK/cutback kanıtı olmadığı için bu yalnızca koşullu zarf, fiziksel PASS
değil.

Progressive-tap/LO-tree excess ve oranları (G3-C), coherent combiner excess
(G3-D), hızlı switch insertion ve PD/thermal fiziksel girdileri henüz compose
edilemiyor. Bu nedenle `g5_composition_complete=false` ve `p6_accepted=false`.
P5 kör sonucu yeniden çalıştırılmadı.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/P6-PROTOCOL|P6 protokolü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G2-LAYOUT-ACCEPTANCE|G2 layout kabulü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G3B-ACCEPTANCE|G3-B bend kabulü]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G3C-STATUS|G3-C splitter durumu]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/G4-STATUS|G4 compact-model durumu]]
- [[🏰 300-Projects/Photonic-Reservoir/p6-physical-validation/STATUS|P6 durum]]
- [[🏰 300-Projects/Photonic-Reservoir/Photonic-Reservoir|Proje merkezi]]
