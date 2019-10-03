package com.ntconcepts.gcpdemo1.transforms

import com.google.api.services.bigquery.model.TableRow
import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import org.apache.beam.sdk.transforms.SimpleFunction
import org.apache.beam.sdk.values.KV

class CodeCashFn : SimpleFunction<KV<TaxiRideL1, TableRow>, KV<TaxiRideL1, TableRow>>() {
    override fun apply(wrapper: KV<TaxiRideL1, TableRow>): KV<TaxiRideL1, TableRow> {
        var row = wrapper.value.clone()
        if (wrapper.key?.payment_type == "Cash") {
            row.set("cash", 1)
        } else row.set("cash", 0)
        return KV.of(wrapper.key, row)
    }
}