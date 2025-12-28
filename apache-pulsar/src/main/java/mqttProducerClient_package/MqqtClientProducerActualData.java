package mqttProducerClient_package;

import org.fusesource.mqtt.client.BlockingConnection;
import org.fusesource.mqtt.client.MQTT;
import org.fusesource.mqtt.client.QoS;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.text.DateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.time.*;
import java.time.format.DateTimeFormatter;

public class MqqtClientProducerActualData {

	public static void main(String[] args) throws IOException, InterruptedException {
		final String COMMA_DELIMITER = " "; //values are being separated by keno diastima
		//System.out.println(System.getProperty("user.dir"));
		
		List<List<String>> records = new ArrayList<>();
		List<String> messages = new ArrayList<>();

		try (BufferedReader br = new BufferedReader(new FileReader("device_1_manipulated.csv"))) {
			String line;
			while ((line = br.readLine()) != null) {
				String[] values = line.split(COMMA_DELIMITER);
				records.add(Arrays.asList(values));
			}
		}
		
	    
		int stop = 0;
		boolean firstRow = true;
		int sensor_id = 0;
		double sensor_energy_value = 0;
		LocalDateTime sensor_timestamp = LocalDateTime.now();
		DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy:MM:dd HH:mm:ss''SS");
		long sensor_timestamp_epong = 0;
		
		for (List<String> record : records) {
			if (firstRow) {
				// Dropping the first row
				firstRow = false;
				continue;
			} else {

				for (int i = 0; i < record.size(); i++) {
					if (i == 0)
						sensor_id = Integer.parseInt(record.get(i));
					if (i == 1)
						sensor_energy_value = Double.parseDouble(record.get(i)) ;
					if (i == 2) {
						sensor_timestamp = LocalDateTime.parse(record.get(i), formatter);
						sensor_timestamp_epong = sensor_timestamp.toEpochSecond(ZoneOffset.UTC);
					}
						
				}
				
				System.out.println(sensor_id);
				System.out.println(sensor_energy_value);
				System.out.println(sensor_timestamp);
				
				JSONObject json = new JSONObject();
				json.put("sensor_id", sensor_id);
				json.put("sensor_energy_value", sensor_energy_value);
				json.put("sensor_timestamp", sensor_timestamp_epong);
				String jsonString = json.toString();

				messages.add(jsonString);

			}
			
			stop++;
			if (stop == 20)
				break;
		}
		
		int counter = 0;
		/*try {
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

			for (int i = 0; i < messages.size(); i++) {
				String message = messages.get(i);
				TimeUnit.MILLISECONDS.sleep(300); //0.3 seconds delay
				// Publish message
				connection.publish("/home/fridge", message.getBytes(), QoS.AT_LEAST_ONCE, false);
			}
			connection.disconnect();

		} catch (

		Exception e) {
			e.printStackTrace();
		}
*/
	}

}
