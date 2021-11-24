# An Overview of Airflow Executers

## Why and When Airflow executers matters?

Executer is a component of the the Airflow Scheduler which runs task instances locally or remotely via remote workers. Selecting the right executor task will be critical since executor will be decisive factor in terms of scaling power and configuration/monitoring/maintanance burden.

There are two types of executors. *Local* and *Remote*. Local executors run task locally, which means inside the scheduler process.

Also, you could write your custom executor.

### Local Executors ###

#### **Sequential Executor** ####

Sequential executor is the default executor when you first install airflow. Since it uses SQLite as DB Backend it can only handle a single task, because SQLite does not allow more than one connection.

#### **Local Executor** ####

Local executor is same with sequantial executor but it has an ability to spawn paralel processes. This behaivour could be adjusted with ``` self.parallelism ``` parameter. 0 means unlimited processes could spawn, >0 means spawn of processes is limited with the number we wrote. Sequantial executor is a special case of local executor with ``` self.parallelism == 1```

#### **Debug Executor** ####

Debug Executor is meant as a debug tool. You could add below line to your DAG file and run it from debugger:

``` python
if __name__ == "__main__":
    from airflow.utils.state import State

    dag.clear(dag_run_state=State.NONE)
    dag.run()
```

If you wish to fail all the other running and scheduled tasks immediately you could set ``` AIRFLOW__DEBUG__FAIL_FAST=True ``` in your configuration.

You must also set ``` AIRFLOW__CORE__EXECUTOR=DebugExecutor ``` to activate debug executor.

### Remote Executors ###

#### **Celery Executor** ####

Celery executer is one of the ways to scale out the number of workers. You need to set-up the celery with the broker and result backend of your choice.

In your celery workers requirements below must be satisfied:

1. Airflow needs to be installed and CLI needs to be on path.
2. Airflow configuration settings should be homogeneous across the cluster
3. Operators which are executed on the workers need to satisfy their dependencies. For example, if you use the ``` MySqlOperator ``` required library needs to be avaliable in the ``` PYTHONPATH ```
4. The worker needs to have access to its DAGS_FOLDER, and you need to synchronize the filesystems by your own means. A common setup would be to store your DAGS_FOLDER in a Git repository and sync it across machines using Chef, Puppet, Ansible, or whatever you use to configure machines in your environment. If all your boxes have a common mount point, having your pipelines files shared there should work as well

Although airflow celery architecture is too complex to explain here, celery workers are basically airflow installed remote machines which are accessible by celery message broker and result backend. You could assign different workers to different queues in order to optimize your task execution workflow. For example one queue could have task which could be executed in short amount of time or one worker might have a resource intensive environment while other have not.

#### **Kubernetes Executor** ####

Kubernetes executer runs each task instance on its own Kubernetes pod. Scheduler it self does not need to be on kubernetes cluster but needs to access to kubernetes cluster. When DAG submits a task KubernetesExecuter request a worker pod from cluster, worker pod runs the task, submits its results and terminates. Similar to celery executor, workers needs to access DAG files.

Kubernetes image configuration could be extended or overridden.

Comparison to CeleryExecuter, KubernetesExecuter could scale down to 0 or maximum. In the regular CeleryExecuter workers are always up. However, in the [official Apache Airflow Helm chart](https://airflow.apache.org/docs/helm-chart/stable/index.html) could automatically scale down Celery workers to 0.

Celery workers will have less latency because they are already up. However when more than one process is runnnig on a pod, one have to careful about resource utilization. Kubernetes Executor is better in terms of long running tasks because CeleryExecutor could end the task if it is running for too long depending on the configuration. KubernetesExecutor could also be helpful in terms of non-uniform resurce and image required tasks. 

One does not have to choose either CeleryExecuter or KubernetesExecuter. You could choose CeleryKubernetesExecuter which runs tasks on Celery queue on default.

#### **CeleryKubernetes Executor** ####

It requires setting up CeleryExecutor and KubernetesExecutor. When your environment requires below actions it could be used.

1. The number of tasks needed to be scheduled at the peak exceeds the scale that your Kubernetes cluster can comfortably handle
2. A relative small portion of your tasks requires runtime isolation.
3. You have plenty of small tasks that can be executed on Celery workers but you also have resource-hungry tasks that will be better to run in predefined environments.

#### **Dask Executor** ####

Dask clusters can be run on a single machine or on remote networks.
- Each Dask worker must be able to import Airflow and any dependencies you require.