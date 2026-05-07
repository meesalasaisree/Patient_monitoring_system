import os
import sys

# 1. Set HADOOP_HOME to your hadoop folder
os.environ['HADOOP_HOME'] = r'D:\hadoop' 

# 2. Add the bin folder to the system PATH using the correct attribute
# We use os.pathsep (no underscore) which is ';' on Windows
os.environ['PATH'] += os.pathsep + r'D:\hadoop\bin'

# 3. Add to sys.path so Python can find the binaries
sys.path.append(r'D:\hadoop\bin')
from pyspark.sql import SparkSession
from pyspark.ml.classification import RandomForestClassificationModel
from pyspark.ml.feature import VectorAssembler
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType

# 1. Initialize Spark
spark = SparkSession.builder.appName("RealTimeMonitoring").getOrCreate()

# 2. Create the streaming directory if it doesn't exist
os.makedirs('data/stream', exist_ok=True)

# 3. Load the TRAINED model we saved in Step 5
model = RandomForestClassificationModel.load("models/patient_monitor_model")

# 4. Define Schema for incoming streaming data
schema = StructType([
    StructField("patient_id", IntegerType(), True),
    StructField("heart_rate", IntegerType(), True),
    StructField("oxygen_sat", IntegerType(), True),
    StructField("temperature", DoubleType(), True),
    StructField("label", IntegerType(), True)
])

# 5. Read Stream: Spark will watch this folder for NEW CSV files
input_stream = spark.readStream.schema(schema).option("maxFilesPerTrigger", 1).csv("data/stream")

# 6. Pre-process the stream (Vectorize)
assembler = VectorAssembler(
    inputCols=['heart_rate', 'oxygen_sat', 'temperature'], 
    outputCol='features', 
    handleInvalid="skip"  # This will ignore rows with missing data instead of crashing
)
stream_features = assembler.transform(input_stream)

# 7. Use the model to predict in real-time
predictions = model.transform(stream_features)
from alerts import send_email_alert

def send_patient_alert(batch_df, batch_id):
    critical_df = batch_df.filter(batch_df.prediction == 1.0)
    
    if not critical_df.isEmpty():
        # Get the first critical patient (Throttling)
        top_patient = critical_df.limit(1).collect()[0]
        
        # Trigger the Email Alert
        send_email_alert(
            top_patient['patient_id'], 
            top_patient['heart_rate'], 
            top_patient['oxygen_sat']
        )
# 8. Output the results using 'foreachBatch'
query = predictions.select("patient_id", "heart_rate", "oxygen_sat", "prediction") \
    .writeStream \
    .foreachBatch(send_patient_alert) \
    .start()

print("Monitoring System Active... Waiting for data in data/stream/")

# THIS LINE IS CRITICAL - It keeps the script running!
query.awaitTermination()