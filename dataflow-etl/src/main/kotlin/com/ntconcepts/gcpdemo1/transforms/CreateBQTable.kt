package com.ntconcepts.gcpdemo1.transforms

import com.google.cloud.bigquery.*
import com.ntconcepts.gcpdemo1.OneHotSchemaWrapper
import org.apache.beam.sdk.options.ValueProvider
import org.apache.beam.sdk.transforms.DoFn
import org.apache.beam.sdk.values.PCollectionView

class CreateBQTable(
    val dataset: ValueProvider<String>,
    val table: ValueProvider<String>,
    val dropTable: ValueProvider<Boolean>,
    val dayOfWeekView: PCollectionView<List<String>>,
    val monthView: PCollectionView<List<String>>,
    val companiesView: PCollectionView<List<String>>
) :
    DoFn<Boolean, Void>() {

    lateinit var bigquery: BigQuery

    @Setup
    fun setup() {
        if (!::bigquery.isInitialized) {
            bigquery = BigQueryOptions.getDefaultInstance().service
        }
    }

    @ProcessElement
    fun apply(c: ProcessContext) {
        val tableId = TableId.of(dataset.get(), table.get())
        if (dropTable.get()) {
            bigquery.delete(tableId)
        }
        val daysOfWeek = c.sideInput(dayOfWeekView)
        val months = c.sideInput(monthView)
        val companies = prefixCompanies(c.sideInput(companiesView))
        val schema = getTransformSchema(
            OneHotSchemaWrapper(daysOfWeek, StandardSQLTypeName.INT64),
            OneHotSchemaWrapper(months, StandardSQLTypeName.INT64),
            OneHotSchemaWrapper(companies, StandardSQLTypeName.INT64)
        )
        val tableDefinition = StandardTableDefinition.of(schema)
        bigquery.create(TableInfo.of(tableId, tableDefinition))

    }

    //Add column prefix to cleaned company values
    private fun prefixCompanies(cs: List<String>): List<String> {
        var new = arrayListOf<String>()
        cs.forEach {
            new.add(it)
        }
        return new
    }

    private fun getTransformSchema(vararg keys: OneHotSchemaWrapper): Schema {

        val fields = ArrayList<Field>()
        fields.add(
            Field.newBuilder(
                "cash",
                StandardSQLTypeName.INT64
            ).setMode(Field.Mode.REQUIRED).build()
        )
        fields.add(
            Field.newBuilder(
                "year",
                StandardSQLTypeName.INT64
            ).setMode(Field.Mode.REQUIRED).build()
        )
        fields.add(
            Field.newBuilder(
                "start_time",
                StandardSQLTypeName.TIMESTAMP
            ).setMode(Field.Mode.REQUIRED).build()
        )
        fields.add(
            Field.newBuilder(
                "trip_miles",
                StandardSQLTypeName.FLOAT64
            ).setMode(Field.Mode.REQUIRED).build()
        )
        fields.add(
            Field.newBuilder(
                "company",
                StandardSQLTypeName.STRING
            ).setMode(Field.Mode.REQUIRED).build()
        )
        fields.add(
            Field.newBuilder(
                "ml_partition",
                StandardSQLTypeName.STRING
            ).setMode(Field.Mode.REQUIRED).build()
        )
        fields.add(
            Field.newBuilder(
                "pickup_latitude",
                StandardSQLTypeName.FLOAT64
            ).setMode(Field.Mode.REQUIRED).build()
        )
        fields.add(
            Field.newBuilder(
                "pickup_longitude",
                StandardSQLTypeName.FLOAT64
            ).setMode(Field.Mode.REQUIRED).build()
        )
        fields.add(
            Field.newBuilder(
                "pickup_lat_norm",
                StandardSQLTypeName.FLOAT64
            ).setMode(Field.Mode.REQUIRED).build()
        )
        fields.add(
            Field.newBuilder(
                "pickup_long_norm",
                StandardSQLTypeName.FLOAT64
            ).setMode(Field.Mode.REQUIRED).build()
        )
        fields.add(
            Field.newBuilder(
                "pickup_lat_std",
                StandardSQLTypeName.FLOAT64
            ).setMode(Field.Mode.REQUIRED).build()
        )
        fields.add(
            Field.newBuilder(
                "pickup_long_std",
                StandardSQLTypeName.FLOAT64
            ).setMode(Field.Mode.REQUIRED).build()
        )
        keys.forEach {
            val bqType = it.bqType
            it.keys.forEach {
                fields.add(
                    Field.newBuilder(
                        it,
                        bqType
                    ).setMode(Field.Mode.REQUIRED).build()
                )
            }
        }

        return Schema.of(fields)
    }

}