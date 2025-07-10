package Producer_package;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.pulsar.client.api.BatcherBuilder;
import org.apache.pulsar.client.api.Producer;
import org.apache.pulsar.client.api.PulsarClient;
import org.apache.pulsar.client.api.Schema;
import org.apache.pulsar.client.impl.schema.JSONSchema;


import ApachePulsarExample.mavenproject.configuration_info;
import User.User;


public class Test_Producer {

	public static void main(String[] args) throws IOException{
				// 1. Instantiate pulsar client 
			    PulsarClient pulsarClient = PulsarClient.builder()
			    	.serviceUrl(configuration_info.SERVICE_URL)
			    	.build();
			    
		    //2. Create a producer
			    Producer<User> producer = pulsarClient.newProducer(JSONSchema.of(User.class))
			    		.producerName("test_producer2")
			    		.topic("persistent://public/default/FlinkTopicJson2") //It is interpreted as "persistent://public/default/test-topic"
			    		.create();
			    
			    System.out.println("Running producer work loop");
			    
			    //3. Initiate a producer work loop/ Injecting data / What my producer does
			    
			    List<User> userList = new ArrayList<>();
			   
//			    for (int i = 0 ; i < 1000 ; i++) {
			    	 	userList.add(new User("PANOS", 27,1000));
				        userList.add(new User("TOD", 30,1100));
				        userList.add(new User("CAT", 22,1300));
				        userList.add(new User("PANOS", 35,1100));
				        userList.add(new User("TOD", 28,1200));
				        userList.add(new User("CAT", 24,1400));
				        userList.add(new User("PANOS", 26,1200));
				        userList.add(new User("TOD", 29,1300));
				        userList.add(new User("CAT", 31,1500));
			 
//			    }
			    
		        for (User user: userList) {
			    producer.newMessage(JSONSchema.of(User.class))
			    	.key(user.getName())
			    	.value(user)
			    	.send();
			    System.out.printf("I have sent message with key %s\n",user.getName());
		        }
		        
		       
			    
			    //4. Close the producer and the client
			    System.out.println("Closing producer");
			    producer.close();
			    System.out.println("Closing Pulsar Client");
			    pulsarClient.close();

	}

}
