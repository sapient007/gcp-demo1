package com.ntconcepts.gcpdemo1.transforms

import com.google.api.services.bigquery.model.TableRow
import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import org.apache.beam.sdk.transforms.SimpleFunction
import org.apache.beam.sdk.values.KV

class TripMilesFn : SimpleFunction<KV<TaxiRideL1, TableRow>, KV<TaxiRideL1, TableRow>>() {
    override fun apply(wrapper: KV<TaxiRideL1, TableRow>): KV<TaxiRideL1, TableRow> {
        var row = wrapper.value.clone()
        row.set("trip_miles", wrapper.key?.trip_miles)
        return KV.of(wrapper.key, row)
    }
}