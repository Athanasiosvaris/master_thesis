package postgress_sink;

import java.io.IOException;
import java.util.concurrent.TimeUnit;

import org.apache.pulsar.client.api.Consumer;
import org.apache.pulsar.client.api.Message;
import org.apache.pulsar.client.api.Producer;
import org.apache.pulsar.client.api.PulsarClient;
import org.apache.pulsar.client.api.PulsarClientException;
import org.apache.pulsar.client.api.Schema;
import org.apache.pulsar.client.api.SubscriptionInitialPosition;
import org.apache.pulsar.client.impl.schema.AvroSchema;

import com.fasterxml.jackson.core.exc.StreamReadException;
import com.fasterxml.jackson.databind.DatabindException;
import com.fasterxml.jackson.databind.ObjectMapper;

import ApachePulsarExample.mavenproject.configuration_info;
import sensor.Sensor;

public class MqttHelperClientBatches {
	public static void main(String[] args) throws StreamReadException, DatabindException, IOException {
		// 1.Initiate pulsar client
		PulsarClient pulsarClient = PulsarClient.builder().serviceUrl(configuration_info.SERVICE_URL).build();

		// 2.Create producer
		Consumer<byte[]> consumer = pulsarClient.newConsumer(Schema.BYTES)
				.topic("persistent://public/default/model60BatchesConsumeTopicBatches").consumerName("Test_consumer")
				.subscriptionInitialPosition(SubscriptionInitialPosition.Earliest)
				.subscriptionName("test-subscriptions").subscribe();
		
		// Producer that sends the messages to pythonModelConsume topic
		Producer<Sensor> modelConsumeTopicProducer = pulsarClient.newProducer(AvroSchema.of(Sensor.class))
				.producerName("test_producer2")
				.topic("persistent://public/default/model60BatchesConsumeTopicPython") 
				.create();
		
		
		ObjectMapper objectMapper = new ObjectMapper();

		try {
			// Assuming consumer is already created and initialized
			while (true) {
				// Waiting up to 10 second to receive a message
				Message<byte[]> message = consumer.receive(10000, TimeUnit.MILLISECONDS);

				if (message == null) {
					// No message received within timeout period, break the loop
					System.out.println("No messages received");
					System.out.println("Trying again.");
				} else {
					byte[] data = message.getValue();
					Sensor sensor = objectMapper.readValue(data, Sensor.class); // readValue() method converts the
																				// byte[] data into a Sensor object
					System.out.println(sensor);
					try {
						consumer.acknowledge(message); // Acknowledge message
					} catch (Exception e) {
						consumer.negativeAcknowledge(message); // Negative acknowledge on error
						e.printStackTrace();
						break;
					}
					modelConsumeTopicProducer.newMessage().key("sensor_id").value(sensor).send(); 
				}
			}
		} finally {
			// Make sure to close the consumer properly
			try {
				if (consumer != null) {
					consumer.close();
					System.out.println("Consumer closed.");
					modelConsumeTopicProducer.close();
	                 System.out.println("Producer closed.");
					pulsarClient.close();
					System.out.println("Pulsar client closed.");
				}
			} catch (PulsarClientException e) {
				System.out.println("Error closing consumer: " + e.getMessage());
				e.printStackTrace();
			}
		}

	}

}
