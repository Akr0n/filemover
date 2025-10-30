# FileMover

Script Python per organizzare automaticamente i file in base al tipo/estensione.

## Caratteristiche

- 🔍 Scansione ricorsiva di tutte le sottocartelle
- 📁 Organizzazione automatica in categorie (Immagini, Video, Audio, Documenti, ecc.)
- 🪟 Multipiattaforma (Windows e Linux)
- 📝 Logging dettagliato di tutte le operazioni
- 🧪 Modalità test per preview senza modifiche
- 🗑️ Pulizia automatica delle cartelle originali

## Utilizzo

```bash
# Esecuzione interattiva
python filemover.py

# Con percorso specificato
python filemover.py /percorso/della/cartella

# Modalità test (solo preview)
python filemover.py /percorso/della/cartella -t
```

## Requisiti

- Python 3.6+
- Nessuna dipendenza esterna (usa solo librerie standard)

## Log

I log vengono salvati nella stessa directory dello script con formato: `YYYYMMDD_HHMMSS_filemover.log`
