package com.ntconcepts.gcpdemo1.transforms

import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
import org.apache.beam.sdk.transforms.SimpleFunction
import org.apache.beam.sdk.values.KV

class ConvertToKVFn : SimpleFunction<TaxiRideL1, KV<TaxiRideL1, TaxiTripOutput>>() {
    override fun apply(trip: TaxiRideL1): KV<TaxiRideL1, TaxiTripOutput> {
        return KV.of(trip, TaxiTripOutput())
    }
}