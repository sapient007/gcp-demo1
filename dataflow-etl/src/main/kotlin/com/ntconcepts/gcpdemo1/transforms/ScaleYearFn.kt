package com.ntconcepts.gcpdemo1.transforms

import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
import org.apache.beam.sdk.transforms.DoFn
import org.apache.beam.sdk.values.KV

class ScaleYearFn : DoFn<KV<TaxiRideL1, TaxiTripOutput>, KV<TaxiRideL1, TaxiTripOutput>>() {

    @ProcessElement
    fun apply(c: ProcessContext, @SideInput("maxYear") maxYear: Int?, @SideInput("minYear") minYear: Int?) {
        val trip = c.element().key
        val row = c.element().value.copy()
        if (maxYear != null && minYear != null) {
            row.year_norm = (row.year.toDouble() - minYear) / (maxYear - minYear).toDouble()
            //Because Kotlin no likey 0/0
            if (row.year_norm.isNaN()) {
                row.year_norm = 0.0
            }
//            else {
//                row.year_norm = round(row.year_norm * 10000) / 10000
//            }
        }
        c.output(KV.of(trip, row))
    }
}