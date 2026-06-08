package mqttProducerClient_package;

import org.fusesource.mqtt.client.BlockingConnection;
import org.fusesource.mqtt.client.MQTT;
import org.fusesource.mqtt.client.QoS;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.TimeUnit;

public class MqttProducerBatches {

	public static void main(String[] args) throws IOException, InterruptedException {

		if (args.length < 2) {
			System.err.println("Usage: MqttProducerBatches <path-to-csv> <mqtt-topic>");
			System.exit(1);
		}
		List<List<String>> records = MqttProducerBatches.records(args[0], ",");
		List<String> messages = MqttProducerBatches.messages(records);

		try {
			MQTT mqtt = new MQTT();
			mqtt.setHost("127.0.0.1", 1884);
			mqtt.setUserName("user1");
			mqtt.setPassword("user1");
			System.out.println("Connecting...");
			BlockingConnection connection = mqtt.blockingConnection();
			connection.connect();
			if (connection.isConnected())
				System.out.println("Connection establised");

			for (int i = 0; i < messages.size(); i++) {
				TimeUnit.SECONDS.sleep(1); //1 seconds delay
				// Stamp message_creation_time right before publishing so latency reflects
				// the actual publish moment.
				JSONObject json = new JSONObject(messages.get(i));
				json.put("message_creation_time", Instant.now().toEpochMilli());
				connection.publish(args[1], json.toString().getBytes(), QoS.AT_LEAST_ONCE, false);
			}
			connection.disconnect();

		} catch (Exception e) {
			e.printStackTrace();
		}
	}


	public static List<List<String>> records (String csvName, String delimeterChar) {
		List<List<String>> records = new ArrayList<>();

		try (BufferedReader br = new BufferedReader(new FileReader(csvName))) {
			String line;
			while ((line = br.readLine()) != null) {
				String[] values = line.split(delimeterChar);
				records.add(Arrays.asList(values));
			}
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return records;
	}

	// Expected CSV column order: sensor_id, aprt_power, sensor_timestamp (with +00 suffix).
	public static List<String> messages (List<List<String>> records) {
		List<String> messages = new ArrayList<>();
		boolean firstRow = true;
		int sensor_id = 0;
		double sensor_energy_value = 0;

		LocalDateTime sensor_timestamp = LocalDateTime.now();
		DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss+SS");
		long sensor_timestamp_epong = 0;

		for (List<String> record : records) {
			if (firstRow) {
				firstRow = false;
				continue;
			}
			for (int i = 0; i < record.size(); i++) {
				if (i == 0)
					sensor_id = Integer.parseInt(record.get(i));
				if (i == 1)
					sensor_energy_value = Double.parseDouble(record.get(i));
				if (i == 2) {
					sensor_timestamp = LocalDateTime.parse(record.get(i), formatter);
					sensor_timestamp_epong = sensor_timestamp.toEpochSecond(ZoneOffset.UTC);
				}
			}

			// message_creation_time is stamped in the publish loop, not here.
			JSONObject json = new JSONObject();
			json.put("sensor_id", sensor_id);
			json.put("sensor_energy_value", sensor_energy_value);
			json.put("sensor_timestamp", sensor_timestamp_epong);
			messages.add(json.toString());
		}
		return messages;
	}
}
