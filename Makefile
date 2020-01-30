
service=kafka
partitions=1
replication-factor=1
topic-name=test-topic-worker
message=hola-chiche

bash:
	docker-compose run --user=$(shell id -u) ${service} bash

# Build docker image with docker-compose
build:
	docker-compose build

run:
	docker-compose up

logs:
	docker-compose logs

# Removes old containers, free's up some space
remove:
	# Try this if this fails: docker rm -f $(docker ps -a -q)
	docker-compose rm --force -v

stop:
	docker-compose stop

run-kafka-cluster: build run

clean: stop remove

# Kafka related
list-topics:
	docker-compose exec kafka kafka-topics --list --zookeeper zookeeper:32181

create-topic:
	docker-compose exec kafka kafka-topics --create --zookeeper zookeeper:32181 --replication-factor ${replication-factor} --partitions ${partitions} --topic ${topic-name}

send-event:
	docker-compose exec kafka kafka-console-producer --broker-list kafka:9092 --topic ${topic-name}
