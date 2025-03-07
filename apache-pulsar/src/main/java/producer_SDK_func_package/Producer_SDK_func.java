package producer_SDK_func_package;

import java.util.*;
import org.apache.pulsar.client.api.*;
import org.apache.pulsar.client.impl.schema.JSONSchema;

import User.User;
import ApachePulsarExample.mavenproject.configuration_info;

public class Producer_SDK_func {

	public static void main(String[] args) throws PulsarClientException {
		// 1. Create client
		PulsarClient client = PulsarClient.builder()
				.serviceUrl(configuration_info.SERVICE_URL)
				.build();

		// 2. Create producer
		Producer<User> producer = client.newProducer(JSONSchema.of(User.class))
				.producerName("Producer_SDK_func")
				.topic("persistent://public/default/Test_SDK_func_topic")
				.create();

		// 3. Preparations of the messages
		List<User> Users = new ArrayList<>();

		Users.add(new User("KOSTAS", 55));
		Users.add(new User("Eleni", 53));
		Users.add(new User("Maria", 23));
		Users.add(new User("Lambros", 27));
		
		// 4. Send messages
		for (User s : Users) {
			producer.newMessage(JSONSchema.of(User.class))
			.key(s.getName())
			.value(s)
			.send();
			 System.out.printf("I have sent message with key %s\n",s.getName());
		}
		
		producer.flush();

		// 5.Closing producer and Pulsar client
		try {
			System.out.println("Closing producer");
			producer.close();
			System.out.println("Closing Pulsar client");
			client.close();
		} catch (Exception e) {
			System.out.println("Error while closing either the producer or the Pulsar client");
			e.printStackTrace();
		}

	}

}
