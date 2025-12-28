package mqttProducerClient_package;

import org.fusesource.mqtt.client.BlockingConnection;
import org.fusesource.mqtt.client.MQTT;
import org.fusesource.mqtt.client.QoS;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.text.DateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.time.*;
import java.time.format.DateTimeFormatter;

public class MqttClientProducerFinal {

	public static void main(String[] args) throws IOException, InterruptedException {
		
		List<List<String>> records = MqttClientProducerFinal.records("device_1_data_manipulated_2025-12-08_2025-12-09.csv", ",");
		List<String> messages = MqttClientProducerFinal.messages(records);			
			
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

			for (int i = 0; i < messages.size(); i++) {
				String message = messages.get(i);
				TimeUnit.SECONDS.sleep(1); //1 seconds delay
				// Publish message
				connection.publish("/home/fridge", message.getBytes(), QoS.AT_LEAST_ONCE, false);
			}
			connection.disconnect();

		} catch (Exception e) {
			e.printStackTrace();
		}

	}
	
	
	//Function that receives as arguments the name of the csv file 
	//and the character that separates the records and returns the records a List<List<String>>
	public static List<List<String>> records (String csvName,String delimeterChar) {
		//final String COMMA_DELIMITER = ",";
		//System.out.println(System.getProperty("user.dir"));
		
		List<List<String>> records = new ArrayList<>();
		
		try (BufferedReader br = new BufferedReader(new FileReader(csvName))) {
			String line;
			while ((line = br.readLine()) != null) {
				String[] values = line.split(delimeterChar);
				records.add(Arrays.asList(values));
			}
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return records;
	}
	
	//function that takes the dataset/records as a List<<List<String>> and
	//returns a list of strings where each String is a message as json. 
	//Example: {"sensor_id":1,"sensor_timestamp":1765152003,"sensor_energy_value":695.3}
	public static List<String> messages (List<List<String>> records) {
		List<String> messages = new ArrayList<>();
		int stop = 0;
		boolean firstRow = true;
		int sensor_id = 0;
		double sensor_energy_value = 0; //aprt_power == sensor_energy_value
		
		LocalDateTime sensor_timestamp = LocalDateTime.now();
		DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss+SS");
		long sensor_timestamp_epong = 0;
		
		for (List<String> record : records) {
			if (firstRow) {
				// Droping the first row
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
				JSONObject json = new JSONObject();
				json.put("sensor_id", sensor_id);
				json.put("sensor_energy_value", sensor_energy_value);
				json.put("sensor_timestamp", sensor_timestamp_epong);
				String jsonString = json.toString();
				//System.out.println(jsonString);
				messages.add(jsonString);
			}
			
			stop++;
			if (stop == 180) //Right now I am only reading the first 180 messages
				break;
		}
		return messages;
	}
}
