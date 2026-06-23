import os
import glob
from PIL import Image

class AssetsManager:
    """
    Gestor de Ativos [ORION-WHITEBOARD]
    Responsável pela integridade, cache e links de documentação.
    """
    def __init__(self, assets_dir="assets/imagens"):
        self.assets_dir = assets_dir
        os.makedirs(self.assets_dir, exist_ok=True)
        self.cache = {}

    def get_asset_info(self, asset_id):
        """Retorna metadados do asset para o Obsidian."""
        path = os.path.join(self.assets_dir, f"{asset_id}.png")
        if os.path.exists(path):
            img = Image.open(path)
            return {
                "id": asset_id,
                "path": path,
                "size": img.size,
                "format": img.format,
                "obsidian_link": f"![[{asset_id}.png]]"
            }
        return None

    def list_all(self):
        """Lista todos os ativos disponíveis."""
        files = glob.glob(os.path.join(self.assets_dir, "*.png"))
        return [os.path.splitext(os.path.basename(f))[0] for f in files]

if __name__ == "__main__":
    am = AssetsManager()
    print(f"📦 Ativos detectados: {am.list_all()}")
