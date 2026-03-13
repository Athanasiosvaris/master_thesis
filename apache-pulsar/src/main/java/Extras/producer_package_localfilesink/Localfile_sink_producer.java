//package producer_package_localfilesink;
//
//import java.util.ArrayList;
//import java.util.List;
//
//import org.apache.pulsar.client.api.Producer;
//import org.apache.pulsar.client.api.PulsarClient;
//import org.apache.pulsar.client.api.PulsarClientException;
//import org.apache.pulsar.client.api.Schema;
//import org.apache.pulsar.client.impl.schema.JSONSchema;
//
//import ApachePulsarExample.mavenproject.configuration_info;
//import User.User;
//
//public class Localfile_sink_producer {
//
//	public static void main(String[] args) throws PulsarClientException  {
//		// 1. Instantiate pulsar client 
//	    PulsarClient pulsarClient = PulsarClient.builder()
//	    	.serviceUrl(configuration_info.SERVICE_URL)
//	    	.build();
//	    
//    //2. Create a producer
//	    Producer<String> producer = pulsarClient.newProducer(Schema.STRING)
//	    		.producerName("test_producer")
//	    		.topic("persistent://public/default/test_sink") //It is interpreted as "persistent://public/default/test-topic"
//	    		.create();
//	    
//	    System.out.println("Running producer work loop");
//	    
//	  //3. Send messages to the topic/ Initiate a producer work loop
//		 List<String> stringList = new ArrayList<>();
//	        
//	     stringList.add("Thanos");
//	     stringList.add("Kostas");
//	     stringList.add("Maria");
//	     stringList.add("Lampbros");
//	     stringList.add("Eleni");
//	     
//	     for (String s: stringList) {
//	    	 producer.newMessage()
//	    	 		 .key(s)
//	    	 		 .value(s)
//	    	 		 .send();
//	    	 System.out.printf("I have sent message with key %s\n",s);
//	     }
//	     
//	     producer.flush();
//	    
//	    //4. Close the producer and the client
//	    System.out.println("Closing producer");
//	    producer.close();
//	    System.out.println("Closing Pulsar Client");
//	    pulsarClient.close();
//
//
//	}
//
//}
