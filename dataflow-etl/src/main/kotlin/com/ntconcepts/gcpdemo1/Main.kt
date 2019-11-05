package com.ntconcepts.gcpdemo1

import com.google.api.services.bigquery.model.TableRow
import com.ntconcepts.gcpdemo1.accumulators.StdFn
import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
import com.ntconcepts.gcpdemo1.transforms.*
import com.ntconcepts.gcpdemo1.utils.CSVNamingFn
import org.apache.avro.generic.GenericRecord
import org.apache.beam.sdk.Pipeline
import org.apache.beam.sdk.coders.*
import org.apache.beam.sdk.io.AvroIO
import org.apache.beam.sdk.io.FileIO
import org.apache.beam.sdk.io.TextIO
import org.apache.beam.sdk.io.gcp.bigquery.BigQueryIO
import org.apache.beam.sdk.io.gcp.bigquery.SchemaAndRecord
import org.apache.beam.sdk.options.PipelineOptionsFactory
import org.apache.beam.sdk.options.ValueProvider
import org.apache.beam.sdk.transforms.*
import org.apache.beam.sdk.values.*


const val daysOfWeekPrefix = "day_of_week_"
const val companyPrefix = "company_"

fun main(args: Array<String>) {
    val options = getOptions(args)
    val p = getPipeline(options)
    p.run()
}

fun getOptions(args: Array<String>): Demo1Options {
    return PipelineOptionsFactory.fromArgs(*args).withValidation()
        .`as`(Demo1Options::class.java)
}

val daysOfWeekList = listOf(
    "${daysOfWeekPrefix}MONDAY",
    "${daysOfWeekPrefix}TUESDAY",
    "${daysOfWeekPrefix}WEDNESDAY",
    "${daysOfWeekPrefix}THURSDAY",
    "${daysOfWeekPrefix}FRIDAY",
    "${daysOfWeekPrefix}SATURDAY",
    "${daysOfWeekPrefix}SUNDAY"
)

fun getDaysOfWeekView(p: Pipeline): PCollectionView<List<String>> {
    val days = daysOfWeekList
    return p.apply("dayOfTheWeek PCollection", Create.of(days)).setCoder(StringUtf8Coder.of())
        .apply("dayOfTheWeek View", View.asList())
}

val monthsList = listOf(
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

fun getMonthView(p: Pipeline): PCollectionView<List<String>> {
    return p.apply("months PCollection", Create.of(monthsList)).setCoder(StringUtf8Coder.of())
        .apply("months View", View.asList())
}

fun getCompaniesView(p: PCollection<String>): PCollectionView<List<String>> {

    return p.apply(
        "companies Distinct",
        Distinct.create<String>()
    )
        .apply(
            "Map prefix to company",
            MapElements.into(TypeDescriptors.strings()).via(SerializableFunction<String, String> {
                "${companyPrefix}${it}"
            })
        )
        .apply("companies View", View.asList<String>())
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
            "Get Chicago taxi rides",
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
                .withoutValidation()
                .from(options.inputTableSpec)
//                .fromQuery("SELECT * FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips` where pickup_latitude is not null LIMIT 10000")
//                .usingStandardSql()
        )
            .apply(
                "Filter rows",
                ParDo.of(FilterRowsFn(companies, trips, options.hotEncodeCompany)).withOutputTags(
                    trips,
                    TupleTagList.of(companies)
                )
            )

    val tripsPCollection: PCollection<TaxiRideL1> =
        results.get(trips).setCoder(SerializableCoder.of(TaxiRideL1::class.java))

    val companiesPCollection: PCollection<String> = results.get(companies).setCoder(StringUtf8Coder.of())
    val companiesView = getCompaniesView(companiesPCollection)

    val kvDescriptor =
        TypeDescriptors.kvs(TypeDescriptor.of(TaxiRideL1::class.java), TypeDescriptor.of(TaxiTripOutput::class.java))

    val tripsWithCenteredCoords = TupleTag<KV<TaxiRideL1, TaxiTripOutput>>()

    val centeredResults = tripsPCollection
        .apply(
        "Map to KVs",
        MapElements.into(
            kvDescriptor
        ).via(ConvertToKVFn())
        )
        .apply(
            "Center lat/longs",
            ParDo.of(
                CenteredLatLongFn(
                    options.mapCenterLat,
                    options.mapCenterLong,
                    tripsWithCenteredCoords,
                    startLats,
                    startLongs
                )
            )
                .withOutputTags(tripsWithCenteredCoords, TupleTagList.of(startLats).and(startLongs))
        )

    val tripsWithCenteredCoordsPCollection: PCollection<KV<TaxiRideL1, TaxiTripOutput>> =
        centeredResults.get(tripsWithCenteredCoords)
            .setCoder(
                KvCoder.of(
                    SerializableCoder.of(TaxiRideL1::class.java),
                    SerializableCoder.of(TaxiTripOutput::class.java)
                )
            )

    val startLatsPCollection: PCollection<Double> = centeredResults.get(startLats).setCoder(DoubleCoder.of())
    val startLongsPCollection: PCollection<Double> = centeredResults.get(startLongs).setCoder(DoubleCoder.of())

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


    val years = TupleTag<Int>()
    val tripsWithTimesTT = TupleTag<KV<TaxiRideL1, TaxiTripOutput>>()

    val tripsWithTimeResults = tripsWithCenteredCoordsPCollection
        .apply(
            "Create trip time fields",
            ParDo.of(TripTimesFn(dayOfWeekView, monthView, years))
                .withSideInputs(dayOfWeekView, monthView)
                .withOutputTags(tripsWithTimesTT, TupleTagList.of(years))
        )


    val yearsPCollection: PCollection<Int> = tripsWithTimeResults.get(years).setCoder(VarIntCoder.of())
    val maxYearView: PCollectionView<Int> =
        yearsPCollection.apply("maxYear", Combine.globally(Max.ofIntegers()).asSingletonView())
    val minYearView: PCollectionView<Int> =
        yearsPCollection.apply("minYear", Combine.globally(Min.ofIntegers()).asSingletonView())

    val tripOutputs = tripsWithTimeResults.get(tripsWithTimesTT).apply(
        "Map cash payments",
        MapElements.into(
            kvDescriptor
        ).via(CodeCashFn())
    )
        .apply(
            "Map trip miles",
            MapElements.into(
                kvDescriptor
            ).via(TripMilesFn())
        )
        .apply(
            "Make ML partitions",
            ParDo.of(
                SetMLPartitionsFn(
                    options.mlPartitionTrainWeight,
                    options.mlPartitionTestWeight,
                    options.mlPartitionValidationWeight
                )
            )
        )
        .apply(
            "Encode company",
            ParDo.of(EncodeCompanyFn(options.hotEncodeCompany, companiesView, companyPrefix)).withSideInputs(
                companiesView
            )
        )
        .apply(
            "Map pickup latlong",
            ParDo.of(
                TransformLatLongFn(
                    maxPickupLat,
                    minPickupLat,
                    maxPickupLong,
                    minPickupLong,
                    stdPickupLat,
                    stdPickupLong,
                    meanPickupLat,
                    meanPickupLong,
                    options.mapCenterLat,
                    options.mapCenterLong
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
            "NormalizeYear",
            ParDo.of(ScaleYearFn()).withSideInputs(
                mapOf(Pair("maxYear", maxYearView), Pair("minYear", minYearView))
            )
        )
        .apply(
            "Sample data",
            ParDo.of(SampleDataFn(options.sampleSize))
        )
    writeBQ(options, p, tripOutputs, dayOfWeekView, monthView, companiesView)
//    writeAvro(options, tripOutputs)
//    writeCSV(options, p, tripOutputs, dayOfWeekView, monthView, companiesView)

    return p
}

fun writeBQ(
    options: Demo1Options,
    p: Pipeline,
    e: PCollection<KV<TaxiRideL1, TaxiTripOutput>>,
    dayOfWeekView: PCollectionView<List<String>>,
    monthView: PCollectionView<List<String>>,
    companiesView: PCollectionView<List<String>>
) {

    p.apply(
        "Create table",
        BQCreateTable(
            options.outputDataset,
            options.outputTable,
            options.dropTable,
            dayOfWeekView,
            monthView,
            companiesView,
            options.hotEncodeCompany
        )
    )

    e.apply(
        "Map to TableRows ", MapElements.into(
            TypeDescriptor.of(TableRow::class.java)
        )
            .via(OutputTableRowsFn())
    )
        .apply(
            "Write Bigquery",
            BigQueryIO.writeTableRows()
                .to(options.outputTableSpec)
                .withCreateDisposition(BigQueryIO.Write.CreateDisposition.CREATE_NEVER)
                .withWriteDisposition(BigQueryIO.Write.WriteDisposition.WRITE_TRUNCATE)
        )
}

fun writeCSVHeader(
    p: Pipeline,
    headerOutputPath: ValueProvider<String>,
    dayOfWeekView: PCollectionView<List<String>>,
    monthView: PCollectionView<List<String>>,
    companiesView: PCollectionView<List<String>>
) {
    p.apply("Make CSV header", Create.of(TaxiTripOutput())).setCoder(SerializableCoder.of(TaxiTripOutput::class.java))
        .apply(
            "Add encoded times", ParDo.of(
                InputsForEmptyOutputFn(dayOfWeekView, monthView, companiesView)
            ).withSideInputs(dayOfWeekView, monthView, companiesView)
        )
        .apply(
            FileIO.write<TaxiTripOutput>()
                .via(Contextful.fn(
                    SerializableFunction {
                        it.toCSVHeader()
                    }
                ), TextIO.sink())
                .to(headerOutputPath)
                .withSuffix(".csv")
                .withNumShards(1)
        )

}

fun writeCSV(
    options: Demo1Options,
    p: Pipeline,
    kvs: PCollection<KV<TaxiRideL1, TaxiTripOutput>>,
    dayOfWeekView: PCollectionView<List<String>>,
    monthView: PCollectionView<List<String>>,
    companiesView: PCollectionView<List<String>>
) {

    writeCSVHeader(p, options.csvHeaderOutputPath, dayOfWeekView, monthView, companiesView)

    kvs.apply(
        "Map to TaxiTripOutput",
        MapElements.into(TypeDescriptor.of(TaxiTripOutput::class.java))
            .via(SerializableFunction<KV<TaxiRideL1, TaxiTripOutput>, TaxiTripOutput> {
                it.value
            })
    )
        .apply(
            "Write CSV",
            FileIO.writeDynamic<String, TaxiTripOutput>()
                .by(SerializableFunction {
                    it.ml_partition
                })
                .via(Contextful.fn(
                    SerializableFunction {
                        it.toCSV()
                    }
                ), TextIO.sink())
                .to(options.csvOutputPath)
                .withDestinationCoder(StringUtf8Coder.of())
                .withNumShards(options.csvShards)
                .withNaming(
                    Contextful.fn(
                        SerializableFunction {
                            CSVNamingFn(it)
                        })
                )
        )
}

fun writeAvro(options: Demo1Options, p: PCollection<KV<TaxiRideL1, TaxiTripOutput>>) {
    p.apply(
        "Map to GenericRecord",
        MapElements.into(
            TypeDescriptor.of(GenericRecord::class.java)
        ).via(OutputTaxiTripOutputFn())
    )
        .setCoder(AvroCoder.of(TaxiTripOutput.AvroSchemaGetter.schema(daysOfWeekList, monthsList)))
        .apply(
            "Write Avro",
            AvroIO.writeGenericRecords(TaxiTripOutput.AvroSchemaGetter.schema(daysOfWeekList, monthsList))
                .to(options.avroOutputPath)
                .withSuffix(".avro")
        )
}