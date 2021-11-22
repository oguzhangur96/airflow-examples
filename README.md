# Airflow Examples

## Introduction to repository

This repository contains examples of airflow DAG's. First user have to make some adjustments to run docker container and debug airflow DAG loading with VSCode's remote container attachment.

1. Create ubuntu user named "airflow" with id specified at .env file. You could use command 

```bash 
sudo adduser -u 50000 airflow
```

2. Add airflow user to docker user group with 

```bash 
sudo usermod -aG docker airflow
```

3. Install VSCode's *Remote Containers* extension to connect to our container.

4. Run *docker-compose* when in this repository with 

```bash
docker-compose up
```

5. Press  ``` CTRL + Shift + P ``` and open *Remote Containers: Attach To a Runnning Container* and select container *airflow-examples_airflow-scheduler-1*
