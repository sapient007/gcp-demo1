package com.ntconcepts.gcpdemo1.transforms

import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
import org.apache.beam.sdk.transforms.SimpleFunction
import org.apache.beam.sdk.values.KV

class TripMilesFn : SimpleFunction<KV<TaxiRideL1, TaxiTripOutput>, KV<TaxiRideL1, TaxiTripOutput>>() {
    override fun apply(wrapper: KV<TaxiRideL1, TaxiTripOutput>): KV<TaxiRideL1, TaxiTripOutput> {
        var row = wrapper.value.copy()
        row.trip_miles = wrapper.key?.trip_miles
        return KV.of(wrapper.key, row)
    }
}