# utils/json_storage.py
# Camada única de acesso a arquivos JSON.
# Nenhum outro módulo lê ou escreve arquivos diretamente.

import json
import uuid
from pathlib import Path
from datetime import datetime


def _ensure_file(path: Path) -> None:
    """Cria o arquivo e diretório se não existirem."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("[]", encoding="utf-8")


def load_all(path: Path) -> list[dict]:
    _ensure_file(path)
    return json.loads(path.read_text(encoding="utf-8"))


def save_all(path: Path, records: list[dict]) -> None:
    path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def insert(path: Path, data: dict) -> dict:
    """Insere registro com ID e timestamp automáticos."""
    records = load_all(path)
    data["id"]         = str(uuid.uuid4())
    data["created_at"] = datetime.utcnow().isoformat()
    records.append(data)
    save_all(path, records)
    return data


def find_all_by(path: Path, field: str, value: str) -> list[dict]:
    """Filtra registros por campo/valor."""
    return [r for r in load_all(path) if r.get(field) == value]