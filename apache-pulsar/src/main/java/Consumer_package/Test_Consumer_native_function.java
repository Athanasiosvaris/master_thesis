package Consumer_package;

import java.util.*;
import java.util.concurrent.TimeUnit;

import org.apache.pulsar.client.api.*;
import ApachePulsarExample.mavenproject.configuration_info;

public class Test_Consumer_native_function {

	public static void main(String[] args) throws PulsarClientException {
		
		//1. Create Pulsar Client
		PulsarClient client = PulsarClient.builder()
				.serviceUrl(configuration_info.SERVICE_URL)
				.build();
		
		//2. Create Pulsar Consumer
		Consumer<String> consumer = client.newConsumer(Schema.STRING)
				.consumerName("Test_Consumer_native_function")
				.topic("persistent://public/default/test_topic-Stringg")
				.subscriptionType(SubscriptionType.Exclusive)
				.subscriptionName("Test_Subscription_native_function")
				.subscribe();
				
		//3. Consume messages
		while(true) {
			Message<String> msg = consumer.receive(1000, TimeUnit.MILLISECONDS);
			
			if (msg == null) {
				//No more messages 
				System.out.println("No more messages to consume.Closing consumer.");
				break;
			}
			else 
			{
				try {consumer.acknowledge(msg);}
				catch(Exception e) {
					   consumer.negativeAcknowledge(msg);  // Negative acknowledge on error
		               e.printStackTrace();
				}
				
			}
			
		}
		

	}

}
