package sensor;

import java.sql.Timestamp;

public class Sensor {
	private int sensor_id;
	private double sensor_energy_value;
	private long sensor_timestamp;
	
	//Constructors
	public Sensor () {}
	
	public Sensor (int sensor_id,double sensor_energy_value,long sensor_timestamp) {
		this.sensor_id = sensor_id;
		this.sensor_energy_value = sensor_energy_value;
		this.sensor_timestamp = sensor_timestamp;
	}
	
	//Getters
	public int getSensor_id () {
		return sensor_id;
	}
	
	public double getSensor_energy_value () {
		return sensor_energy_value;
	}
	
	public long getSensor_timestamp  () {
		return sensor_timestamp;
	}
	
	//Setters
	void setSensor_id (int sensor_id) {
		this.sensor_id = sensor_id;
	}
	
	void setSensor_energy_value(double sensor_energy_value) {
		this.sensor_energy_value = sensor_energy_value;
	}
	
	void setSensor_timestamp (long timestamp) {
		this.sensor_timestamp = timestamp;
	}
	
	@Override
	public String toString() {
		return "Sensor id:" + sensor_id + " Sensor_energy_value: " + sensor_energy_value + " sensor_timestamp: " + sensor_timestamp; //new Timestamp(sensor_timestamp) ;
	}
}
