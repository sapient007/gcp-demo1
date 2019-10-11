package com.ntconcepts.gcpdemo1

import org.apache.beam.runners.dataflow.options.DataflowPipelineOptions
import org.apache.beam.sdk.options.Default
import org.apache.beam.sdk.options.Description
import org.apache.beam.sdk.options.ValueProvider
import java.awt.geom.Point2D

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
    val hotEncodeCompany: ValueProvider<Boolean>

    fun setHotEncodeCompany(hotEncodeCompany: ValueProvider<Boolean>)

    @get:Description("Map of ML partition names and weights. Example {\"train\": 80, \"validation\":20} will partition 80 percent of data for training and 20 percent for validation.")
    val partitionWeights: ValueProvider<HashMap<String, Double>>

    fun setPartitionWeights(partitionWeights: ValueProvider<HashMap<String, Double>>)

    @get:Description("GCS output path for CSV. Example: gs://bucket/path/to/csv")
    val csvOutputPath: ValueProvider<String>

    fun setCsvOutputPath(csvOutputPath: ValueProvider<String>)

    @get:Description("GCS output path for CSV header. Example: gs://bucket/path/to/csv/header")
    val csvHeaderOutputPath: ValueProvider<String>

    fun setCsvHeaderOutputPath(csvHeaderOutputPath: ValueProvider<String>)

    @get:Description("GCS output path for Avro. Example: gs://bucket/path/to/avro")
    val avroOutputPath: ValueProvider<String>

    fun setAvroOutputPath(avroOutputPath: ValueProvider<String>)

    @get:Description("java.awt.geom.Point2D value to center row lat/longs. Example (Chicago City Hall): {\"x\": -87.6319, \"y\":41.8839}")
    val mapCenterPoint: ValueProvider<Point2D.Double>

    fun setMapCenterPoint(mapCenterPoint: ValueProvider<Point2D.Double>)

}
