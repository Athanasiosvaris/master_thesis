package sensor;

import java.sql.Timestamp;

import com.fasterxml.jackson.annotation.JsonProperty;

public class Sensor {
	private int sensor_id;
	private double sensor_energy_value;
	private Timestamp sensor_creation_timestamp;
	
	//Constructors
	public Sensor () {}
	
	public Sensor (int sensor_id,double sensor_energy_value) {
		this.sensor_id = sensor_id;
		this.sensor_energy_value = sensor_energy_value;
		this.sensor_creation_timestamp = new Timestamp(System.currentTimeMillis());
	}
	
	//Getters
	public int getSensor_id () {
		return sensor_id;
	}
	
	public double getSensor_energy_value () {
		return sensor_energy_value;
	}
	
	public Timestamp getSensor_creation_timestamp () {
		return sensor_creation_timestamp;
	}
	
	//Setters
	public void setSensor_id (int sensor_id) {
		this.sensor_id = sensor_id;
	}
	
	public void setSensor_energy_value (double sensor_energy_value) {
		this.sensor_energy_value = sensor_energy_value;
	}
	
	public void setSensor_creation_timestamp () {
	}
	
	@Override
	public String toString() {
		return "Sensor id:" + sensor_id + " Sensor_energy_value: " + sensor_energy_value + " Sensor_creation_timestamp: " + sensor_creation_timestamp;
	}
	
}
