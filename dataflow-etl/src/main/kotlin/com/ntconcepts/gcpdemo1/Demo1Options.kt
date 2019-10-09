package com.ntconcepts.gcpdemo1

import org.apache.beam.runners.dataflow.options.DataflowPipelineOptions
import org.apache.beam.sdk.options.ValueProvider
import java.awt.geom.Point2D

interface Demo1Options : DataflowPipelineOptions {
    val dataset: ValueProvider<String>
    fun setDataset(dataset: ValueProvider<String>)
    val table: ValueProvider<String>
    fun setTable(table: ValueProvider<String>)
    val outputTableSpec: ValueProvider<String>
    fun setOutputTableSpec(outputTableSpec: ValueProvider<String>)
    val dropTable: ValueProvider<Boolean>
    fun setDropTable(dropTable: ValueProvider<Boolean>)
    val hotEncodeCompany: ValueProvider<Boolean>
    fun setHotEncodeCompany(hotEncodeCompany: ValueProvider<Boolean>)
    val partitionWeights: ValueProvider<HashMap<String, Double>>
    fun setPartitionWeights(partitionWeights: ValueProvider<HashMap<String, Double>>)
    val csvOutputPath: ValueProvider<String>
    fun setCsvOutputPath(csvOutputPath: ValueProvider<String>)
    val parquetOutputPath: ValueProvider<String>
    fun setParquetOutputPath(parquetOutputPath: ValueProvider<String>)
    val avroOutputPath: ValueProvider<String>
    fun setAvroOutputPath(avroOutputPath: ValueProvider<String>)

    //Business logic
    val mapCenterPoint: ValueProvider<Point2D.Double>

    fun setMapCenterPoint(mapCenterPoint: ValueProvider<Point2D.Double>)

}
