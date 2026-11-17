# SpecForge — кузница спецификаций

## Установка
pip install -r requirements.txt

## Команды
python main.py parse examples/techvault.spec
python main.py visualize examples/techvault.spec
python main.py trace examples/requirements.json examples/tests.json
python main.py impact examples/cr.json examples/requirements.json examples/tests.json
python main.py run examples/techvault.spec examples/tests.json --seed 42
python main.py initdb

## Тесты
pytest tests/ -v
