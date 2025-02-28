package conusmer_package_native_function;

import java.util.*;
import java.util.concurrent.TimeUnit;

import org.apache.pulsar.client.api.*;
import ApachePulsarExample.mavenproject.configuration_info;

public class Test_consumer_native_function {

	public static void main(String[] args) throws PulsarClientException {

		// 1. Create Pulsar Client
		PulsarClient client = PulsarClient.builder().serviceUrl(configuration_info.SERVICE_URL).build();

		// 2. Create Pulsar Consumer
		Consumer<String> consumer = client.newConsumer(Schema.STRING).consumerName("Test_Consumer_native_function")
				.topic("persistent://public/default/test-topic-String-outputt")
				.subscriptionType(SubscriptionType.Exclusive)
				.subscriptionName("Test_Subscription_native_function")
				.subscribe();

		// 3. Consume messages
		try {
			while (true) {
				Message<String> msg = consumer.receive(1000, TimeUnit.MILLISECONDS);
				if (msg == null) {
					// No more messages to consume
					System.out.println("No more messages to consume.Closing consumer.");
					break;
				} else {
					try {
						consumer.acknowledge(msg);
						System.out.println("Acked message [" + msg.getValue() + "]");
					} catch (Exception e) {
						System.out.println("Failed to acknowledge message. I send negative acknowledgement");
						consumer.negativeAcknowledge(msg); // Negative acknowledge on error
						e.printStackTrace();
					}
				}
			}
		} catch (Exception e) {
			// Problima kata to receive kai kleise
			System.out.println("Error while consuming messages: " + e.getMessage());
			e.printStackTrace();
		} finally {
			// Closing consumer and client
			try {
				if (consumer != null) {
					System.out.println("Closing the consumer");
					consumer.close();
					System.out.println("Closing the client");
					client.close();
				}
			} catch (Exception e) {
				// Problem while closing the consumer/client
				System.out
						.println("Exception while closing the consumer or the client. Error message:" + e.getMessage());
				e.printStackTrace();
			}

		}
	}
}
