"""Helper comum aos data loaders Python do Observable Framework: localiza a
raiz do repositório (onde vivem dados_*.py e etl/) e a adiciona ao sys.path,
para os loaders importarem exatamente a mesma lógica usada pelo site
estático em site_estatico/, sem duplicar nenhuma regra de negócio.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
