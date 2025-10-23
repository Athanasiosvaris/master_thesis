package mqttProducerClient_package;

import org.fusesource.mqtt.client.BlockingConnection;
import org.fusesource.mqtt.client.MQTT;
import org.fusesource.mqtt.client.QoS;
import org.json.JSONObject;

import java.sql.Timestamp;
import java.util.concurrent.TimeUnit;

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

			for (int i = 0; i < 10; i++) {
				// Message creation
				double sensor_energy_value = Math.random(); // Sensor energy value in Watts
				long timestamp = System.currentTimeMillis(); // It gives the current time in milliseconds
				
				JSONObject json = new JSONObject();
				json.put("sensor_energy_value", sensor_energy_value);
				json.put("sensor_timestamp", timestamp);
				String jsonString = json.toString();
				TimeUnit.MILLISECONDS.sleep(400); //Delay of 400 ms
				// Publish message
				connection.publish("/home/fridge", jsonString.getBytes(), QoS.AT_LEAST_ONCE, false);
				System.out.println(new Timestamp(timestamp) + " Message sent"); // I want to see the timestamp on date format
			}
			connection.disconnect();

		} catch (

		Exception e) {
			e.printStackTrace();
		}

	}

}
