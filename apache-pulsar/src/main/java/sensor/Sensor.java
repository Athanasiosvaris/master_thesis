package sensor;

import java.sql.Timestamp;
import com.fasterxml.jackson.annotation.JsonFormat;

public class Sensor {
	private int sensor_id;
	private double sensor_energy_value;
	private long sensor_timestamp;
	
	//Constructors
	public Sensor () {}
	
	public Sensor (int sensor_id,double sensor_energy_value) {
		this.sensor_id = sensor_id;
		this.sensor_energy_value = sensor_energy_value;
		this.sensor_timestamp = System.currentTimeMillis();
	}
	
	//Getters
	public int getSensor_id () {
		return sensor_id;
	}
	
	public double getSensor_energy_value () {
		return sensor_energy_value;
	}
	
	public long getSensor_timestamp () {
		return sensor_timestamp;
	}
	
	//Setters
	public void setSensor_id (int sensor_id) {
		this.sensor_id = sensor_id;
	}
	
	public void setSensor_energy_value (double sensor_energy_value) {
		this.sensor_energy_value = sensor_energy_value;
	}
	
	public void setSensor_timestamp (long sensor_timestamp) {
		this.sensor_timestamp = sensor_timestamp;
	}
	
	@Override
	public String toString() {
		return "Sensor id:" + sensor_id + " Sensor_energy_value: " + sensor_energy_value + " Sensor_creation_timestamp: " + sensor_timestamp;
	}
	
}
