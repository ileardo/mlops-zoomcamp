FROM python:3.12-slim

# upgrade pip 
RUN pip install -U pip  
# to manage dependencies
RUN pip install pipenv  

# set working directory as /app
WORKDIR /app  

# copy Pipfile and Pipfile.lock to Docker image
COPY ["Pipfile", "Pipfile.lock", "./"]  

# install dependencies on the base image
RUN pipenv install --system --deploy  

# copy the model and predict.py
COPY ["predict.py", "taxi_ridge_reg.bin", "./"]  

# expose port 9696 in the container
EXPOSE 9696  

# run gunicorn server
ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:9696", "predict:app"]  
