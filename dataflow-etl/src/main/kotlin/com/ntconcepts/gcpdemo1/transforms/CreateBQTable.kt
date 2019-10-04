package com.ntconcepts.gcpdemo1.transforms

import com.google.cloud.bigquery.*
import com.ntconcepts.gcpdemo1.OneHotSchemaWrapper
import org.apache.beam.sdk.options.ValueProvider
import org.apache.beam.sdk.transforms.DoFn
import org.apache.beam.sdk.values.PBegin
import org.apache.beam.sdk.values.PCollectionView
import org.apache.beam.sdk.values.PDone

class CreateBQTable(
    val dataset: ValueProvider<String>,
    val table: ValueProvider<String>,
    val dropTable: ValueProvider<Boolean>,
    val dayOfWeekView: PCollectionView<List<String>>,
    val monthView: PCollectionView<List<String>>) :
    DoFn<Boolean, Void>() {

    lateinit var bigquery: BigQuery

    private fun initBq() {
        if (!::bigquery.isInitialized) {
            bigquery = BigQueryOptions.getDefaultInstance().service
        }
    }

    @ProcessElement
    fun apply(c: ProcessContext) {
        initBq()
        val tableId = TableId.of(dataset.get(), table.get())
        if (dropTable.get()) {
            bigquery.delete(tableId)
        }
        val dayOfWeekView = c.sideInput(dayOfWeekView)
        val monthView = c.sideInput(monthView)
        val schema = getTransformSchema(
            OneHotSchemaWrapper(dayOfWeekView, StandardSQLTypeName.INT64),
            OneHotSchemaWrapper(monthView, StandardSQLTypeName.INT64)
        )
        val tableDefinition = StandardTableDefinition.of(schema)
        bigquery.create(TableInfo.of(tableId, tableDefinition))


    }

    private fun getTransformSchema(vararg keys: OneHotSchemaWrapper): Schema {

        val fields = ArrayList<Field>()
        fields.add(Field.newBuilder("cash",
            StandardSQLTypeName.INT64).setMode(Field.Mode.REQUIRED).build())
        fields.add(Field.newBuilder("year",
            StandardSQLTypeName.INT64).setMode(Field.Mode.REQUIRED).build())
        fields.add(Field.newBuilder("start_time",
            StandardSQLTypeName.FLOAT64).setMode(Field.Mode.REQUIRED).build())
        fields.add(Field.newBuilder("trip_miles",
            StandardSQLTypeName.FLOAT64).setMode(Field.Mode.REQUIRED).build())
        fields.add(Field.newBuilder("pickup_latitude",
            StandardSQLTypeName.FLOAT64).setMode(Field.Mode.REQUIRED).build())
        fields.add(Field.newBuilder("pickup_longitude",
            StandardSQLTypeName.FLOAT64).setMode(Field.Mode.REQUIRED).build())

        keys.forEach {
            val bqType = it.bqType
            it.keys.forEach {
                fields.add(Field.newBuilder(it,
                    bqType).setMode(Field.Mode.REQUIRED).build())
            }
        }

        return Schema.of(fields)
    }

}