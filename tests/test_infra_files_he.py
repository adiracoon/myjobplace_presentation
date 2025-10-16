import os, re
ROOT = os.path.dirname(os.path.dirname(__file__))
def test_infrastructure_files_exist():
    assert os.path.isfile(os.path.join(ROOT, "alembic", "env.py")), "alembic/env.py missing"
    assert os.path.isfile(os.path.join(ROOT, "Dockerfile")), "Dockerfile missing"
    assert os.path.isfile(os.path.join(ROOT, "docker-compose.yml")), "docker-compose.yml missing"
    assert os.path.isfile(os.path.join(ROOT, "API_CONTRACT.md")), "API_CONTRACT.md missing"
    assert os.path.isfile(os.path.join(ROOT, "Makefile")), "Makefile missing"
def test_makefile_contains_important_targets():
    mk = open(os.path.join(ROOT, "Makefile"), encoding="utf-8").read()
    assert re.search(r"\btest:", mk), "Makefile is missing the 'test' target"
    assert re.search(r"\brun:", mk), "run target missing in Makefile"
def test_env_example_including_DATABASE_URL():
    env = os.path.join(ROOT, ".env.example")
    assert os.path.isfile(env), ".env.example missing"
    txt = open(env, encoding="utf-8").read()
    assert "DATABASE_URL=" in txt, "DATABASE_URL must be defined in .env.example"
