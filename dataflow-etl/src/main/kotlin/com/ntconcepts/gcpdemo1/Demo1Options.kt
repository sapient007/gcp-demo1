package com.ntconcepts.gcpdemo1

import org.apache.beam.runners.dataflow.options.DataflowPipelineOptions
import org.apache.beam.sdk.options.ValueProvider

interface Demo1Options : DataflowPipelineOptions {
    val dataset: ValueProvider<String>
    fun setDataset(dataset: ValueProvider<String>)
    val table: ValueProvider<String>
    fun setTable(table: ValueProvider<String>)
    val dropTable: ValueProvider<Boolean>
    fun setDropTable(dropTable: ValueProvider<Boolean>)
}