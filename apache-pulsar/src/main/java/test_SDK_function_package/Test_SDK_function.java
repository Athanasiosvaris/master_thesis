package test_SDK_function_package;
import org.apache.pulsar.functions.api.*;
import User.*;

public class Test_SDK_function implements Function <User,User> {

	public User process(User input, Context ctx) throws Exception {
		
		User s =  input;
		s.setName("Success");
		s.setAge(100);
		return s; 
	}
}
