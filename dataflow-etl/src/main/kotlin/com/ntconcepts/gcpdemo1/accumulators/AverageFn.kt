package com.ntconcepts.gcpdemo1.accumulators

import org.apache.beam.sdk.transforms.Combine

class AverageFn : Combine.CombineFn<Double, StdAccum, Double>() {


    override fun createAccumulator(): StdAccum {
        return StdAccum()
    }

    override fun addInput(accum: StdAccum, input: Double): StdAccum {
        accum.sum += input
        accum.count++
        return accum
    }

    override fun mergeAccumulators(accums: Iterable<StdAccum>): StdAccum {
        var merged = createAccumulator()

        for (accum in accums) {
            merged.sum += accum.sum
            merged.count += accum.count
        }

        return merged
    }

    override fun extractOutput(accum: StdAccum): Double {
        return accum.sum / accum.count
    }


}