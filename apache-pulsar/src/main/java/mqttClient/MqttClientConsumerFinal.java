package mqttClient;

import org.fusesource.mqtt.client.*;
import org.json.JSONObject;

public class MqttClientConsumerFinal {

	public static void main(String[] args) {
		// Here I have 2 MQTT clients. One which connects to mosquito and acts as a
		// consumer.

		// The 2nd client connects to MOP and publishes the message to Apache Pulsar.
		try {
			// Mosquito client
			MQTT mqtt_consumer = new MQTT();
			// Port in which the client will try to connect
			mqtt_consumer.setHost("127.0.0.1", 1884);
			// Client's credentials to connect to MQTT broker
			mqtt_consumer.setUserName("user1");
			mqtt_consumer.setPassword("user1");

			BlockingConnection mosquito_connection = mqtt_consumer.blockingConnection();
			// Asynchronous method to connect to MQTT broker
			mosquito_connection.connect();
			if (mosquito_connection.isConnected())
				System.out.println("Mosquito connection establised");

			// List of topics in which this client (consumer) will connect to
			Topic[] topics = { new Topic("/home/fridge", QoS.AT_LEAST_ONCE) };
			mosquito_connection.subscribe(topics);

			// Apache Pulsar (MOP) Client
			MQTT mqtt_producer = new MQTT();
			mqtt_producer.setHost("127.0.0.1", 1883);
			BlockingConnection mop_connection = mqtt_producer.blockingConnection();
			mop_connection.connect();
			if (mop_connection.isConnected())
				System.out.println("Connected to MOP");

			// It runs forever.
			// Converts the message from bytes -> String -> Publishes to Pulsar.

			while (true) {
				Message message = mosquito_connection.receive();
				message.ack();
				byte[] payload = message.getPayload();
				String Pulsar_message = new String(payload);
				System.out.println(Pulsar_message);

				// Publish it to Apache Pulsar
				mop_connection.publish("persistent://public/default/MQTTtopic9", Pulsar_message.getBytes(),QoS.AT_LEAST_ONCE, false);
			}

		} catch (Exception e) {
			e.printStackTrace();
		}

	}

}
