# TODO (Cursor): Проверить бэкенд моделей внимательно и без зависаний

Назначение
- Подтвердить, что create_model и update_model работают атомарно (одна транзакция, staged flush) и не зависают.
- Проверить коды ошибок и структуру тела ответа (409/422/400) и что в логах видно этапы.

Важно (прочитай перед стартом)
- Ничего в коде не менять. Только запуск и запросы.
- Все сетевые вызовы с таймаутами (`--max-time`). Если таймаут — фиксируй и переходи дальше.
- Сервер запускать в фоне, собирать PID, все выводы писать в `diagnostics/post_model.log` и `backend/logs/observer.log`.

Пути и логи
- Рабочая папка: `/Users/four/Documents/krai/kr2/forDesktop/krai_desktop`
- Основной лог диагностики: `diagnostics/post_model.log`
- Лог сервера: `backend/logs/observer.log`
- PID сервера: `backend/logs/uvicorn.pid`

Шаги
1) Подготовка окружения и логов
```
cd /Users/four/Documents/krai/kr2/forDesktop/krai_desktop && mkdir -p backend/logs diagnostics && : > backend/logs/observer.log && : > diagnostics/post_model.log
```

2) Освободить порт и запустить сервер в фоне (без reload — надёжнее)
```
kill $(lsof -t -i :8001) 2>/dev/null || true
./venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8001 </dev/null > backend/logs/observer.log 2>&1 & echo $! > backend/logs/uvicorn.pid
```

3) Дождаться готовности (до 15 сек)
```
sleep 3; rg -n "Application startup complete" backend/logs/observer.log || (sleep 12; rg -n "Application startup complete" backend/logs/observer.log)
```

4) Базовые проверки API
```
echo "===== $(date '+%Y-%m-%d %H:%M:%S') RUN =====" | tee -a diagnostics/post_model.log
curl --max-time 5  http://localhost:8001/health        2>&1 | tee -a diagnostics/post_model.log
curl --max-time 10 http://localhost:8001/api/v1/models/ 2>&1 | tee -a diagnostics/post_model.log
```

5) Создание минимальной модели (ожидаем 201)
```
curl -v --max-time 20 -X POST http://localhost:8001/api/v1/models/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Quick Base","article":"QB-0001"}' \
  2>&1 | tee -a diagnostics/post_model.log
```

6) Обновление модели с небольшим BOM (ожидаем 200)
```
MID=$(curl -s --max-time 5 http://localhost:8001/api/v1/models/ | sed -n 's/.*"id":"\([^"]*\)".*/\1/p' | head -n1)
curl -v --max-time 35 -X PUT http://localhost:8001/api/v1/models/$MID \
  -H "Content-Type: application/json" \
  -d '{"name":"Quick Base","article":"QB-0001","isActive":true,"sizeMin":36,"sizeMax":45,"superBom":{"perforationOptions":[{"name":"Без перфорации","isDefault":true,"isActive":true}],"insoleOptions":[{"name":"Стелька стандарт","isDefault":true,"isActive":true}],"hardwareSets":[{"name":"Базовый набор","isDefault":true,"isActive":true,"items":[]}]},"cuttingParts":[],"soleOptions":[]}' \
  2>&1 | tee -a diagnostics/post_model.log
```

7) Конфликт артикула (ожидаем 409 и detail.code = CONFLICT)
```
curl -s -o /dev/null -w "HTTP:%{http_code}\n" --max-time 10 -X POST http://localhost:8001/api/v1/models/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Dup","article":"QB-0001"}' | tee -a diagnostics/post_model.log
```

8) Некорректные ссылки (FK) при обновлении (ожидаем 409)
```
BAD=$(uuidgen)
curl -v --max-time 20 -X PUT http://localhost:8001/api/v1/models/$MID \
  -H "Content-Type: application/json" \
  -d '{"name":"Quick Base","article":"QB-0001","superBom":{},"cuttingParts":[{"material":{"id":"'"$BAD"'"},"quantity":1}],"soleOptions":[]}' \
  2>&1 | tee -a diagnostics/post_model.log
```

9) Зафиксировать хвосты логов
```
echo "--- observer.log tail ---"       | tee -a diagnostics/post_model.log
tail -n 160 backend/logs/observer.log | tee -a diagnostics/post_model.log
echo "--- krai_backend.log tail ---"   | tee -a diagnostics/post_model.log
tail -n 160 logs/krai_backend.log      | tee -a diagnostics/post_model.log
```

10) Остановить сервер
```
kill $(cat backend/logs/uvicorn.pid) 2>/dev/null || true
```

Критерии
- Нет зависаний; запросы завершаются по таймауту либо с ответом 200/201/409/422/400.
- В логах видны этапы: `create_model: ... flushed`, `update_model: committed and refreshed`.
- На конфликт артикула возвращается 409 с JSON `detail.code = CONFLICT`.
- На некорректные FK при обновлении — 409 (IntegrityError).

Приложение (опционально)
- Если есть время — запусти фронт, убедись, что страницы `Models`/`Materials` открываются и ModelDrawer не падает:
  - `cd frontend && echo VITE_API_URL=http://localhost:8001/api/v1 > .env && npm run dev`
