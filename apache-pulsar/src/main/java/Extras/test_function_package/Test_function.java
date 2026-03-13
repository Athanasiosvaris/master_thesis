package test_function_package;
import java.util.function.Function;

public class Test_function implements Function <String,String>{
	public String apply(String input) {
		return input.toUpperCase();
	}
}
