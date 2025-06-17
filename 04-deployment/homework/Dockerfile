FROM agrigorev/zoomcamp-model:mlops-2024-3.10.13-slim
# model already present in the image as model.bin

RUN pip install -U pip
RUN pip install pipenv

WORKDIR /app

COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --system --deploy

COPY starter.py ./

RUN ls -la /app/

CMD ["python", "starter.py", "--help"]