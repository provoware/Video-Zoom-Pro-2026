# Status und Wiederaufnahme – 02.11.2026

## Vollzogene Integration
#34 → #35 → #36 → #37 regulär und ohne Force-Push in main übernommen. Keine Freigabeprüfung abgeschwächt.

| Paket | Main-Commit | Erfolgreicher Main-Lauf |
|---|---|---|
| #34 Strategie | d470ea00d239fc1d57031fcd43808d1ae0e6e353 | 41377347113 |
| #35 WAV | 60b24d9806f346f15f3f6bd645cde1cad7fb5589 | 41377490494 |
| #36 Speicher | 8fca030174d4a00bcf2b4dca7e673a8b93494951 | 41377620159 |
| #37 Einrichtung | e544b711794080be5300158dd6608b964c5b9bea | 41377743071 |

Alle 63 versionierten lokalen Dateien nach #37 mit dem integrierten Git-Baum abgeglichen: null Abweichungen. Gemeinsamer integrierter Umfang: 136 Python-/Medientests, zehn Chromium-Verträge, 20 Layoutfälle. Diese Nachweise gehören zu diesem Stand, nicht zu zukünftigen Änderungen.

## Aktuelles Bedienungspaket
Branch `feat/safe-settings-after-37`, Basis-main `e544b711794080be5300158dd6608b964c5b9bea`. UX-01b und UX-03: gewählte Bedienwerte mit exakter alter Dateisicherung, Fingerabdruck und gruppenweiser Rücknahme nach Neustart; Farbschema während eines laufenden Auftrags speichern, ohne dessen Medienkonfiguration zu ändern.

Prognose: Fehlbedienung sicher rücknehmbar und Farbwahl ohne Produktionsstopp möglich. Gemessen: neun gezielte Pythonfälle inklusive echter HTTP-/Zugriffsschutzprüfung und zwölf ausgeführte JavaScript-Verträge als lokale Vorprüfung. Endgültige Gesamt-/Chromium-CI des neuen Commit separat im PR auswerten, nicht vorwegnehmen. Kein Eingriff in Quellmedien, keine neue Produktruntime.

## Nächste offene Schritte
`docs/TODO.md` ist führend. Nach diesem Paket verbleiben UX-04 (Kontrast/Tab/Pixel), UX-05 (zweite Oberfläche), die dokumentierten Architektur-/Sicherheitsbewertungen und QA-FINAL. Rechteentscheidung, eingefrorener Kandidat und reale Kubuntu-Endabnahme bleiben separat OFFEN; Kubuntu zuletzt. Kein Stable-Release.
