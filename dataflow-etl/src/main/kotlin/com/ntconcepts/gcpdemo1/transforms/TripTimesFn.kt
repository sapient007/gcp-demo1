package com.ntconcepts.gcpdemo1.transforms

import com.google.api.services.bigquery.model.TableRow
import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import org.apache.beam.sdk.transforms.SimpleFunction
import org.apache.beam.sdk.values.KV
import java.time.LocalDateTime
import java.time.ZoneOffset

class TripTimesFn : SimpleFunction<KV<TaxiRideL1, TableRow>, KV<TaxiRideL1, TableRow>>() {
    override fun apply(wrapper: KV<TaxiRideL1, TableRow>): KV<TaxiRideL1, TableRow> {
        var row = wrapper.value.clone()
        val trip = wrapper.key

        val startTrip: LocalDateTime =
            LocalDateTime.ofEpochSecond(trip?.trip_start_timestamp as Long, 0, ZoneOffset.UTC)

        row.set(
            "start_time", trip.trip_start_timestamp
        )

        row.set("day_of_week_$startTrip.dayOfWeek.name", 1)
        row.set("month_$startTrip.month.name", 1)
        row.set("year", startTrip.year)

        return KV.of(wrapper.key, row)
    }
}