//package sensor_producer;
//
//import java.io.IOException;
//import java.util.ArrayList;
//import java.util.List;
//
//import org.apache.pulsar.client.api.Producer;
//import org.apache.pulsar.client.api.PulsarClient;
//import org.apache.pulsar.client.impl.schema.JSONSchema;
//
//import ApachePulsarExample.mavenproject.configuration_info;
//import sensor.Sensor;
//
//
//public class Sensor_producer {
//	public static void main(String[] args) throws IOException, InterruptedException {
//		//1) Create Pulsar client
//		PulsarClient pulsarclient = PulsarClient.builder()
//				.serviceUrl(configuration_info.SERVICE_URL)
//				.build();
//		
//		//2) Create producer
//		Producer<Sensor> sensor_producer = pulsarclient.newProducer(JSONSchema.of(Sensor.class))
//				.producerName("Sensor Producer")
//				.topic("persistent://public/default/Sensors Topic3")
//				.create();
//		
//		System.out.println("Hello world");
//		//3) Create messages
//		double a=0,b=0,c=0,average_a=0,average_b=0,average_c = 0;
//		List<Sensor> sensorList = new ArrayList<>();
//		for (int i = 0; i < 10 ;i++) {
//			a = Math.random();
//			average_a = average_a + a;
//			sensorList.add(new Sensor(1,a));
//			b = Math.random();
//			average_b = average_b + b;
//			sensorList.add(new Sensor(2,b));
//			c = Math.random();
//			average_c = average_c + c;
//			sensorList.add(new Sensor(3,c));
//				long start = System.currentTimeMillis();
//				while (System.currentTimeMillis() - start < 400) {
//	            // Busy-waiting for 0.4 second
//	        } 
////			}
//		}
//		
//		//4) Send messages
//		for (Sensor s: sensorList) {
//			System.out.println(s);
//			sensor_producer.newMessage(JSONSchema.of(Sensor.class))
//			.value(s)
//			.eventTime(s.getSensor_creation_timestamp().getTime())
//			.send();
//		}
//		
//		System.out.println();
//		System.out.println("I have sent all sensor messages");
//		sensor_producer.flush();
//		
//		//5) Close producer and client
//		 System.out.println("Closing producer");
//		 sensor_producer.close();
//		 System.out.println("Closing Pulsar Client");
//		 pulsarclient.close();
//		
//	}
//}
