package mqttClient;


import org.fusesource.mqtt.client.*;
import org.json.JSONObject;

public class MqttClientConsumer {

	public static void main(String[] args) {
		try {
			MQTT mqtt_consumer = new MQTT();
			// Port in which the client will try to connect
			mqtt_consumer.setHost("127.0.0.1", 1884);
			// Client's credentials to connect to MQTT broker
			mqtt_consumer.setUserName("user1");
			mqtt_consumer.setPassword("user1");

			BlockingConnection connection = mqtt_consumer.blockingConnection();
			// Asynchronous method to connect to MQTT broker
			connection.connect();
			if (connection.isConnected())
				System.out.println("Connection establised");
			
			//Publish to Apache Pulsar
			MQTT mqtt_producer = new MQTT();
			// Port in which the client will try to connect
			mqtt_producer.setHost("127.0.0.1", 1883);
			BlockingConnection connection_producer= mqtt_producer.blockingConnection();
			connection_producer.connect();
			if (connection_producer.isConnected()) System.out.println("Connected to MOP");

			// List of topics in which this client (consumer) will connect to
			Topic[] topics = { new Topic("/home/priza_saloni", QoS.AT_LEAST_ONCE) };
			connection.subscribe(topics);
			
			while (true) {
			Message message = connection.receive();
			byte[] payload = message.getPayload();
			String payload_s = new String(payload);
			JSONObject json = new JSONObject (payload_s);
			json.put("sensor_id", 1);
//			System.out.println(json.toString());
			message.ack();
		
			//Adding sensor_id field
			String Pulsar_message = json.toString();
			System.out.println(Pulsar_message);
			
			
			
			//Publish it to Apache Pulsar
			connection_producer.publish("persistent://public/default/MQTTtopic7", Pulsar_message.getBytes(), QoS.AT_LEAST_ONCE, false);
			System.out.println("Hi there");
			}

		} catch (Exception e) {
			e.printStackTrace();
		}

	}

}
