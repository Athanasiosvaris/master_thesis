package sink_connector_exaple;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Map;

import org.apache.pulsar.functions.api.Record;
import org.apache.pulsar.io.core.Sink;
import org.apache.pulsar.io.core.SinkContext;

public class LocalFileSinnk implements Sink <String>{

	private String prefix,suffix;
	private BufferedWriter bw = null;
	private FileWriter fw = null;
	
	@Override
	public void open(Map<String, Object> config, SinkContext sinkContext) throws Exception {
		// TODO Auto-generated method stub
		prefix = (String) config.getOrDefault("filenamePrefix", "test-out");
		suffix = (String) config.getOrDefault("filenameSuffix", ".tmp");
		
		File file = File.createTempFile(prefix, suffix);
		fw = new FileWriter(file.getAbsoluteFile(),true);
		bw = new BufferedWriter(fw);
	}

	@Override
	public void write(Record<String> record) throws Exception {
		// TODO Auto-generated method stub
		try {
			bw.write(record.getValue());
			bw.flush();
			record.ack();
		}
		catch (IOException e) {
			record.fail(); 
			throw new RuntimeException(e);
		}
	}
	
	@Override
	public void close() throws Exception {
		// TODO Auto-generated method stub
		try {
			if ( bw!= null)
				bw.close();
			if (fw != null)
				fw.close();
			} 
		catch (IOException ex) {
			ex.printStackTrace();
		}
	}
	
}
