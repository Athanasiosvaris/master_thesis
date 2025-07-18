//package postgress_sink;
//
//import java.util.ArrayList;
//import java.util.List;
//
//import org.apache.pulsar.client.api.Producer;
//import org.apache.pulsar.client.api.PulsarClient;
//import org.apache.pulsar.client.api.PulsarClientException;
//import org.apache.pulsar.client.api.Schema;
//import org.apache.pulsar.client.api.schema.GenericRecord;
//import org.apache.pulsar.client.api.schema.GenericSchema;
//import org.apache.pulsar.client.api.schema.RecordSchemaBuilder;
//import org.apache.pulsar.client.api.schema.SchemaBuilder;
//import org.apache.pulsar.client.impl.schema.JSONSchema;
//import org.apache.pulsar.common.schema.SchemaInfo;
//import org.apache.pulsar.common.schema.SchemaType;
//
//import ApachePulsarExample.mavenproject.configuration_info;
//import User.User;
//
//public class AvroProducer {
//	public static void main(String[] args) throws PulsarClientException {
//		
//		// 1. Instantiate pulsar client 
//	    PulsarClient pulsarClient = PulsarClient.builder()
//	    	.serviceUrl(configuration_info.SERVICE_URL)
//	    	.build();
//	    
//	    RecordSchemaBuilder schemabuilder = SchemaBuilder.record("Test");
//	    schemabuilder.field("id").type(SchemaType.INT32); // Integer field for id (serial)
//	    schemabuilder.field("name").type(SchemaType.STRING);  // String field for name (VARCHAR)
//	    SchemaInfo schemaInfo = schemabuilder.build(SchemaType.AVRO);
//        GenericSchema<GenericRecord> schema = Schema.generic(schemaInfo);
//        
//    //2. Create a producer
//	    Producer<GenericRecord> producer = pulsarClient.newProducer(schema)
//	    		.producerName("test_producer")
//	    		.topic("persistent://public/default/postgress_sink") //It is interpreted as "persistent://public/default/test-topic"
//	    		.create();
//	    
//	    System.out.println("Running producer work loop");
//	    
//	    User U = new User("Kostas",5);
//	    
//	    
//	  //3. Initiate a producer work loop/ Injecting data / What my producer does
//	    GenericRecord record = schema.newRecordBuilder()
//                .set("id", U.getAge())
//                .set("name", U.getName())
//                .build();
//	    
//	    producer.newMessage()
//	    			.key("id")
//	    			.value(record)
//	    			.send();
//	    System.out.printf("I have sent message\n");
//	    
//        
//	    producer.flush();
//	    
//	    //4. Close the producer and the client
//	    System.out.println("Closing producer");
//	    producer.close();
//	    System.out.println("Closing Pulsar Client");
//	    pulsarClient.close();
//	}
//}
