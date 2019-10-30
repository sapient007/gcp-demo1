package com.ntconcepts.gcpdemo1.accumulators

import java.io.Serializable

class StdAccum : Serializable {

    var sum: Double = 0.0
    var count: Double = 0.0
    var sumSq: Double = 0.0

    override fun equals(other: Any?): Boolean {
        if (other == null) return false
//        if (other == this) return true
        if (other::class != StdAccum::class) return false

        val o = other as StdAccum

        if (this.sum != o.sum ||
            this.count != o.count ||
            this.sumSq != o.sumSq
        ) {
            return false
        }

        return true

    }

}