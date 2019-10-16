package com.ntconcepts.gcpdemo1.transforms

import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
import org.apache.beam.sdk.options.ValueProvider
import org.apache.beam.sdk.transforms.DoFn
import org.apache.beam.sdk.values.KV
import kotlin.random.Random

class SampleDataFn(
    private val sampleSize: ValueProvider<Int>
) :
    DoFn<KV<TaxiRideL1, TaxiTripOutput>, KV<TaxiRideL1, TaxiTripOutput>>() {

//    private lateinit var random: Random
//
//    @StartBundle
//    fun setup() {
//        random = Random(7131357)
//    }

    @ProcessElement
    fun apply(c: ProcessContext) {
        if (Random.nextInt(0, 100) < sampleSize.get()) {
            c.output(KV.of(c.element().key, c.element().value))
        }
    }

}