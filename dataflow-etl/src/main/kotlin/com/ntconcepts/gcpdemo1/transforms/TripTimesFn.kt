package com.ntconcepts.gcpdemo1.transforms

import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
import org.apache.beam.sdk.transforms.DoFn
import org.apache.beam.sdk.values.KV
import org.apache.beam.sdk.values.PCollectionView
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter

class TripTimesFn(
    val daysOFWeekView: PCollectionView<List<String>>,
    val monthsView: PCollectionView<List<String>>
) :
    DoFn<KV<TaxiRideL1, TaxiTripOutput>, KV<TaxiRideL1, TaxiTripOutput>>() {

    @ProcessElement
    fun apply(c: ProcessContext) {

        val trip = c.element().key
        val row = c.element().value.copy()

        row.start_time_epoch = trip?.trip_start_timestamp as Long / 1000000

        row.daysOfWeekEncoded = row.daysOfWeekEncoded?.clone() as HashMap<String, Int>
        row.monthsEncoded = row.monthsEncoded?.clone() as HashMap<String, Int>

        val daysOfWeek = c.sideInput(daysOFWeekView)
        val months = c.sideInput(monthsView)

        val startTrip: LocalDateTime =
            LocalDateTime.ofEpochSecond(trip.trip_start_timestamp / 1000000, 0, ZoneOffset.UTC)
        val timestampFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")

        row.start_time = startTrip.format(timestampFormatter)

        //One-hot-encode day of the week
        val oheDayOfWeek = "day_of_week_${startTrip.dayOfWeek.name}"
        row.daysOfWeekEncoded?.put(oheDayOfWeek, 1)
        daysOfWeek.forEach {
            if (it != oheDayOfWeek) {
                row.daysOfWeekEncoded?.put(it, 0)
            }
        }
        //One-hot-encode month
        val ohemonth = "month_${startTrip.month.name}"
        row.daysOfWeekEncoded?.put(ohemonth, 1)
        months.forEach {
            if (it != ohemonth) {
                row.daysOfWeekEncoded?.put(it, 0)
            }
        }
        row.year = startTrip.year

        c.output(KV.of(trip, row))
    }


}