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
		if (args.length < 2) {
			System.err.println("Usage: MqttHelperClientBatches <source-topic> <model-consume-topic>");
			System.exit(1);
		}

		PulsarClient pulsarClient = PulsarClient.builder().serviceUrl(configuration_info.SERVICE_URL).build();

		Consumer<byte[]> consumer = pulsarClient.newConsumer(Schema.BYTES)
				.topic("persistent://public/default/" + args[0])
				.consumerName("MqttHelperClientBatches_consumer")
				.subscriptionInitialPosition(SubscriptionInitialPosition.Latest)
				.subscriptionName("mqtt-helper-subscription").subscribe();

		Producer<Sensor> modelConsumeTopicProducer = pulsarClient.newProducer(AvroSchema.of(Sensor.class))
				.producerName("MqttHelperClientBatches_producer")
				.topic("persistent://public/default/" + args[1])
				.create();

		ObjectMapper objectMapper = new ObjectMapper();

		try {
			while (true) {
				Message<byte[]> message = consumer.receive(10000, TimeUnit.MILLISECONDS);

				if (message == null) {
					System.out.println("No messages received");
					System.out.println("Trying again.");
				} else {
					byte[] data = message.getValue();
					Sensor sensor = objectMapper.readValue(data, Sensor.class);
					System.out.println(sensor);
					try {
						consumer.acknowledge(message);
					} catch (Exception e) {
						consumer.negativeAcknowledge(message);
						e.printStackTrace();
						break;
					}
					modelConsumeTopicProducer.newMessage().key("sensor_id").value(sensor).send();
				}
			}
		} finally {
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
