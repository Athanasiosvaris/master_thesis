import pulsar

client = pulsar.Client('pulsar://localhost:6650')
producer = client.create_producer(topic="Python_test_topic",producer_name="pythonTestproducer")

for i in range (10):
    producer.send(('Hello there from Python %d' %i).encode('utf-8'))

client.close(0)
    