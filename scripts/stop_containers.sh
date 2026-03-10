#!/usr/bin/bash

docker stop rustfs_container
sleep 2
docker stop postgres
sleep 2
docker stop mosquittoo
sleep 2
docker stop grafana
sleep 2
docker stop prometheus 
sleep 2
docker stop cadvisor 
sleep 2
docker stop taskmanager 
sleep 2 
docker stop jobmanager 
sleep 2
docker stop pulsar 
sleep 2
echo "All containers stoped" 
