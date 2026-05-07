import os
import sys

# CHANGE THIS: Point to the folder ABOVE bin
os.environ['HADOOP_HOME'] = r'D:\hadoop' 

# This adds the actual bin folder to the PATH for the DLLs
os.environ['PATH'] += os.pathsep + os.path.join(os.environ['HADOOP_HOME'], 'bin')
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# 1. Initialize Spark
spark = SparkSession.builder.appName("PatientMonitoringSystem").getOrCreate()

# 2. Load Data (Same as before)
schema = StructType([
    StructField("patient_id", IntegerType(), True),
    StructField("heart_rate", IntegerType(), True),
    StructField("oxygen_sat", IntegerType(), True),
    StructField("temperature", DoubleType(), True),
    StructField("label", IntegerType(), True)
])
df = spark.read.csv("data/patient_vitals.csv", header=True, schema=schema)

# 3. Vectorization (Same as before)
assembler = VectorAssembler(inputCols=['heart_rate', 'oxygen_sat', 'temperature'], outputCol='features')
transformed_data = assembler.transform(df)
(training_data, test_data) = transformed_data.randomSplit([0.8, 0.2], seed=42)

# 4. Initialize the Model
# We tell it which column is the feature and which is the target (label)
rf = RandomForestClassifier(featuresCol='features', labelCol='label')

# 5. Train the Model
print("Training the model... please wait.")
model = rf.fit(training_data)

# 6. Make Predictions on the Test Data
predictions = model.transform(test_data)

# 7. Evaluate Accuracy
evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)

print(f"--- Model Results ---")
print(f"Test Accuracy: {accuracy * 100:.2f}%")
predictions.select("patient_id", "label", "prediction", "probability").show(5)

# 8. Save the Model (to use it later for real-time deployment)
model.write().overwrite().save("models/patient_monitor_model")
print("Model saved to models/patient_monitor_model")

spark.stop()