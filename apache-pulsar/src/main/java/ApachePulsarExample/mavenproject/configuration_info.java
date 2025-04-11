package ApachePulsarExample.mavenproject;

public class configuration_info {
	public static final String SERVICE_HTTP_URL = "http://localhost:8080"; //adminUrl
    public static final String SERVICE_URL      = "pulsar://localhost:6650"; 
    public static final String INPUT_FILE_PATH  = "/src/main/resources/datasets/stock_ticker.csv";
    //"/sn-examples/src/main/resources/datasets/stock_ticker.csv";
    public static final String singleTopic      = "stock-tickers";
}
