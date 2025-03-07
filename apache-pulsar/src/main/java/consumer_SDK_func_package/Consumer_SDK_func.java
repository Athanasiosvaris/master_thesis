package consumer_SDK_func_package;

import java.util.*;
import java.util.concurrent.TimeUnit;

import org.apache.pulsar.client.api.*;
import org.apache.pulsar.client.impl.schema.JSONSchema;

import User.User;

import ApachePulsarExample.mavenproject.configuration_info;

public class Consumer_SDK_func {

	public static void main(String[] args) throws PulsarClientException {
		// 1. Create Pulsar client
		PulsarClient client = PulsarClient.builder()
				.serviceUrl(configuration_info.SERVICE_URL)
				.build();

		// 2. Create consumer
		Consumer<User> consumer = client.newConsumer(JSONSchema.of(User.class))
				.consumerName("Consumer_SDK_func")
				.topic("persistent://public/default/Test_SDK_func_topic_output")
				.subscriptionName("Test_Subscription_SDK_function")
				.subscriptionType(SubscriptionType.Exclusive)
				.subscribe();
		
		// 3. Consume messages
		try {
			while (true) {
				Message<User> msg = consumer.receive(1000, TimeUnit.MILLISECONDS);
				if (msg == null) {
					System.out.println("No more messages to receive. Closing the consumer and the Apache pulsar client");
					break;
				} else {
					try {
						consumer.acknowledge(msg);
						User user = msg.getValue();
						System.out.println("User name : " + user.getName() + " User age: " + user.getAge());
						//System.out.println("I have acked message with key: " + msg.getValue());
					} catch (Exception e) {
						System.out.println("I could not ack message with key : " + msg.getKey());
						consumer.negativeAcknowledge(msg);
						e.printStackTrace();
					}
				}
			}

		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			try {
				System.out.println("Closing producer");
				consumer.close();
				System.out.println("Closing Pulsar client");
				client.close();
			} catch (Exception e) {
				System.out.println("Error while closing either the producer or the Pulsar client");
				e.printStackTrace();
			}
		}
	}

}
