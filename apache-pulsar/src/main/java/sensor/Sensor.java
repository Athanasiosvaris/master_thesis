package sensor;

public class Sensor {
	//private int recordId;
	private Integer sensor_id;
	private Double sensor_energy_value;
	private Long sensor_timestamp; //epoch seconds
	private Long message_creation_time; //epoch milliseconds

	//Constructors
	public Sensor () {}

	public Sensor (Integer sensor_id, Double sensor_energy_value, Long sensor_timestamp, Long message_creation_time) {
		this.sensor_id = sensor_id;
		this.sensor_energy_value = sensor_energy_value;
		this.sensor_timestamp = sensor_timestamp;
		this.message_creation_time = message_creation_time;
	}

	//Getters
	public Integer getSensor_id () {
		return sensor_id;
	}

	public Double getSensor_energy_value () {
		return sensor_energy_value;
	}

	public Long getSensor_timestamp () {
		return sensor_timestamp;
	}

	public Long getMessage_creation_time() {
		return message_creation_time;
	}

	//Setters
	public void setSensor_id (Integer sensor_id) {
		this.sensor_id = sensor_id;
	}

	public void setSensor_energy_value (Double sensor_energy_value) {
		this.sensor_energy_value = sensor_energy_value;
	}

	public void setSensor_timestamp (Long sensor_timestamp) {
		this.sensor_timestamp = sensor_timestamp;
	}
	
	public void setMessage_creation_time(Long message_creation_time) {
		this.message_creation_time = message_creation_time;
	}

	@Override
	public String toString() {
		return "Sensor id:" + sensor_id + " Sensor_energy_value:" + sensor_energy_value + " Sensor_creation_timestamp:" + sensor_timestamp + " Message_creation_time:" + message_creation_time;
	}
	
}
