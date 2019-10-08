package com.ntconcepts.gcpdemo1.transforms

import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
import org.apache.beam.sdk.transforms.SimpleFunction
import org.apache.beam.sdk.values.KV

class CodeCashFn : SimpleFunction<KV<TaxiRideL1, TaxiTripOutput>, KV<TaxiRideL1, TaxiTripOutput>>() {
    override fun apply(wrapper: KV<TaxiRideL1, TaxiTripOutput>): KV<TaxiRideL1, TaxiTripOutput> {
        var row = wrapper.value.copy()

        if (wrapper.key?.payment_type == "Cash") {
            row.cash = 1
        } else row.cash = 0
        return KV.of(wrapper.key, row)
    }
}