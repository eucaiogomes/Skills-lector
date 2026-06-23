import os
import json
from datetime import datetime

class OrionBrain:
    """
    Supercérebro de IA - Orion Whiteboard
    Utilitário para integração automática com Obsidian Vault.
    """
    def __init__(self, vault_path="ORION_BRAIN"):
        self.vault_path = vault_path
        os.makedirs(self.vault_path, exist_ok=True)
        
    def log_decision(self, title, decision, json_data, python_code, rationale, related_links):
        """
        Gera uma nota Markdown formatada para o Obsidian.
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}_{title.replace(' ', '_').lower()}.md"
        filepath = os.path.join(self.vault_path, filename)
        
        tags_str = "orion-whiteboard, decisao-tecnica, " + date_str
        
        content = f"""---
tags: [{tags_str}]
---
# {title}

## Decisão Chave / Objetivo
{decision}

## Estrutura de Dados / JSON Gerado
```json
{json.dumps(json_data, indent=4) if isinstance(json_data, dict) else json_data}
```

## Código / Função da Engine Desenvolvida
```python
{python_code}
```

## Racional e Justificativa Técnica
{rationale}

## Conceitos Relacionados e Links Internos
{related_links}

---
*Gerado por [ORION-WHITEBOARD]*
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

if __name__ == "__main__":
    brain = OrionBrain()
    print("🧠 Orion Brain Logger Inicializado.")
