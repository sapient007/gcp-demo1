package com.ntconcepts.gcpdemo1.transforms

import com.google.api.services.bigquery.model.TableRow
import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
import org.apache.beam.sdk.transforms.SimpleFunction
import org.apache.beam.sdk.values.KV

class OutputTableRowsFn : SimpleFunction<KV<TaxiRideL1, TaxiTripOutput>, TableRow>() {
    override fun apply(wrapper: KV<TaxiRideL1, TaxiTripOutput>): TableRow {
        var row = wrapper.value

        var tableRow = TableRow()
            .set("cash", row.cash)
            .set("year", row.year)
            .set("start_time", row.start_time)
            .set("trip_miles", row.trip_miles)
            .set("company", row.company)
            .set("ml_partition", row.ml_partition)
            .set("distance_from_center", row.distance_from_center)
            .set("pickup_latitude", row.pickup_latitude)
            .set("pickup_longitude", row.pickup_longitude)
            .set("pickup_lat_centered", row.pickup_lat_centered)
            .set("pickup_long_centered", row.pickup_long_centered)
            .set("pickup_lat_norm", row.pickup_lat_norm)
            .set("pickup_long_norm", row.pickup_long_norm)
            .set("pickup_lat_std", row.pickup_lat_std)
            .set("pickup_long_std", row.pickup_long_std)

        row.companiesEncoded?.forEach {
            tableRow.set(it.key, it.value)
        }

        row.daysOfWeekEncoded?.forEach {
            tableRow.set(it.key, it.value)
        }

        row.monthsEncoded?.forEach {
            tableRow.set(it.key, it.value)
        }

        return tableRow
    }
}