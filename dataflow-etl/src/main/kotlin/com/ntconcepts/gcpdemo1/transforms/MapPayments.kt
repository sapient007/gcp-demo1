package com.ntconcepts.gcpdemo1.transforms

import com.google.api.services.bigquery.model.TableRow
import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import org.apache.beam.sdk.transforms.SimpleFunction
import org.apache.beam.sdk.values.KV

class MapPayments : SimpleFunction<KV<TaxiRideL1, TableRow>, KV<TaxiRideL1, TableRow>>() {
    override fun apply(wrapper: KV<TaxiRideL1, TableRow>): KV<TaxiRideL1, TableRow> {
        var row = wrapper.value.clone()
        val trip = wrapper.key
        if (trip?.payment_type == "Dispute" || trip?.payment_type == "Mobile") {
            row.set("payment_type", "Credit Card")
        }
        return KV.of(trip, row)
    }
}