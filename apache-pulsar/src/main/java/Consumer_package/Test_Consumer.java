package Consumer_package;

import org.apache.pulsar.client.api.PulsarClient;
import org.apache.pulsar.client.api.PulsarClientException;
import org.apache.pulsar.client.api.Schema;
import org.apache.pulsar.client.api.SubscriptionInitialPosition;
import org.apache.pulsar.client.impl.schema.AvroSchema;

import java.util.concurrent.TimeUnit;
import java.io.IOException;
import org.apache.pulsar.client.api.Consumer;
import org.apache.pulsar.client.api.Message;
import ApachePulsarExample.mavenproject.configuration_info;
import sensor.Sensor;


public class Test_Consumer {
	 public static void main(String[] args) throws IOException {
		 
	//1.Initiate pulsar client
	 PulsarClient pulsarClient = PulsarClient.builder()
		    	.serviceUrl(configuration_info.SERVICE_URL)
		    	.build();
	 
	 //2.Create producer
//	 Consumer<User> consumer = pulsarClient.newConsumer(JSONSchema.of(User.class))
//			 .topic("persistent://public/default/test_topic")
//			 .consumerName("Test_consumer")
//			 .subscriptionInitialPosition(SubscriptionInitialPosition.Earliest)
//             .subscriptionName("test-subscriptions")
////             .subscriptionType(null) If I don't specify one subscription type by default it is exclusive.
//             .subscribe();
	 
	 Consumer<Sensor> consumer = pulsarClient.newConsumer(AvroSchema.of(Sensor.class))
			 .topic("persistent://public/default/FlinkTopicSinkFinal2")
			 .consumerName("Test_consumer1")
			 .subscriptionInitialPosition(SubscriptionInitialPosition.Earliest)
             .subscriptionName("test-subscriptions1")
//             .subscriptionType(null) If I don't specify one subscription type by default it is exclusive.
             .subscribe();
	 	 
     try {
         // Assuming consumer is already created and initialized
         while (true) {
            // Message<User> message = consumer.receive(1000, TimeUnit.MILLISECONDS); // 1-second timeout
             Message<Sensor> message = consumer.receive(1000, TimeUnit.MILLISECONDS);

             if (message == null) {
                 // No message received within timeout period, break the loop
                 System.out.println("No more messages, closing consumer.");
                 break;
             }
             
             System.out.println(message.getValue());
//             System.out.println("Acked message with key [" + message.getKey() + "]");
            
             try {
                 consumer.acknowledge(message);  // Acknowledge message
             } catch (Exception e) {
                 consumer.negativeAcknowledge(message);  // Negative acknowledge on error
                 e.printStackTrace();
             }
         }
     } catch (PulsarClientException e) {
         System.out.println("Error while consuming messages: " + e.getMessage());
         e.printStackTrace();
     } finally {
         // Make sure to close the consumer properly
         try {
             if (consumer != null) {
                 consumer.close();
                 System.out.println("Consumer closed.");
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
	 

