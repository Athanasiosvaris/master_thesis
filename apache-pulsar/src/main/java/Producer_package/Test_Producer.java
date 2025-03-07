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
		// TODO Auto-generated method stub
				// 1. Instantiate pulsar client 
			    PulsarClient pulsarClient = PulsarClient.builder()
			    	.serviceUrl(configuration_info.SERVICE_URL)
			    	.build();
			    
		    //2. Create a producer
			    Producer<User> producer = pulsarClient.newProducer(JSONSchema.of(User.class))
			    		.producerName("test_producer")
			    		.topic("persistent://public/default/test_topic") //It is interpreted as "persistent://public/default/test-topic"
//			    		.enableBatching(true)
//			    		.batcherBuilder(BatcherBuilder.KEY_BASED) //This ensures that messages with the same key will end up in the same batch
			    		.create();
			    
			    System.out.println("Running producer work loop");
			    
			    //3. Initiate a producer work loop/ Injecting data / What my producer does
			    
			    List<User> userList = new ArrayList<>();
			    
			    userList.add(new User("Tom", 27));
		        userList.add(new User("Alice", 30));
		        userList.add(new User("Bob", 22));
		        userList.add(new User("Charlie", 35));
		        userList.add(new User("David", 28));
		        userList.add(new User("Eve", 24));
		        userList.add(new User("Frank", 26));
		        userList.add(new User("Grace", 29));
		        userList.add(new User("Hannah", 31));
		        userList.add(new User("Isaac", 33));
			    
			    
		        for (User user: userList) {
			    producer.newMessage(JSONSchema.of(User.class))
			    	.key(user.getName())
			    	.value(user)
			    	.send();
			    System.out.printf("I have sent message with key %s\n",user.getName());
		        }
		        
			    producer.flush();
			    
			    //4. Close the producer and the client
			    System.out.println("Closing producer");
			    producer.close();
			    System.out.println("Closing Pulsar Client");
			    pulsarClient.close();

	}

}
