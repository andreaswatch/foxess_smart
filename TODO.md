# Open Tasks / TODOs for Home Assistant Integration (foxess_smart)

## Home Assistant Maintenance Tasks
- [ ] **Home Assistant Statistikwerte korrigieren (Energy Dashboard Ausreißer)**:
  - **Grund**: Durch die vorherige 32-Bit Big-Endian Dekodierung (vor v1.0.7) wurden überhöhte Leistungswerte aufgezeichnet.
  - **Schritte zur Behebung**:
    1. In Home Assistant zu **Entwicklerwerkzeuge** -> **Statistik** navigieren.
    2. Entitäten auswählen:
       - `sensor.foxess_h12_pv_production_total`
       - `sensor.foxess_h12_grid_import_energy`
       - `sensor.foxess_h12_grid_export_energy`
       - `sensor.foxess_h12_battery_charge_energy`
       - `sensor.foxess_h12_battery_discharge_energy`
    3. Rechts das Icon **Statistikwert anpassen** (Rampe mit Stift) anklicken.
    4. Den Ausreißer-Wert vom 24. Juli 2026 korrigieren oder auf den vorherigen Stand zurücksetzen und speichern.
