package com.ntconcepts.gcpdemo1.transforms

import com.google.api.services.bigquery.model.TableRow
import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import org.apache.beam.sdk.transforms.DoFn
import org.apache.beam.sdk.transforms.SimpleFunction
import org.apache.beam.sdk.values.KV
import org.apache.beam.sdk.values.PCollectionView
import java.time.LocalDateTime
import java.time.ZoneOffset

class TripTimesFn(val daysOFWeekView: PCollectionView<List<String>>, val monthsView: PCollectionView<List<String>>, val daysOfWeekPrefix: String) :
    DoFn<KV<TaxiRideL1, TableRow>, KV<TaxiRideL1, TableRow>>() {

    @ProcessElement
    fun apply(c: ProcessContext) {
        val trip = c.element().key
        val row = c.element().value.clone()

        val daysOfWeek = c.sideInput(daysOFWeekView)
        val months = c.sideInput(monthsView)

        val startTrip: LocalDateTime =
            LocalDateTime.ofEpochSecond(trip?.trip_start_timestamp as Long, 0, ZoneOffset.UTC)

        row.set(
            "start_time", trip.trip_start_timestamp
        )

        //One-hot-encode day of the week
        val oheDayOfWeek = "day_of_week_${startTrip.dayOfWeek.name}"
        row.set(oheDayOfWeek, 1)
        daysOfWeek.forEach {
            if(it != oheDayOfWeek) {
                row.set(it, 0)
            }
        }
        //One-hot-encode month
        val ohemonth = "month_${startTrip.month.name}"
        row.set(ohemonth, 1)
        months.forEach {
            if(it != ohemonth) {
                row.set(it, 0)
            }
        }
        row.set("year", startTrip.year)

        c.output(KV.of(trip, row))
    }


}