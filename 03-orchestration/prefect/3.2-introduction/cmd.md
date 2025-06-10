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

Stop Prefect process:
```bash
pkill -f prefect
```

---

## Deployment

1. Initialize Prefect project:

    ```bash
    prefect init
    ```

2. Add `@flow` decorator to code

3. Login to Prefect Cloud `prefect cloud login` or start Prefect server `Prefect server start`.

4. Start a worker that polls the work pool:
    
    * From command line:
        ```bash
        prefect worker start -p my-pool -t process
        ```

    * From UI:
        ```
        Work Pools > Create work pool
        ```

        Then, start worker from terminal: `prefect worker start --pool "my-pool"`

5. Deploy flow:

    ```bash
    prefect deploy file.py:entry_point_flow -n deploy_name -p pool-name
    ```

    e.g.

    ```bash
    prefect deploy 3.4-deployment/orchestrate.py:run -n taxy-deploy -p my-pool
    ```

6. Start a run from the deployed flow:
    * From command line:
        ```bash
        prefect deployment run flow-name/deploy_name  --param p1=v1 --param p2=v2
        ```

        e.g.
        ```bash
        prefect deployment run train-taxi-duration-model/taxy-deploy --param year=2023 --param month=1
        ```

    * From UI:
        ```
        Flows > Deployment > Run
        ```

---

## Blocks

Blocks info:
```bash
prefect block ls
```
```bash
prefect block type ls  
```

Register block types:
```bash
prefect block register -m prefect_aws
```

---

## AWS credentials

```bash
echo 'export AWS_ACCESS_KEY_ID="your-access-key-here"' >> ~/.bashrc
```
```bash
echo 'export AWS_SECRET_ACCESS_KEY="your-secret-key-here"' >> ~/.bashrc
```
```bash
echo 'export AWS_DEFAULT_REGION="your-region"' >> ~/.bashrc
```

# Ricarica il file
```bash
source ~/.bashrc
```

---