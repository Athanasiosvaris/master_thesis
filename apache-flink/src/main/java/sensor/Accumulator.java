package sensor;

public class Accumulator extends Sensor{
	private int count;
	private long accumulator_creation_timestamp;
	
	public Accumulator () {
		super();
	}
	
	public Accumulator (int sensor_id,double sensor_energy_value,long sensor_creation_timestamp,int count) {
		super(sensor_id,sensor_energy_value,sensor_creation_timestamp);
		this.accumulator_creation_timestamp = 0;
		this.count = count;
	}
	
	//Getter
	public int getCount() {
		return this.count;
	}
	
	public long getAccumulator_creation_timestamp () {
		return this.accumulator_creation_timestamp;
	}
	//Setter
	
	public void setCount(int count) {
		this.count = count;
	}
	
	public void setTimestamp (long timestamp) {
		this.accumulator_creation_timestamp = timestamp;
	}
}
