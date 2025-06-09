## Start Prefect


Launch server:  

```bash
prefect server start
```

Once started, copy API URL and apply it to prefect configuration to point the correct API URL and send workflow metadata to server UI:

```bash
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

UI available at:
```bash
http://127.0.0.1:4200/api
```

---


