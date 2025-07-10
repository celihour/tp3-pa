.PHONY: seeds

seeds:
	@echo "🔄 Cargando semillas de usuarios…"
	python src/seeds.py

.PHONY: migrate migrate-head migrate-down

migrate:
	@echo "🛠 Generando migración…"
	alembic revision --autogenerate -m "$(msg)"

migrate-head:
	@echo "⬆️  Aplicando migraciones…"
	alembic upgrade head

migrate-down:
	@echo "⬇️  Deshaciendo última migración…"
	alembic downgrade -1
