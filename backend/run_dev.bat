@echo off
set DATABASE_URL=postgresql://lifehub:lifehub_secret@localhost:5432/lifehub
uvicorn app.main:app --reload --host 0.0.0.0
