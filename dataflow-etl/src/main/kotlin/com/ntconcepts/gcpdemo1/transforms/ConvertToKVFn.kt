package com.ntconcepts.gcpdemo1.transforms

import com.google.api.services.bigquery.model.TableRow
import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import org.apache.beam.sdk.transforms.SimpleFunction
import org.apache.beam.sdk.values.KV

class ConvertToKVFn : SimpleFunction<TaxiRideL1, KV<TaxiRideL1, TableRow>>() {
    override fun apply(trip: TaxiRideL1): KV<TaxiRideL1, TableRow> {
        return KV.of(trip, TableRow())
    }
}