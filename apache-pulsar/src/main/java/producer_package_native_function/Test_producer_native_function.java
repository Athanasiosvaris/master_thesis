package producer_package_native_function;

import java.util.*;
import java.io.IOException;

import org.apache.pulsar.client.api.*;
import ApachePulsarExample.mavenproject.configuration_info;

public class Test_producer_native_function {
	public static void main(String[] args) throws IOException {
		//1. Create a Pulsar Client
		PulsarClient client = PulsarClient.builder().serviceUrl(configuration_info.SERVICE_URL).build();
		
		//2.Create producer
		Producer<String> producer = client.newProducer(Schema.STRING).
				producerName("Test_Producer_native_function")
				.topic("persistent://public/default/test_topic-Stringg")
				.create();
		
		System.out.println("Producer created");
		
		//3. Send messages to the topic/ Initiate a producer work loop
		 List<String> stringList = new ArrayList<>();
	        
	     stringList.add("Thanos");
	     stringList.add("Kostas");
	     stringList.add("Maria");
	     stringList.add("Lampbros");
	     stringList.add("Eleni");
	     
	     for (String s: stringList) {
	    	 producer.newMessage()
	    	 		 .key(s)
	    	 		 .value(s)
	    	 		 .send();
	    	 System.out.printf("I have sent message with key %s\n",s);
	     }
	     
	     producer.flush();
	     
		//4. Close producer and client
	    System.out.println("Closing producer");
	    producer.close();
	    System.out.println("Closing client");
		client.close();
	}
}
