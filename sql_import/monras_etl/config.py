from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Union
import yaml

@dataclass
class Config:
    raw: Dict[str, Any]
    base_dir: Path  # adresář, kde leží config.yaml (pro resolvování relativních cest)

def load_config(path: Union[str, Path]) -> Config:
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return Config(raw=raw, base_dir=path.parent.resolve())
