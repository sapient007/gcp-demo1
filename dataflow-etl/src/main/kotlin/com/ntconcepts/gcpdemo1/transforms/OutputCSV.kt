package com.ntconcepts.gcpdemo1.transforms

import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
import org.apache.beam.sdk.transforms.SimpleFunction
import org.apache.beam.sdk.values.KV

class OutputCSV : SimpleFunction<KV<TaxiRideL1, TaxiTripOutput>, String>() {

    override fun apply(wrapper: KV<TaxiRideL1, TaxiTripOutput>): String {
        return wrapper.value.toCSV()
    }
}