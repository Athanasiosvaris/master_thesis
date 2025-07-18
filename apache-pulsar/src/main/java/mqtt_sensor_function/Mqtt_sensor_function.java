package mqtt_sensor_function;

import java.io.ByteArrayInputStream;
import java.io.ObjectInputStream;
import com.fasterxml.jackson.databind.ObjectMapper;

import org.apache.pulsar.functions.api.Context;
import org.apache.pulsar.functions.api.Function;
import sensor.Sensor;

public class Mqtt_sensor_function implements Function <byte [],Sensor>{

	private ObjectMapper mapper = new ObjectMapper(); 
	

	@Override
	public Sensor process(byte[] input, Context context) throws Exception {
		
		Sensor sensor = mapper.readValue(input, Sensor.class);
		sensor.setSensor_energy_value(sensor.getSensor_energy_value()/1000);// converting kWatts to Watts
		return sensor;
	}

}
