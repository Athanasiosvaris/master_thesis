package postgress_sink;

import java.io.IOException;
import java.util.concurrent.TimeUnit;

import org.apache.pulsar.client.api.Consumer;
import org.apache.pulsar.client.api.Message;
import org.apache.pulsar.client.api.Producer;
import org.apache.pulsar.client.api.PulsarClient;
import org.apache.pulsar.client.api.PulsarClientException;
import org.apache.pulsar.client.api.Schema;
import org.apache.pulsar.client.api.SubscriptionInitialPosition;
import org.apache.pulsar.client.api.schema.GenericRecord;
import org.apache.pulsar.client.api.schema.GenericSchema;
import org.apache.pulsar.client.api.schema.RecordSchemaBuilder;
import org.apache.pulsar.client.api.schema.SchemaBuilder;
import org.apache.pulsar.client.impl.schema.AvroSchema;
import org.apache.pulsar.client.impl.schema.JSONSchema;
import org.apache.pulsar.common.schema.SchemaInfo;
import org.apache.pulsar.common.schema.SchemaType;

import com.fasterxml.jackson.core.exc.StreamReadException;
import com.fasterxml.jackson.databind.DatabindException;
import com.fasterxml.jackson.databind.ObjectMapper;

import ApachePulsarExample.mavenproject.configuration_info;
import sensor.Sensor;

public class TestConsumerFinal {

	public static void main(String[] args) throws StreamReadException, DatabindException, IOException {
		//1.Initiate pulsar client
		 PulsarClient pulsarClient = PulsarClient.builder()
			    	.serviceUrl(configuration_info.SERVICE_URL)
			    	.build();
		 
		 //2.Create producer
		 Consumer<byte []> consumer = pulsarClient.newConsumer(Schema.BYTES)
				 .topic("persistent://public/default/FlinkTopicSinkFinal")
				 .consumerName("Test_consumer")
				 .subscriptionInitialPosition(SubscriptionInitialPosition.Earliest)
	             .subscriptionName("test-subscriptions")
	             .subscribe();
		

//		    RecordSchemaBuilder schemabuilder = SchemaBuilder.record("Test_Json");
//		    schemabuilder.field("sensor_id").type(SchemaType.INT32).optional(); 
//		    schemabuilder.field("sensor_energy_value").type(SchemaType.DOUBLE).optional();   
//		    schemabuilder.field("sensor_timestamp").type(SchemaType.INT64).optional(); // Long = INT64 in JAVA
//		    SchemaInfo schemaInfo = schemabuilder.build(SchemaType.AVRO);
//	        GenericSchema<GenericRecord> schema = Schema.generic(schemaInfo);
		 
		 Producer<Sensor> producer = pulsarClient.newProducer(AvroSchema.of(Sensor.class))
		    		.producerName("test_producer2")
		    		.topic("persistent://public/default/FlinkTopicSinkFinal2") //It is interpreted as "persistent://public/default/test-topic"
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
	             Sensor sensor = objectMapper.readValue(data, Sensor.class); //readValue() method converts the byte[] data into a Sensor object
	             
	             try {
	                 consumer.acknowledge(message);  // Acknowledge message
	                 System.out.print("Current message's (sensor) id is: \n" + sensor.getSensor_id() + "\n");
	                 
	             } catch (Exception e) {
	                 consumer.negativeAcknowledge(message);  // Negative acknowledge on error
	                 e.printStackTrace();
	             }
	             
//	             GenericRecord record = schema.newRecordBuilder()
//	                     .set("sensor_id", sensor.getSensor_id())
//	                     .set("sensor_energy_value", sensor.getSensor_energy_value())
//	                     .set("sensor_timestamp", sensor.getSensor_timestamp())
//	                     .build();
	             
	             producer.newMessage()
			    	.key("sensor_id")
			    	.value(sensor)
			    	.send();
	             
			    System.out.printf("I have sent message with key %s\n",sensor.getSensor_id());
			    System.out.println();
	         }
	         }
		 finally {
	         // Make sure to close the consumer properly
	         try {
	             if (consumer != null) {
	                 consumer.close();
	                 System.out.println("Consumer closed.");
//	                 producer.close();
//	                 System.out.println("Producer closed.");
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
