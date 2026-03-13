//package Producer_package;
//
//import java.io.IOException;
//import java.util.ArrayList;
//import java.util.List;
//import org.apache.pulsar.client.api.Producer;
//import org.apache.pulsar.client.api.PulsarClient;
//import org.apache.pulsar.client.api.Schema;
//import org.apache.pulsar.client.impl.schema.JSONSchema;
//import org.apache.pulsar.client.impl.schema.StringSchema;
//
//import ApachePulsarExample.mavenproject.configuration_info;
//import User.User;
//
//public class string_producer {
//	
//	public static void main(String[] args) throws IOException {
//		// 1. Instantiate pulsar client 
//	    PulsarClient pulsarClient = PulsarClient.builder()
//	    	.serviceUrl(configuration_info.SERVICE_URL)
//	    	.build();
//	    
//	//2. Create a producer
//	    Producer<String> producer = pulsarClient.newProducer(Schema.STRING)
//	    		.producerName("my_producer")
//	    		.topic("persistent://public/default/FlinkTopicString") //It is interpreted as "persistent://public/default/test-topic"
//	    		.create();
//	    
//	    System.out.println("Running producer work loop");
//	    
//	    //3. Initiate a producer work loop/ Injecting data / What my producer does
//	    
//	    List<String> userList = new ArrayList<>();
//	    
//	    for (int i = 0 ; i <1000 ; i++) {
//	    	userList.add("noaaa");
//	    }
//	     
//	    for (String user: userList) {
//	    producer.newMessage(Schema.STRING)
//	    	.key(user)
//	    	.value(user)
//	    	.send();
//	    System.out.printf("I have sent message with key %s\n",user);
//	    }
//	    
//	   
//	    
//	    //4. Close the producer and the client
//	    System.out.println("Closing producer");
//	    producer.close();
//	    System.out.println("Closing Pulsar Client");
//	    pulsarClient.close();
//	}
//	
//
//}
