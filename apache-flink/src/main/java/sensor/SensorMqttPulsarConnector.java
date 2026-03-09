package sensor;

import java.time.Duration;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.AggregateFunction;
import org.apache.flink.connector.base.DeliveryGuarantee;
import org.apache.flink.connector.pulsar.sink.PulsarSink;
import org.apache.flink.connector.pulsar.source.PulsarSource;
import org.apache.flink.connector.pulsar.source.enumerator.cursor.StartCursor;
import org.apache.flink.formats.json.JsonDeserializationSchema;
import org.apache.flink.formats.json.JsonSerializationSchema;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows;
//import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.util.Collector;

public class SensorMqttPulsarConnector {

	public static void main(String[] args) throws Exception {
		StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
		System.out.println("App started");
		
		env.enableCheckpointing(5000); //start a checkpoint every 5000 ms (5 seconds)
		
		JsonDeserializationSchema<Sensor> jsonFormatDeserializationSchema=new JsonDeserializationSchema<>(Sensor.class);
		JsonSerializationSchema<Sensor> jsonFormatSerializationSchema = new JsonSerializationSchema<Sensor>();
		
		
		// Pulsar source which reads Sensor type messages from a specific Pulsar topic
		// and brings them into Flink as stream.
		PulsarSource<Sensor> source = PulsarSource.<Sensor>builder()
				.setServiceUrl("pulsar://pulsar:6650")
				.setAdminUrl("http://pulsar:8080")
				.setStartCursor(StartCursor.earliest())
				.setTopics("persistent://public/default/MQTTtopic9")
				.setDeserializationSchema(jsonFormatDeserializationSchema)
				.setSubscriptionName("FlinkSub")
				.setConsumerName("FlinkConsumer").build();

		System.out.println("Pulsar source created");

//		DataStream<Sensor> Data = env.fromSource(source, WatermarkStrategy.<Sensor>noWatermarks(), "Pulsar Source");
//		Data.print();
		//DataStream<Sensor> Data = env.fromSource(source, WatermarkStrategy.<Sensor>forMonotonousTimestamps()
		//		.withTimestampAssigner((event, timestamp) -> event.getSensor_timestamp() * 1000L ).withIdleness(Duration.ofMinutes(1)), "Pulsar Source");

		DataStream<Sensor> Data = env.fromSource(source, WatermarkStrategy.<Sensor>forBoundedOutOfOrderness(Duration.ofSeconds(30))
				.withTimestampAssigner((event, timestamp) ->  event.getSensor_timestamp() * 1000L ) , "Pulsar Source");
		
		
		DataStream <Sensor> result = Data.keyBy(Sensor -> Sensor.getSensor_id())
				.window(TumblingEventTimeWindows.of(Time.minutes(1)))
				.process(new MyProcessWindowFunction());
				
		result.print();
		PulsarSink<Sensor> sink = PulsarSink.<Sensor>builder()
				.setServiceUrl("pulsar://pulsar:6650")
				.setAdminUrl("http://pulsar:8080")
				.setTopics("persistent://public/default/FlinkTopicSinkFinal") // SOS It has to be a partitioned topic
				.setSerializationSchema(jsonFormatSerializationSchema)
				.setDeliveryGuarantee(DeliveryGuarantee.AT_LEAST_ONCE)
				.build();
		
//		SensorAverageValues.sinkTo(sink);
		
		result.sinkTo(sink);
		env.execute();

	}
	
	
	//Function that returns as a datastream/batch all messages that are inside one minute interval
	//e.g. 
	//One batch is all messages beetween 12:00:00.000 - 12:59:59.999,
	public static class MyProcessWindowFunction extends ProcessWindowFunction<Sensor, Sensor, Integer, TimeWindow> {

		private static final long serialVersionUID = 1L;

		@Override
		public void process(Integer key, Context context,Iterable<Sensor> input, Collector<Sensor> out) throws Exception {
			// TODO Auto-generated method stub
			Sensor firstElement = input.iterator().next();
			long firstElementTimestamp = firstElement.getSensor_timestamp();
			long lastElementTimestamp = 0;
			for (Sensor s: input) {
				out.collect(s);
				lastElementTimestamp = s.getSensor_timestamp();
			}
			System.out.println("That was the window beetween " + firstElementTimestamp + " and " + lastElementTimestamp);
			System.out.println();
		}
		
	}
	
	
	public static DataStream<Sensor> avgValuePer1Sec(DataStream<Sensor> stream) {
		DataStream<Sensor> finalStream = stream.keyBy(Sensor -> Sensor.getSensor_id())
				.window(TumblingEventTimeWindows.of(Time.seconds(5))) //5 seconds Tumbling window
				.aggregate(new SensorMqttPulsarConnector.AverrageEnergyValue())
				.map(Accumulator -> new Sensor(Accumulator.getSensor_id(), Accumulator.getSensor_energy_value(),
						Accumulator.getAccumulator_creation_timestamp()));

		return finalStream;

	}
	
	
	public static class AverrageEnergyValue implements AggregateFunction<Sensor, Accumulator, Accumulator> {

		private static final long serialVersionUID = 1L;

		@Override
		public Accumulator createAccumulator() {
			Accumulator accumulator = new Accumulator(0, 0, 0, 0);
			return accumulator;
		}

		@Override
		public Accumulator add(Sensor value, Accumulator accumulator) {
			accumulator.setSensor_id(value.getSensor_id());
			accumulator.setSensor_energy_value(accumulator.getSensor_energy_value() + value.getSensor_energy_value());
			if (accumulator.getAccumulator_creation_timestamp() == 0) {
				accumulator.setTimestamp(value.getSensor_timestamp());
			}
			accumulator.setCount(accumulator.getCount() + 1);
			return accumulator;
		}

		@Override
		public Accumulator getResult(Accumulator accumulator) {
			// Average logic here
			accumulator.setSensor_energy_value(accumulator.getSensor_energy_value() / accumulator.getCount());
			return accumulator;
		}

		@Override
		public Accumulator merge(Accumulator a, Accumulator b) {
			// TODO Auto-generated method stub
			return null;
		}

	}
}
