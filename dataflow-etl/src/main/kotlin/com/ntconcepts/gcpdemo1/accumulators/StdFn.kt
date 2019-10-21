package com.ntconcepts.gcpdemo1.accumulators

import org.apache.beam.sdk.transforms.Combine
import kotlin.math.pow
import kotlin.math.sqrt

class StdFn : Combine.CombineFn<Double, StdAccum, Double>() {


    override fun createAccumulator(): StdAccum {
        return StdAccum()
    }

    override fun addInput(accum: StdAccum, input: Double): StdAccum {
        accum.sum += input
        accum.sumSq += input.pow(2)
        accum.count++
        return accum
    }

    override fun mergeAccumulators(accums: Iterable<StdAccum>): StdAccum {
        var merged = createAccumulator()

        for (accum in accums) {
            merged.sum += accum.sum
            merged.sumSq += accum.sumSq
            merged.count += accum.count
        }

        return merged
    }

    override fun extractOutput(accum: StdAccum): Double {
        val mean = accum.sum / accum.count
        val variance = (accum.sumSq / accum.count) - mean.pow(2)
//        val variance = ((accum.sumSq - accum.sum.pow(2) ) / accum.count ) / (accum.count - 2)
        return sqrt(variance)
    }
}