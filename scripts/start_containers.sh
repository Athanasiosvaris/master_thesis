#!/usr/bin/bash

docker start pulsar 
sleep 2
docker start jobmanager
sleep 2
docker start taskmanager
sleep 2
docker start cadvisor
sleep 2
docker start prometheus
sleep 2
docker start grafana
sleep 2
docker start mosquittoo
sleep 2
docker start postgres
sleep 2
docker start rustfs_container
sleep 2
echo "All containers started"
echo "Running:"
echo "docker ps"
docker ps



