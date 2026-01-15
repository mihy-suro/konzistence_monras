from pathlib import Path
from monras_etl.config import load_config
from monras_etl.sqlite_io import run_import

def main():
    # Automaticky načte config.yaml ze stejného adresáře jako tento skript
    script_dir = Path(__file__).parent
    config_path = script_dir / "config.yaml"
    
    cfg = load_config(config_path)
    run_import(cfg)

if __name__ == "__main__":
    main()
