package com.ntconcepts.gcpdemo1.utils

import java.io.Serializable
import java.util.*

//From https://stackoverflow.com/questions/6409652/random-weighted-selection-in-java
class RandomCollection<T>() : Serializable {
    private val map: NavigableMap<Double, T> = TreeMap<Double, T>()
    private var random: Random
    private var total: Double = 0.0

    init {
        random = Random()
    }

    constructor(r: Random) : this() {
        random = r
    }

    fun add(weight: Double, result: T): RandomCollection<T> {
        if (weight <= 0) return this
        total += weight
        map.put(total, result)
        return this
    }

    fun next(): T {
        val value: Double = random.nextDouble() * total
        return map.higherEntry(value).value
    }

    fun size(): Int {
        return map.size
    }

}