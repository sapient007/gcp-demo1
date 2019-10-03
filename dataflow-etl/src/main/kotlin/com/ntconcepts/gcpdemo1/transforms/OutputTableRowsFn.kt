package com.ntconcepts.gcpdemo1.transforms

import com.google.api.services.bigquery.model.TableRow
import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import org.apache.beam.sdk.transforms.SimpleFunction
import org.apache.beam.sdk.values.KV

class OutputTableRowsFn : SimpleFunction<KV<TaxiRideL1, TableRow>, TableRow>() {
    override fun apply(wrapper: KV<TaxiRideL1, TableRow>): TableRow {
        return wrapper.value
    }
}