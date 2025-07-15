# Unit test

## Pipenv

Install pipenv

```bash
pipenv install 
```

Add pytest to pipenv dev `group`

```bash
pipenv install --dev pytest
```

Activate pipenv
```bash
pipenv shell
```

Rename command line
```bash
PS1="> "
```

## Configure test via environment

Select python interpreter  
1. Go to extensions and search for `python` → `install`
2. `Ctrl + shift + p` and search for `python select interpreter`
3. To find the path of the right python: `pipenv --venv`
4. Add to the path found: `/bin/python`
5. Select new interpreter

Configure pytest
1. Add `__init__.py` to `tests` folder
2. pytest extension → `Configure Python Tests` → `pytest` → select `tests` folder
3. If `tests` folder is not available, modify `.vscode/setting.json`
4. Add `pytest.ini`:
    ```
    [pytest]
    testpaths = path/to/tests
    ```
5. Reload window (`Developer: Reload Window`) and refresh Testing

## Docker

Build docker:
```bash
docker build -t web-service-duration:v1 .
```

Run container:

```bash
docker run -it --rm -p 9696:9696 web-service-duration:v1
```

Test API:
```python
python predict_api.py
```

## CI/CD

Check error code of previous command:
```bash
echo $?
```

Should be `0`


## Linting and formatting

### Linting

Install:
```bash
pipenv install --dev pylint
```

Run:
```bash
pylint --recursive=y .
```

Disable pylint for entire codebase: `pyproject.toml`

Disable pylint for specific class or specific file (put at beggining of the file): 
```python
# pylint: disable=lint-to-disable
```

### Formatting

Install:
```bash
pipenv install --dev black
```