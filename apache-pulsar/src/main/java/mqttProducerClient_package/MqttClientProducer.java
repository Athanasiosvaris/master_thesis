package mqttProducerClient_package;

import java.sql.Timestamp;

import org.fusesource.mqtt.client.BlockingConnection;
import org.fusesource.mqtt.client.MQTT;
import org.fusesource.mqtt.client.QoS;

public class MqttClientProducer {

	public static void main(String[] args) {
		try {
			MQTT mqtt = new MQTT();
			// Port in which the client will try to connect
			mqtt.setHost("127.0.0.1", 1884);
			// Client's credentials to connect to MQTT broker
			mqtt.setUserName("user1");
			mqtt.setPassword("user1");

			BlockingConnection connection = mqtt.blockingConnection();
			// Asynchronous method to connect to MQTT broker
			connection.connect();
			if (connection.isConnected())
				System.out.println("Connection establised");

			// Message creation
			double sensor_energy_value = Math.random(); // Sensor energy value in kWatts
			Timestamp timestamp = new Timestamp(System.currentTimeMillis());

			String jsonString = "{" + "\"sensor_energy_value\": " + sensor_energy_value + ","
					+ "\"sensor_creation_timestamp\": \"" + timestamp + "\"" + "}";

			// Publish message
			connection.publish("/home/priza_saloni", jsonString.getBytes(), QoS.AT_LEAST_ONCE, false);
			System.out.println("Message sent");
			connection.disconnect();

		} catch (Exception e) {
			e.printStackTrace();
		}

	}

}
