package postgress_sink;

import org.apache.pulsar.client.api.PulsarClient;
import org.apache.pulsar.client.api.PulsarClientException;
import org.apache.pulsar.client.api.Schema;
import org.apache.pulsar.client.api.SubscriptionInitialPosition;
import org.apache.pulsar.client.impl.schema.JSONSchema;
import org.apache.pulsar.common.schema.SchemaInfo;
import org.apache.pulsar.common.schema.SchemaType;

import java.util.concurrent.TimeUnit;
import java.io.IOException;
import org.apache.pulsar.client.api.Consumer;
import org.apache.pulsar.client.api.Message;
import org.apache.pulsar.client.api.Producer;
import org.apache.pulsar.client.api.schema.GenericRecord;
import org.apache.pulsar.client.api.schema.GenericSchema;
import org.apache.pulsar.client.api.schema.RecordSchemaBuilder;
import org.apache.pulsar.client.api.schema.SchemaBuilder;

import com.fasterxml.jackson.databind.ObjectMapper;

import ApachePulsarExample.mavenproject.configuration_info;
import User.User;
public class Test_consumer {
		 public static void main(String[] args) throws IOException {
			 
		//1.Initiate pulsar client
		 PulsarClient pulsarClient = PulsarClient.builder()
			    	.serviceUrl(configuration_info.SERVICE_URL)
			    	.build();
		 
		 //2.Create producer
		 Consumer<byte []> consumer = pulsarClient.newConsumer(Schema.BYTES)
				 .topic("persistent://public/default/FlinkTopicSink")
				 .consumerName("Test_consumer")
				 .subscriptionInitialPosition(SubscriptionInitialPosition.Earliest)
	             .subscriptionName("test-subscriptions")
	             .subscribe();
		 

		    RecordSchemaBuilder schemabuilder = SchemaBuilder.record("Test_Json");
		    schemabuilder.field("name").type(SchemaType.STRING).optional(); // String field for name (VARCHAR)
		    schemabuilder.field("age").type(SchemaType.INT32).optional();  // 
		    schemabuilder.field("salary").type(SchemaType.INT32).optional();
		    SchemaInfo schemaInfo = schemabuilder.build(SchemaType.AVRO);
	        GenericSchema<GenericRecord> schema = Schema.generic(schemaInfo);
		 
		 Producer<GenericRecord> producer = pulsarClient.newProducer(schema)
		    		.producerName("test_producer2")
		    		.topic("persistent://public/default/postgressSinkJSONNNn") //It is interpreted as "persistent://public/default/test-topic"
		    		.create();
		    
		 ObjectMapper objectMapper = new ObjectMapper(); 
	     try {
	         // Assuming consumer is already created and initialized
	         while (true) {
	            // Message<User> message = consumer.receive(1000, TimeUnit.MILLISECONDS); // 1-second timeout
	             Message<byte []> message = consumer.receive(1000, TimeUnit.MILLISECONDS);
	             
	             if (message == null) {
	                 // No message received within timeout period, break the loop
	                 System.out.println("No more messages, closing consumer.");
	                 break;
	             }
	             
	             byte[] data = message.getValue();
	             User user = objectMapper.readValue(data, User.class);
	             
	             try {
	                 consumer.acknowledge(message);  // Acknowledge message
	                 System.out.print("Current message's (user) name is: \n" + user.getName() + "\n");
	                 
	             } catch (Exception e) {
	                 consumer.negativeAcknowledge(message);  // Negative acknowledge on error
	                 e.printStackTrace();
	             }
	             
	             GenericRecord record = schema.newRecordBuilder()
	                     .set("name", user.getName())
	                     .set("age", user.getAge())
	                     .set("salary", user.getSalary())
	                     .build();
	             
	             producer.newMessage()
			    	.key("name")
			    	.value(record)
			    	.send();
	             
			    System.out.printf("I have sent message with key %s\n",user.getName());
			    System.out.println();
	         }
	         }
	     
	      finally {
	         // Make sure to close the consumer properly
	         try {
	             if (consumer != null) {
	                 consumer.close();
	                 System.out.println("Consumer closed.");
	                 producer.close();
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
		 
