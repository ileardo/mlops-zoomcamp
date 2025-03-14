### Package version  
    pip freeze | grep package_name

### Create pipenv isolated from conda environment
```
pipenv install package1==version package2==version --python=version
```
or
```
pipenv install package1==version package2==version --python==path/to/python
```

### Create pipenv directly in the base environmet
    pipenv install --system ...

### Install development packages
    pipenv install --dev package1==version package2==version

### Enter pipenv
    pipenv shell

### Change prompt in shell
    PS1="> "

### Launch gunicron server:

```
pipenv install gunicorn
``` 

```    
gunicorn --bind=0.0.0.0:9696 predict:app
```

### Create container (check for same version of python)
Docker image tags: [dockerhub](https://hub.docker.com/_/python)  
Further instruction in [Dockerfile](./01_web_service/Dockerfile)

### Build container
    docker build -t image-name:tag

e.g.  

    docker build -t taxi-ride-duration-prediction:v1 .

### Run container
* `-it` for interactive mode: exing with ctrl + c
* `--rm` for removing image after exit
* `-p` to map port from host machine to container  

    ```
    docker run -it --rm -p 9696:9696 taxi-ride-duration-prediction:v1
    ```

### Convert jupyter to script
    jupyter nbconvert --to script notebook_name.ipynb