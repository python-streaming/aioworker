## aioworker

A Python worker running over `asyncio`

### Requirements

python 3.7+, aiokafka==0.5.2, aiotools==0.8.5

### Usage

Install requirements:

```bash
pip install requirements.txt
```

The project contains two ways of running the workers:

1. Run only the wWrker with a `kafka consumer`
2. Run the Worker with a `kafka consumer` + TCP server on `localhost:8888`

For option [1] execute:

```bash
python worker.py
```

For option [2] execute:

```bash
python worker_tcp_server.py
```

After the worker is running, in a different terminal execute in:

```bash
kafka-console-producer --broker-list 0.0.0.0:9092 --topic [your-topic]

>hola
>chiche
```

If you choose option [2], you can send message to the TCP server as well.

```bash
curl -X POST localhost:8888 -d "hola chiche"
```

and you will see the in the worker logs the data received over `TCP`.

## How to stop the worker:

`ctrl+c`

## Default values:

| Variable | Default |
|----------|---------|
| TCP server | 0.0.0.0:8888|
| BOOTSTRAP_SERVERS | 0.0.0.0:9092|
| TOPIC | test-topic-worker|
| GROUP_ID | test-consumer-group|
| AUTO_OFFSET_RESET| earliest|
