# Troubleshooting

## Admin Reset funktioniert nicht

- `POST /api/admin/reset` ist nur aktiv, wenn `ADMIN_RESET_TOKEN` gesetzt ist.
- Stelle sicher, dass der Header `X-Reset-Token` exakt dem Wert von
  `ADMIN_RESET_TOKEN` entspricht.
- Wenn der Token fehlt oder falsch ist, antwortet der Server mit `401`.
