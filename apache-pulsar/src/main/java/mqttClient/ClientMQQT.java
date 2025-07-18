package mqttClient;

import java.sql.Timestamp;
import org.fusesource.mqtt.client.*;


public class ClientMQQT {
	public static void main(String[] args) throws Exception {
		MQTT mqtt = new MQTT();
//		mqtt.setHost("127.0.0.1", 1883);
		//In which port to try to connect
		mqtt.setHost("127.0.0.1",1884);
		//Credentials of the connection
		mqtt.setUserName("user1");
		mqtt.setPassword("user1");
		
		try {
			BlockingConnection connection = mqtt.blockingConnection();
			connection.connect();
			//for (int i = 0; i < 100 ; i++) {
			
			Timestamp timestamp = new Timestamp(System.currentTimeMillis());
			
			//Sensor energy value in kWatts
			
//			int sensor_id = (int) ((Math.random() * 10) / 3);
//			if (sensor_id == 0) sensor_id = sensor_id + 1 ; // Sensor_id between 1 and 3
//			double sensor_energy_value = Math.random();
//			
//			String jsonString = "{"
//				    + "\"sensor_id\": \"" + sensor_id + "\","
//				    + "\"sensor_energy_value\": \"" + sensor_energy_value + "\","
//				    + "\"sensor_creation_timestamp\": \"" + timestamp + "\""
//				    + "}";
			
			// publish message
			//connection.publish("persistent://public/default/MQTTtopic7", jsonString.getBytes(), QoS.AT_LEAST_ONCE, false);
			connection.publish("test", "Hi".getBytes(), QoS.AT_LEAST_ONCE, true);
			
			//Subscribe to all the topics of the list
			Topic[] topics = {new Topic("test", QoS.AT_LEAST_ONCE)};
			byte[] qoses = connection.subscribe(topics);
			//Receive message from each topic you have subscribed
			Message message =  connection.receive();
			System.out.println(message.getTopic());
			byte[] payload = message.getPayload();
			System.out.println(new String(payload));
			
			//Acknowledge the message
			message.ack();
			//}
			connection.disconnect();
		}
		catch (Exception e) {
			System.out.println("Exception :" + e.getMessage());
			e.printStackTrace();
		}
	}
}
