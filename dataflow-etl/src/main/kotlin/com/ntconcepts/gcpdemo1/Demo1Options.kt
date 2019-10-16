package com.ntconcepts.gcpdemo1

import org.apache.beam.runners.dataflow.options.DataflowPipelineOptions
import org.apache.beam.sdk.options.Default
import org.apache.beam.sdk.options.Description
import org.apache.beam.sdk.options.ValueProvider

interface Demo1Options : DataflowPipelineOptions {

    @get:Description("Bigquery output dataset")
    val outputDataset: ValueProvider<String>

    fun setOutputDataset(dataset: ValueProvider<String>)

    @get:Description("Bigquery output table")
    val outputTable: ValueProvider<String>

    fun setOutputTable(table: ValueProvider<String>)

    @get:Description("Bigquery output tablespec. Example: project_id:dataset.table")
    val outputTableSpec: ValueProvider<String>

    fun setOutputTableSpec(outputTableSpec: ValueProvider<String>)

    @get:Description("Bigquery input tablespec. Example: bigquery-public-data:chicago_taxi_trips.taxi_trips")
    @get:Default.String("bigquery-public-data:chicago_taxi_trips.taxi_trips")
    val inputTableSpec: ValueProvider<String>

    fun setinputTableSpec(inputTableSpec: ValueProvider<String>)

    @get:Description("Drop output table when job starts")
    @get:Default.Boolean(true)
    val dropTable: ValueProvider<Boolean>

    fun setDropTable(dropTable: ValueProvider<Boolean>)

    @get:Description("One-hot-encode company field")
    @get:Default.Boolean(false)
    val hotEncodeCompany: ValueProvider<Boolean>

    fun setHotEncodeCompany(hotEncodeCompany: ValueProvider<Boolean>)

    @get:Description("Weight to apply to random partitioning of training data. Example: 70 for 70 percent. Default: 70.0")
    @get:Default.Double(70.0)
    val mlPartitionTrainWeight: ValueProvider<Double>

    fun setMlPartitionTrainWeight(mlPartitionTrainWeight: ValueProvider<Double>)

    @get:Description("Weight to apply to random partitioning of testing data. Example: 15 for 15 percent. Default: 15.0")
    @get:Default.Double(15.0)
    val mlPartitionTestWeight: ValueProvider<Double>

    fun setMlPartitionTestWeight(mlPartitionTestWeight: ValueProvider<Double>)

    @get:Description("Weight to apply to random partitioning of validation data. Example: 15 for 15 percent. Default: 15.0")
    @get:Default.Double(15.0)
    val mlPartitionValidationWeight: ValueProvider<Double>

    fun setMlPartitionValidationWeight(mlPartitionValidationWeight: ValueProvider<Double>)

    @get:Description("Number of CSV shards to create. Example: 30 for 30 files. Default: 30")
    @get:Default.Integer(30)
    val csvShards: ValueProvider<Int>

    fun setCsvShards(csvShards: ValueProvider<Int>)

    @get:Description("GCS output path for CSV. Example: gs://bucket/path/to/csv/")
    val csvOutputPath: ValueProvider<String>

    fun setCsvOutputPath(csvOutputPath: ValueProvider<String>)

    @get:Description("GCS output path for CSV header. Example: gs://bucket/path/to/csv/header")
    val csvHeaderOutputPath: ValueProvider<String>

    fun setCsvHeaderOutputPath(csvHeaderOutputPath: ValueProvider<String>)

    @get:Description("GCS output path for Avro. Example: gs://bucket/path/to/avro/")
    @get:Default.String("")
    val avroOutputPath: ValueProvider<String>

    fun setAvroOutputPath(avroOutputPath: ValueProvider<String>)

    @get:Description("Latitude in radians to center row latitude values on. Example: 41.8839. Default: 41.8839 (Chicago City Hall)")
    @get:Default.Double(41.8839)
    val mapCenterLat: ValueProvider<Double>

    fun setMapCenterLat(mapCenterLat: ValueProvider<Double>)

    @get:Description("Longitude in radians to center row latitude values on. Example: -87.6319. Default: -87.6319 (Chicago City Hall)")
    @get:Default.Double(-87.6319)
    val mapCenterLong: ValueProvider<Double>

    fun setMapCenterLong(mapCenterLong: ValueProvider<Double>)

    @get:Description("Percent of data to sample. Example: 0-100. Default: 100")
    @get:Default.Integer(100)
    val sampleSize: ValueProvider<Int>

    fun setSampleSize(sampleSize: ValueProvider<Int>)
}
