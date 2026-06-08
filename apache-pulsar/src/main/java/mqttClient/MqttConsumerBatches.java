package mqttClient;

import org.fusesource.mqtt.client.BlockingConnection;
import org.fusesource.mqtt.client.MQTT;
import org.fusesource.mqtt.client.Message;
import org.fusesource.mqtt.client.QoS;
import org.fusesource.mqtt.client.Topic;

public class MqttConsumerBatches {

	public static void main(String[] args) {
		if (args.length < 1) {
			System.err.println("Usage: MqttConsumerBatches <mqtt-topic>");
			System.exit(1);
		}

		// Two MQTT clients: one subscribes to Mosquitto, one publishes to Pulsar (MOP).
		try {
			MQTT mqtt_consumer = new MQTT();
			mqtt_consumer.setHost("127.0.0.1", 1884);
			mqtt_consumer.setUserName("user1");
			mqtt_consumer.setPassword("user1");

			BlockingConnection mosquito_connection = mqtt_consumer.blockingConnection();
			mosquito_connection.connect();
			if (mosquito_connection.isConnected())
				System.out.println("Mosquito connection establised");

			Topic[] topics = { new Topic(args[0], QoS.AT_LEAST_ONCE) };
			mosquito_connection.subscribe(topics);

			MQTT mqtt_producer = new MQTT();
			mqtt_producer.setHost("127.0.0.1", 1883);
			BlockingConnection mop_connection = mqtt_producer.blockingConnection();
			mop_connection.connect();
			if (mop_connection.isConnected())
				System.out.println("Connected to MOP");

			while (true) {
				Message message = mosquito_connection.receive();
				message.ack();
				byte[] payload = message.getPayload();
				String Pulsar_message = new String(payload);
				System.out.println(Pulsar_message);

				mop_connection.publish("persistent://public/default/" + args[0],
						Pulsar_message.getBytes(), QoS.AT_LEAST_ONCE, false);
			}

		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}
