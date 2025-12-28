package sensor;

import org.apache.pulsar.client.admin.PulsarAdmin;
import org.apache.pulsar.client.admin.PulsarAdminException;
import org.apache.pulsar.client.admin.Schemas;
import org.apache.pulsar.client.api.PulsarClientException;
import org.apache.pulsar.common.protocol.schema.PostSchemaPayload;
import org.apache.pulsar.common.schema.SchemaInfo;


/**
 * This class connects to Apache Pulsar Admin,
 * retrieves the existing schema of a topic,
 * deletes it, and creates a new AVRO schema
 * without the recordId field.
 * 
 * References : https://pulsar.apache.org/docs/4.1.x/admin-api-schemas/#upload-a-schema
 */


public class SensorSchemaManipulation {
	
	public static void main(String[] args) throws PulsarClientException, PulsarAdminException {
	
		PulsarAdmin admin =  PulsarAdmin.builder().
				serviceHttpUrl("http://localhost:8080").
				build();
		
		Schemas sh = admin.schemas();
		SchemaInfo si;
		String topicName = "persistent://public/default/FlinkTopicSinkFinal2";
		System.out.println("Old topic schema");
		try {
			si = sh.getSchemaInfo(topicName);
			System.out.println(si);
		} catch (Exception e) {
			System.out.println("Couldn't receive the existing schema.");
			System.out.println(e.getStackTrace());
			System.out.println("Program continues to run");
		}
		
		try {
			System.out.println("Deleting the schema");
			sh.deleteSchema(topicName);
		} catch (Exception e) {
			System.out.println("Couldn't delete the existing schema.");
			System.out.println(e.getStackTrace());
			System.out.println("Program continues to run");
		}
			
		
		PostSchemaPayload payload = new PostSchemaPayload();
		payload.setType("AVRO");
		//String oldSchema = "{ \"type\": \"record\", \"name\": \"Sensor\", \"namespace\": \"sensor\", \"fields\": [ { \"name\": \"recordId\", \"type\": \"int\" }, { \"name\": \"sensor_energy_value\", \"type\": \"double\" }, { \"name\": \"sensor_id\", \"type\": \"int\" }, { \"name\": \"sensor_timestamp\", \"type\": \"long\" } ] }";
		String newSchema = "{ \"type\": \"record\", \"name\": \"Sensor\", \"namespace\": \"sensor\", \"fields\": [ { \"name\": \"sensor_energy_value\", \"type\": \"double\" }, { \"name\": \"sensor_id\", \"type\": \"int\" }, { \"name\": \"sensor_timestamp\", \"type\": \"long\" } ] }";

		payload.setSchema(newSchema);
		sh.createSchema(topicName, payload);
		
		System.out.println("New topic's schema");
		si = sh.getSchemaInfo(topicName);
		System.out.println(si);
		
		
		admin.close();
		}

}
