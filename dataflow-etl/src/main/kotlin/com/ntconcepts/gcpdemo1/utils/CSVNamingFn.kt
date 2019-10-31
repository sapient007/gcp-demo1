package com.ntconcepts.gcpdemo1.utils

import org.apache.beam.sdk.io.Compression
import org.apache.beam.sdk.io.FileIO
import org.apache.beam.sdk.transforms.windowing.BoundedWindow
import org.apache.beam.sdk.transforms.windowing.PaneInfo

class CSVNamingFn(private val partition: String) : FileIO.Write.FileNaming {

    override fun getFilename(
        window: BoundedWindow?,
        pane: PaneInfo?,
        numShards: Int,
        shardIndex: Int,
        compression: Compression?
    ): String {
//        val time = window?.maxTimestamp()?.toDateTime(DateTimeZone.UTC)
        return "${partition}/${shardIndex + 1}-of-${numShards}.csv${if (compression != null && compression.suggestedSuffix != "") ".${compression.suggestedSuffix}" else ""}"

    }

}