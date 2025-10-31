#!/usr/bin/env python3
"""
filemover.py - Script per organizzare i file in base al loro tipo/estensione.
Compatibile con Windows e Linux.
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict
import sys
from datetime import datetime
import logging

# Mappatura estensioni -> categorie
FILE_CATEGORIES = {
    'Immagini': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff', '.tif'],
    'Video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.mpg'],
    'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.opus'],
    'Documenti': ['.pdf', '.doc', '.docx', '.txt', '.odt', '.rtf', '.tex', '.wpd'],
    'Fogli_di_calcolo': ['.xlsx', '.xls', '.csv', '.ods', '.xlsm'],
    'Presentazioni': ['.ppt', '.pptx', '.odp', '.key'],
    'Archivi': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'],
    'Codice': ['.py', '.js', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go', '.rs', '.swift'],
    'Web': ['.html', '.htm', '.css', '.scss', '.sass', '.less', '.xml', '.json', '.yaml', '.yml'],
    'Eseguibili': ['.exe', '.msi', '.app', '.deb', '.rpm', '.dmg', '.apk'],
    'Database': ['.db', '.sqlite', '.sql', '.mdb', '.accdb'],
    'Font': ['.ttf', '.otf', '.woff', '.woff2', '.eot'],
}

def setup_logging():
    """Configura il sistema di logging."""
    # Ottieni la directory dello script
    script_dir = Path(__file__).parent.resolve()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = script_dir / f"{timestamp}_filemover.log"
    
    # Configura logging su file e console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return log_file

def sanitize_folder_name(name):
    """Sanitizza il nome della cartella per evitare problemi filesystem."""
    # Rimuovi caratteri problematici per Windows/Linux
    invalid_chars = '<>:"|?*\\/'
    for char in invalid_chars:
        name = name.replace(char, '_')
    
    # Rimuovi spazi iniziali/finali
    name = name.strip()
    
    # Se il nome è vuoto dopo la pulizia, usa un fallback
    if not name:
        return "Senza_nome"
    
    # Evita nomi riservati di Windows
    reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 
                     'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 
                     'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    if name.upper() in reserved_names:
        name = f"{name}_file"
    
    return name

def get_category(file_path):
    """Determina la categoria del file in base all'estensione."""
    ext = file_path.suffix.lower().strip()
    
    # Gestisci estensioni vuote o solo punto
    if not ext or ext == '.':
        return "Senza_estensione"
    
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    
    # Se non trova una categoria, usa "Altri" + estensione sanitizzata
    clean_ext = ext[1:] if ext.startswith('.') else ext  # Rimuove il punto
    clean_ext = sanitize_folder_name(clean_ext)
    
    if not clean_ext:
        return "Senza_estensione"
    
    return f"Altri_{clean_ext}"

def scan_files(root_path):
    """Scansiona tutte le sottocartelle e cataloga i file."""
    root = Path(root_path)
    files_by_category = defaultdict(list)
    
    logging.info(f"Inizio scansione da: {root.absolute()}")
    print(f"[SCAN] Scansione in corso da: {root.absolute()}")
    print("-" * 60)
    
    file_count = 0
    for item in root.rglob('*'):
        if item.is_file():
            category = get_category(item)
            files_by_category[category].append(item)
            file_count += 1
    
    logging.info(f"Scansione completata: {file_count} file trovati in {len(files_by_category)} categorie")
    return files_by_category

def show_summary(files_by_category):
    """Mostra il riepilogo dei file trovati."""
    total_files = sum(len(files) for files in files_by_category.values())
    print(f"\n[INFO] Trovati {total_files} file in {len(files_by_category)} categorie:")
    for category, files in sorted(files_by_category.items()):
        print(f"  - {category}: {len(files)} file")
        logging.info(f"Categoria '{category}': {len(files)} file")

def get_user_confirmation():
    """Chiede conferma all'utente prima di procedere."""
    print("\n" + "=" * 60)
    response = input("Vuoi procedere con l'organizzazione? (si/no): ").strip().lower()
    return response in ['si', 's', 'sì', 'y', 'yes']

def get_unique_filename(category_dir, original_name):
    """Genera un nome file unico se esiste già un file con lo stesso nome."""
    dest_file = category_dir / original_name
    if not dest_file.exists():
        return dest_file
    
    # Gestisci file con stesso nome
    file_path = Path(original_name)
    stem = file_path.stem
    suffix = file_path.suffix
    counter = 1
    
    while dest_file.exists():
        dest_file = category_dir / f"{stem}_{counter}{suffix}"
        counter += 1
    
    return dest_file

def copy_files_to_categories(root, files_by_category):
    """Copia i file nelle cartelle appropriate."""
    print("\n[COPY] Creazione cartelle e copia file...")
    original_dirs = set()
    files_copied = 0
    files_failed = 0
    
    for category, files in files_by_category.items():
        category_dir = root / category
        category_dir.mkdir(exist_ok=True)
        logging.info(f"Cartella creata/verificata: {category}/")
        
        for file_path in files:
            # Salva la directory originale per eliminarla dopo
            original_dirs.add(file_path.parent)
            
            # Gestisci file con stesso nome
            dest_file = get_unique_filename(category_dir, file_path.name)
            
            try:
                shutil.copy2(file_path, dest_file)
                files_copied += 1
                print(f"  [OK] Copiato: {file_path.name} -> {category}/")
                logging.info(f"File copiato: {file_path} → {dest_file}")
            except Exception as e:
                files_failed += 1
                print(f"  [ERR] Errore copiando {file_path.name}: {e}")
                logging.error(f"Errore durante copia di {file_path}: {e}")
    
    logging.info(f"Copia completata: {files_copied} successi, {files_failed} errori")
    return original_dirs, files_copied, files_failed

def cleanup_original_directories(root, original_dirs, files_by_category):
    """Elimina le cartelle originali dopo aver copiato i file."""
    print("\n[DELETE] Eliminazione cartelle originali...")
    dirs_deleted = 0
    dirs_failed = 0
    
    # Filtra le directory da eliminare in modo più sicuro
    dirs_to_delete = []
    for dir_path in original_dirs:
        # Condizioni più rigorose per l'eliminazione
        is_subdirectory_of_root = dir_path != root and root in dir_path.parents
        is_not_new_category = dir_path.name not in files_by_category
        
        if is_subdirectory_of_root and is_not_new_category:
            dirs_to_delete.append(dir_path)
    
    for dir_path in dirs_to_delete:
        try:
            # Verifica che la directory sia vuota prima di eliminarla
            if dir_path.exists() and not any(dir_path.iterdir()):
                shutil.rmtree(dir_path)
                dirs_deleted += 1
                print(f"  [OK] Eliminata: {dir_path.name}/")
                logging.info(f"Cartella eliminata: {dir_path}")
            else:
                logging.warning(f"Cartella non vuota, saltata: {dir_path}")
        except Exception as e:
            dirs_failed += 1
            print(f"  [ERR] Errore eliminando {dir_path.name}: {e}")
            logging.error(f"Errore durante eliminazione di {dir_path}: {e}")
    
    logging.info(f"Eliminazione completata: {dirs_deleted} cartelle eliminate, {dirs_failed} errori")
    return dirs_deleted, dirs_failed

def organize_files(root_path, dry_run=False):
    """Organizza i file copiandoli in cartelle per categoria."""
    root = Path(root_path)
    files_by_category = scan_files(root)
    
    if not files_by_category:
        logging.warning("Nessun file trovato!")
        print("[ERROR] Nessun file trovato!")
        return
    
    # Mostra riepilogo
    show_summary(files_by_category)
    
    if dry_run:
        logging.info("MODALITÀ TEST ATTIVA - Nessuna modifica effettuata")
        print("\n[TEST] MODALITÀ TEST - Nessuna modifica verrà effettuata")
        return
    
    # Chiedi conferma
    if not get_user_confirmation():
        logging.info("Operazione annullata dall'utente")
        print("[CANCEL] Operazione annullata.")
        return
    
    logging.info("Inizio organizzazione file")
    
    # Copia file nelle categorie
    original_dirs, files_copied, _ = copy_files_to_categories(root, files_by_category)
    
    # Elimina le cartelle originali
    dirs_deleted, _ = cleanup_original_directories(root, original_dirs, files_by_category)
    
    logging.info(f"OPERAZIONE COMPLETATA - File copiati: {files_copied}, Cartelle eliminate: {dirs_deleted}")
    print("\n[SUCCESS] Organizzazione completata!")

def print_header():
    """Stampa l'header del programma."""
    print("=" * 60)
    print("  FILEMOVER - ORGANIZZATORE FILE PER TIPO")
    print("=" * 60)

def parse_command_line_args():
    """Analizza gli argomenti da riga di comando e restituisce modalità test e path."""
    test_mode = '-t' in sys.argv or '--test' in sys.argv or '--dry-run' in sys.argv
    
    # Cerca un path tra gli argomenti
    root_path = None
    for arg in sys.argv[1:]:
        if not arg.startswith('-'):
            root_path = arg
            break
    
    return test_mode, root_path

def get_root_path(test_mode, initial_path):
    """Determina il path della cartella root da utilizzare."""
    if initial_path:
        return initial_path
    
    # Se siamo in modalità automatica (CI/CD) usa la directory corrente
    if test_mode or not sys.stdin.isatty():
        print(f"\n[AUTO] Usando directory corrente: {Path('.').resolve()}")
        return "."
    else:
        root_path = input("\nInserisci il percorso della cartella root (Enter per cartella corrente): ").strip()
        return root_path if root_path else "."

def validate_root_path(root_path):
    """Valida che il path sia esistente e sia una directory."""
    root = Path(root_path).resolve()
    
    if not root.exists():
        print(f"[ERROR] Il percorso '{root}' non esiste!")
        sys.exit(1)
    
    if not root.is_dir():
        print(f"[ERROR] '{root}' non è una cartella!")
        sys.exit(1)
    
    return root

def setup_logging_and_info(root_path, test_mode):
    """Configura il logging e stampa le informazioni iniziali."""
    log_file = setup_logging()
    logging.info("="*60)
    logging.info("FILEMOVER - Avvio script")
    logging.info(f"Cartella root: {root_path}")
    logging.info(f"File di log: {log_file}")
    logging.info("="*60)
    
    print(f"\n[LOG] File di log: {log_file}")
    
    if test_mode:
        logging.info("Modalità test attivata")
    
    return log_file

def run_organization(root_path, test_mode):
    """Esegue l'organizzazione dei file con gestione errori."""
    try:
        organize_files(root_path, dry_run=test_mode)
        logging.info("Script terminato con successo")
    except KeyboardInterrupt:
        logging.warning("Operazione interrotta dall'utente (Ctrl+C)")
        print("\n\n[INTERRUPT] Operazione interrotta dall'utente.")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Errore fatale: {e}", exc_info=True)
        print(f"\n[ERROR] Errore: {e}")
        sys.exit(1)

def main():
    """Funzione principale."""
    print_header()
    
    # Analizza argomenti da riga di comando
    test_mode, initial_path = parse_command_line_args()
    
    # Determina la cartella root
    root_path = get_root_path(test_mode, initial_path)
    
    # Valida il path
    validated_root = validate_root_path(root_path)
    
    # Setup logging e informazioni
    setup_logging_and_info(validated_root, test_mode)
    
    # Esegue l'organizzazione
    run_organization(validated_root, test_mode)

if __name__ == "__main__":
    main()