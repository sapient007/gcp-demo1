package com.ntconcepts.gcpdemo1

import com.google.api.services.bigquery.model.TableRow
import com.ntconcepts.gcpdemo1.accumulators.StdFn
import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
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

const val daysOfWeekPrefix = "day_of_week_"
const val companyPrefix = "company_"

fun main(args: Array<String>) {
//    val LOG = LoggerFactory.getLogger("com.ntconcepts.gcp-demo1")
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
        .apply("Make one-hot month view", View.asList())
}

fun getCompaniesView(p: PCollection<String>): PCollectionView<List<String>> {
    return p.apply(
        "companies",
        Distinct.create<String>()
    )
        .apply(MapElements.into(TypeDescriptors.strings()).via(SerializableFunction<String, String> {
            "${companyPrefix}${it}"
        }))
        .apply(View.asList<String>())
}


fun getPipeline(options: Demo1Options): Pipeline {
    val p = Pipeline.create(options)

    val companies = TupleTag<String>()
    val startLats = TupleTag<Double>()
    val startLongs = TupleTag<Double>()
    val trips = TupleTag<TaxiRideL1>()

    val dayOfWeekView = getDaysOfWeekView(p)
    val monthView = getMonthView(p)

    val results: PCollectionTuple =
        p.apply(
            "Get raw data from Chicago taxi rides dataset",
            BigQueryIO.read(SerializableFunction { r: SchemaAndRecord ->
                TaxiRideL1(
                    if (r.record.get("unique_key") != null) r.record.get("unique_key").toString() else "",
                    if (r.record.get("taxi_id") != null) r.record.get("taxi_id").toString() else "",
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
                    if (r.record.get("company") != null) r.record.get("company").toString() else "",
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
                .fromQuery("SELECT * FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips` where pickup_latitude is not null LIMIT 1000")
                .usingStandardSql()
        )
            .apply(
                "Filter rows",
                ParDo.of(FilterRowsFn(companies, startLats, startLongs, trips)).withOutputTags(
                    trips,
                    TupleTagList.of(startLats).and(startLongs).and(companies)
                )
            )


    val tripsPCollection: PCollection<TaxiRideL1> =
        results.get(trips).setCoder(SerializableCoder.of(TaxiRideL1::class.java))

    val companiesPCollection: PCollection<String> = results.get(companies).setCoder(StringUtf8Coder.of())
    val companiesView = getCompaniesView(companiesPCollection)

    p.apply(
        "Create table",
        BQCreateTable(
            options.dataset,
            options.table,
            options.dropTable,
            dayOfWeekView,
            monthView,
            companiesView,
            companyPrefix
        )
    )

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

    val stdPickupLat: PCollectionView<Double> =
        startLatsPCollection.apply("stdPickupLat", Combine.globally(StdFn()).asSingletonView())
    val stdPickupLong: PCollectionView<Double> =
        startLongsPCollection.apply("stdPickupLong", Combine.globally(StdFn()).asSingletonView())

    val meanPickupLat: PCollectionView<Double> =
        startLatsPCollection.apply("meanPickupLat", Mean.globally<Double>().asSingletonView())
    val meanPickupLong: PCollectionView<Double> =
        startLongsPCollection.apply("meanPickupLong", Mean.globally<Double>().asSingletonView())

    val kvDescriptor = TypeDescriptors.kvs(TypeDescriptor.of(TaxiRideL1::class.java), TypeDescriptor.of(TaxiTripOutput::class.java))



    tripsPCollection.apply(
        "Convert to KVs",
        MapElements.into(
            kvDescriptor
        ).via(ConvertToKVFn())
    )
        .apply(
            "Code cash payments",
            MapElements.into(
                kvDescriptor
            ).via(CodeCashFn())
        )
        .apply(
            "Trip miles",
            MapElements.into(
                kvDescriptor
            ).via(TripMilesFn())
        )
        .apply(
            "Apply ML partitions",
            ParDo.of(SetMLPartitionsFn(options.partitionWeights))
        )
        .apply(
            "Create trip time fields",
            ParDo.of(TripTimesFn(dayOfWeekView, monthView))
                .withSideInputs(dayOfWeekView, monthView)
        )
        .apply(
            "Encode company",
            ParDo.of(EncodeCompanyFn(companiesView, companyPrefix)).withSideInputs(companiesView)
        )
        .apply(
            "Process pickup latlong fields",
            ParDo.of(
                TransformLatLongFn(
                    maxPickupLat,
                    minPickupLat,
                    maxPickupLong,
                    minPickupLong,
                    stdPickupLat,
                    stdPickupLong,
                    meanPickupLat,
                    meanPickupLong
                )
            ).withSideInputs(
                maxPickupLat,
                minPickupLat,
                maxPickupLong,
                minPickupLong,
                stdPickupLat,
                stdPickupLong,
                meanPickupLat,
                meanPickupLong
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
//                .withTimePartitioning(TimePartitioning().setField("start_time"))
//                .withClustering(Clustering().setFields(listOf("ml_partition")))
        )




    return p
}