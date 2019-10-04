package com.ntconcepts.gcpdemo1

import com.google.api.services.bigquery.model.TableFieldSchema
import com.google.api.services.bigquery.model.TableRow
import com.google.api.services.bigquery.model.TableSchema
import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.transforms.*
import org.apache.beam.sdk.Pipeline
import org.apache.beam.sdk.coders.DoubleCoder
import org.apache.beam.sdk.coders.SerializableCoder
import org.apache.beam.sdk.coders.StringUtf8Coder
import org.apache.beam.sdk.io.gcp.bigquery.BigQueryIO
import org.apache.beam.sdk.io.gcp.bigquery.SchemaAndRecord
import org.apache.beam.sdk.options.PipelineOptionsFactory
import org.apache.beam.sdk.transforms.*
import org.apache.beam.sdk.values.*
import org.slf4j.LoggerFactory

const val daysOfWeekPrefix = "day_of_week_"

fun main(args: Array<String>) {
    val LOG = LoggerFactory.getLogger("com.ntconcepts.gcp-demo1")
    val options = getOptions(args)
    val p = getPipeline(options)
    p.run()
}

fun getOptions(args: Array<String>): Demo1Options {
    return PipelineOptionsFactory.fromArgs(*args).withValidation()
        .`as`(Demo1Options::class.java)
}



fun getDaysOfWeekList(): List<String> {
    return listOf(
        "${daysOfWeekPrefix}MONDAY",
        "${daysOfWeekPrefix}TUESDAY",
        "${daysOfWeekPrefix}WEDNESDAY",
        "${daysOfWeekPrefix}THURSDAY",
        "${daysOfWeekPrefix}FRIDAY",
        "${daysOfWeekPrefix}SATURDAY",
        "${daysOfWeekPrefix}SUNDAY"
    )
}

fun getDaysOfWeekView(p: Pipeline): PCollectionView<List<String>> {
    val days = getDaysOfWeekList()
    return p.apply("Get one-hot-encoded day of the week keys", Create.of(days)).setCoder(StringUtf8Coder.of())
        .apply("Make one-hot week view", View.asList())
}

fun getMonthView(p: Pipeline): PCollectionView<List<String>> {
    val months = listOf(
        "month_JANUARY",
        "month_FEBRUARY",
        "month_MARCH",
        "month_APRIL",
        "month_MAY",
        "month_JUNE",
        "month_JULY",
        "month_AUGUST",
        "month_SEPTEMBER",
        "month_OCTOBER",
        "month_NOVEMBER",
        "month_DECEMBER"
    )
    return p.apply("Get one-hot-encoded month keys", Create.of(months)).setCoder(StringUtf8Coder.of())
        .apply("Make one-hot month view",View.asList())
}

fun getPipeline(options: Demo1Options): Pipeline {
    val p = Pipeline.create(options)

    val startLats = TupleTag<Double>()
    val startLongs = TupleTag<Double>()
    val trips = TupleTag<TaxiRideL1>()

    val dayOfWeekView = getDaysOfWeekView(p)
    val monthView = getMonthView(p)

    p.apply("Create table",
        BQCreateTable(options.dataset, options.table, options.dropTable, dayOfWeekView, monthView))

    val results: PCollectionTuple =
        p.apply(
            "Get raw data from Chicago taxi rides dataset",
            BigQueryIO.read(SerializableFunction { r: SchemaAndRecord ->
                TaxiRideL1(
                    "",
                    "",
                    if (r.record.get("trip_start_timestamp") != null) r.record.get("trip_start_timestamp") as Long else 0L,
                    0,
                    if (r.record.get("trip_seconds") != null) r.record.get("trip_seconds") as Long else 0L,
                    if (r.record.get("trip_miles") != null) r.record.get("trip_miles") as Double else 0.0,
                    0,
                    0,
                    0,
                    0,
                    if (r.record.get("fare") != null) r.record.get("fare") as Double else 0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    if (r.record.get("payment_type") != null) r.record.get("payment_type").toString() else "",
                    "",
                    if (r.record.get("pickup_latitude") != null) r.record.get("pickup_latitude") as Double else 0.0,
                    if (r.record.get("pickup_longitude") != null) r.record.get("pickup_longitude") as Double else 0.0,
                    "",
                    0.0,
                    0.0,
                    ""
                )
            }
            )
//        .from("bigquery-public-data:chicago_taxi_trips.taxi_trips")
                .fromQuery("SELECT * FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips` LIMIT 100000")
                .usingStandardSql()
        )
            .apply(
                "Filter rows",
                ParDo.of(FilterRowsFn(startLats, startLongs, trips)).withOutputTags(
                    trips,
                    TupleTagList.of(startLats).and(startLongs)
                )
            )


    val tripsPCollection: PCollection<TaxiRideL1> =
        results.get(trips).setCoder(SerializableCoder.of(TaxiRideL1::class.java))
    val startLatsPCollection: PCollection<Double> = results.get(startLats).setCoder(DoubleCoder.of())
    val startLongsPCollection: PCollection<Double> = results.get(startLongs).setCoder(DoubleCoder.of())

    val maxPickupLat: PCollectionView<Double> =
        startLatsPCollection.apply("maxPickupLat", Combine.globally(Max.ofDoubles()).asSingletonView())
    val minPickupLat: PCollectionView<Double> =
        startLatsPCollection.apply("minPickupLat", Combine.globally(Min.ofDoubles()).asSingletonView())
    val maxPickupLong: PCollectionView<Double> =
        startLongsPCollection.apply("maxPickupLong", Combine.globally(Max.ofDoubles()).asSingletonView())
    val minPickupLong: PCollectionView<Double> =
        startLongsPCollection.apply("minPickupLong", Combine.globally(Min.ofDoubles()).asSingletonView())

    tripsPCollection.apply(
        "Convert to KVs",
        MapElements.into(
            TypeDescriptors.kvs(TypeDescriptor.of(TaxiRideL1::class.java), TypeDescriptor.of(TableRow::class.java))
        ).via(ConvertToKVFn())
    )
        .apply(
            "Code cash payments",
            MapElements.into(
                TypeDescriptors.kvs(TypeDescriptor.of(TaxiRideL1::class.java), TypeDescriptor.of(TableRow::class.java))
            ).via(CodeCashFn())
        )
        .apply(
            "Create trip time fields",
            ParDo.of(TripTimesFn(dayOfWeekView, monthView, daysOfWeekPrefix))
                .withSideInputs(dayOfWeekView, monthView)
        )
        .apply(
            "Process pickup latlong fields",
            ParDo.of(TransformLatLongFn(maxPickupLat)).withSideInputs(
                maxPickupLat,
                minPickupLat,
                maxPickupLong,
                minPickupLong
            )
        )
        .apply(
            "Output to TableRows for writing", MapElements.into(
                TypeDescriptor.of(TableRow::class.java)
            )
                .via(OutputTableRowsFn())
        )
        .apply(
            "Load transformed rides",
            BigQueryIO.writeTableRows()
                .to("chicagotaxi.finaltaxi_encoded_el_test")
//                .withSchema(getTransformSchema(OneHotSchemaWrapper(getDaysOfWeekList(), "INTEGER")))
                .withCreateDisposition(BigQueryIO.Write.CreateDisposition.CREATE_NEVER)
                .withWriteDisposition(BigQueryIO.Write.WriteDisposition.WRITE_TRUNCATE)
        )




    return p
}