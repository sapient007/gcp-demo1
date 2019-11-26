FROM tensorflow/tensorflow:2.0.0-gpu-py3

RUN apt-get update && apt-get install -y libsnappy-dev

### Actually package our app now

WORKDIR /opt/gcp-demo1/mlp_trainer

# Do this first to cache this step
COPY requirements.txt /opt/gcp-demo1/mlp_trainer/requirements.txt

RUN pip install -r requirements.txt
COPY ./ /opt/gcp-demo1/mlp_trainer

ENTRYPOINT ["python", "-m", "trainer.task"]