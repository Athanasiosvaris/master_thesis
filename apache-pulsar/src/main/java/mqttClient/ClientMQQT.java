package mqttClient;

import java.net.URISyntaxException;
import java.sql.Timestamp;

import org.fusesource.mqtt.client.BlockingConnection;
import org.fusesource.mqtt.client.MQTT;
import org.fusesource.mqtt.client.QoS;

public class ClientMQQT {
	public static void main(String[] args) throws Exception {
		MQTT mqtt = new MQTT();
		mqtt.setHost("127.0.0.1", 1883);
		System.out.println("Hi there");
		try {
			BlockingConnection connection = mqtt.blockingConnection();
			connection.connect();
			System.out.println("Hi there2");
			
			Timestamp timestamp = new Timestamp(System.currentTimeMillis());
			String jsonString = "{"
				    + "\"id\": 1,"
				    + "\"energy-value\": 0.5,"
				    + "\"timestamp\":" + timestamp +" ,"
				    + "}";
			
			// publish message
			connection.publish("persistent://public/default/MQTTtopic", jsonString.getBytes(), QoS.AT_LEAST_ONCE, false);
			connection.disconnect();
		}
		catch (Exception e) {
			System.out.println("Exception :" + e.getMessage());
			e.printStackTrace();
		}
	}
}
